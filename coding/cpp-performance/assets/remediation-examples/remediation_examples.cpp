// Original C++20 correctness fixtures, not performance benchmark results.
// Compile commands and contracts are in README.md beside this file.
#include <algorithm>
#include <atomic>
#include <condition_variable>
#include <cstddef>
#include <cstdint>
#include <deque>
#include <exception>
#include <iostream>
#include <mutex>
#include <stdexcept>
#include <thread>
#include <utility>
#include <vector>

void require(bool condition, const char* message) {
  if (!condition) throw std::runtime_error(message);
}

std::pair<std::size_t, std::size_t> partition(std::size_t size,
                                            std::size_t workers,
                                            std::size_t index) {
  const auto quotient = size / workers;
  const auto remainder = size % workers;
  const auto begin = index * quotient + std::min(index, remainder);
  return {begin, begin + quotient + (index < remainder ? 1U : 0U)};
}

// BEFORE: one contended atomic location. Relaxed is valid ONLY for this independent
// tally; no other data is published through it. Joining establishes completion.
std::size_t shared_tally(const std::vector<int>& values, std::size_t requested) {
  if (values.empty()) return 0;
  const auto workers = std::min(values.size(), std::max(std::size_t{1}, requested));
  std::atomic<std::size_t> total{0};
  std::vector<std::jthread> threads;
  threads.reserve(workers);
  for (std::size_t i = 0; i < workers; ++i) {
    const auto [begin, end] = partition(values.size(), workers, i);
    threads.emplace_back([&, begin, end] {
      for (auto j = begin; j < end; ++j) {
        if (values[j] > 0) total.fetch_add(1, std::memory_order_relaxed);
      }
    });
  }
  threads.clear();  // jthread destruction joins; workers do not use stop tokens.
  return total.load(std::memory_order_relaxed);
}

// AFTER: accumulation stays in a local variable. Each worker publishes once into
// pre-sized stable storage; readers access it only after every worker is joined.
std::size_t local_tally(const std::vector<int>& values, std::size_t requested) {
  if (values.empty()) return 0;
  const auto workers = std::min(values.size(), std::max(std::size_t{1}, requested));
  std::vector<std::size_t> partial(workers, 0);
  std::vector<std::jthread> threads;
  threads.reserve(workers);
  for (std::size_t i = 0; i < workers; ++i) {
    const auto [begin, end] = partition(values.size(), workers, i);
    threads.emplace_back([&, begin, end, i] {
      std::size_t local = 0;
      for (auto j = begin; j < end; ++j) local += values[j] > 0 ? 1U : 0U;
      partial[i] = local;
    });
  }
  threads.clear();
  std::size_t total = 0;
  for (const auto value : partial) total += value;
  return total;
}

// Same bounded integer sum, different access order for a row-major buffer.
std::int64_t column_first(const std::vector<int>& matrix, std::size_t rows,
                          std::size_t columns) {
  std::int64_t result = 0;
  for (std::size_t column = 0; column < columns; ++column)
    for (std::size_t row = 0; row < rows; ++row)
      result += matrix[row * columns + column];
  return result;
}
std::int64_t row_first(const std::vector<int>& matrix, std::size_t rows,
                       std::size_t columns) {
  std::int64_t result = 0;
  for (std::size_t row = 0; row < rows; ++row)
    for (std::size_t column = 0; column < columns; ++column)
      result += matrix[row * columns + column];
  return result;
}

// Concrete close-and-drain bounded queue. Not a generic executor: int values have
// nonthrowing move/copy; real job ownership/exception contracts need explicit work.
class BoundedQueue {
 public:
  explicit BoundedQueue(std::size_t capacity) : capacity_(capacity) {
    if (capacity == 0) throw std::invalid_argument("capacity must be positive");
  }
  bool push(int value) {
    std::unique_lock lock(mutex_);
    not_full_.wait(lock, [&] { return closed_ || values_.size() < capacity_; });
    if (closed_) return false;
    values_.push_back(value);
    peak_ = std::max(peak_, values_.size());
    lock.unlock();
    not_empty_.notify_one();
    return true;
  }
  bool pop(int& result) {
    std::unique_lock lock(mutex_);
    not_empty_.wait(lock, [&] { return closed_ || !values_.empty(); });
    if (values_.empty()) return false;  // closed and drained
    result = values_.front();
    values_.pop_front();
    lock.unlock();
    not_full_.notify_one();
    return true;
  }
  void close() {
    {
      std::lock_guard lock(mutex_);
      closed_ = true;
    }
    not_empty_.notify_all();
    not_full_.notify_all();
  }
  std::size_t peak_size() const {
    std::lock_guard lock(mutex_);
    return peak_;
  }
 private:
  const std::size_t capacity_;
  mutable std::mutex mutex_;
  std::condition_variable not_empty_;
  std::condition_variable not_full_;
  std::deque<int> values_;
  std::size_t peak_ = 0;
  bool closed_ = false;
};

void queue_pipeline(std::size_t jobs, std::size_t workers, std::size_t capacity,
                    bool inject_worker_error = false) {
  require(workers > 0 && workers <= 32, "fixture worker count out of range");
  require(jobs <= 10000, "fixture job count out of range");
  BoundedQueue queue(capacity);
  std::vector<unsigned> hits(jobs, 0);
  std::mutex hits_mutex;
  std::mutex error_mutex;
  std::exception_ptr error;
  std::vector<std::jthread> threads;
  threads.reserve(workers);
  try {
    for (std::size_t i = 0; i < workers; ++i) {
      threads.emplace_back([&] {
        try {
          int job = 0;
          while (queue.pop(job)) {
            if (inject_worker_error && job == 3)
              throw std::runtime_error("intentional worker failure");
            // Production work runs OUTSIDE the queue mutex. This tiny lock only
            // verifies exact-once delivery; it is not a fast-processing example.
            std::lock_guard lock(hits_mutex);
            ++hits[static_cast<std::size_t>(job)];
          }
        } catch (...) {
          {
            std::lock_guard lock(error_mutex);
            if (!error) error = std::current_exception();
          }
          queue.close();  // wakes producer and other consumers
        }
      });
    }
    for (std::size_t job = 0; job < jobs; ++job)
      if (!queue.push(static_cast<int>(job))) break;
    queue.close();
  } catch (...) {
    queue.close();  // also covers allocation/thread-launch failure
    throw;          // already-started jthreads join during unwinding
  }
  threads.clear();  // no queue/error/hits lock is held while joining
  if (error) std::rethrow_exception(error);
  require(queue.peak_size() <= capacity, "queue exceeded bound");
  require(std::all_of(hits.begin(), hits.end(), [](unsigned n) { return n == 1; }),
          "job not delivered exactly once");
}

// Reuse only under an explicit ownership/alias contract. Capacity is not a budget
// for unbounded growth: call this only for an already bounded input batch.
void transform_reuse(const std::vector<double>& input, std::vector<double>& output) {
  if (&input == &output) throw std::invalid_argument("input/output must not alias");
  output.clear();
  output.reserve(input.size());
  for (const auto value : input) output.push_back(value * value + 1.0);
}

int main() {
  try {
    const std::vector<int> values{-2, 0, 1, 2, 0, 7, -9, 4, 5};
    for (const auto workers : {std::size_t{1}, std::size_t{2}, std::size_t{4}, std::size_t{16}}) {
      require(shared_tally(values, workers) == 5, "shared tally wrong");
      require(local_tally(values, workers) == 5, "local tally wrong");
    }
    require(local_tally({}, 4) == 0, "empty tally wrong");
    require(local_tally(values, 0) == 5, "zero request normalization wrong");
    std::vector<int> matrix(31 * 17);
    for (std::size_t i = 0; i < matrix.size(); ++i) matrix[i] = static_cast<int>(i % 23);
    require(column_first(matrix, 31, 17) == row_first(matrix, 31, 17), "layout sum differs");
    require(row_first({}, 0, 0) == 0, "empty matrix differs");
    for (const auto cap : {std::size_t{1}, std::size_t{7}})
      for (const auto workers : {std::size_t{1}, std::size_t{4}})
        queue_pipeline(257, workers, cap);
    queue_pipeline(0, 2, 1);
    bool failed = false;
    try { queue_pipeline(32, 3, 1, true); }
    catch (const std::runtime_error&) { failed = true; }
    require(failed, "worker exception was not propagated");
    BoundedQueue drain(2);
    require(drain.push(7) && drain.push(8), "initial push failed");
    drain.close();
    require(!drain.push(9), "closed queue accepted a new job");
    int item = 0;
    require(drain.pop(item) && item == 7, "first drain item wrong");
    require(drain.pop(item) && item == 8, "second drain item wrong");
    require(!drain.pop(item), "closed empty queue did not stop");
    std::vector<double> output;
    transform_reuse({-2.0, 0.0, 3.0}, output);
    require(output == std::vector<double>({5.0, 1.0, 10.0}), "transform wrong");
    const auto capacity = output.capacity();
    transform_reuse({1.0}, output);
    require(output == std::vector<double>({2.0}) && output.capacity() == capacity,
            "reuse did not preserve capacity/results");
    bool rejected = false;
    try { transform_reuse(output, output); }
    catch (const std::invalid_argument&) { rejected = true; }
    require(rejected, "aliased reuse input was accepted");
    std::cout << "all correctness checks passed\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
