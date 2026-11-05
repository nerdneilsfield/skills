# Window-Sketch: Bounded-Memory Frequency Estimation for Streaming Telemetry

**Authors:** R. Okonkwo, M. Lindqvist, A. Bhatt
**Venue:** Proceedings of the Workshop on Streaming Systems (WSS), 2024
**Status:** Self-authored fixture for skill evaluation. Not a real publication.
**License:** CC0 1.0 Universal (public domain dedication).

## Abstract

Counting exact event frequencies over a high-volume telemetry stream requires memory
proportional to the number of distinct keys, which is often larger than the machine.
We present Window-Sketch, a fixed-size sketch that answers point-frequency queries over
a recent telemetry window using 96 KB regardless of key cardinality. Window-Sketch
replaces the per-key counters of a standard count-min sketch with a windowed decay
schedule, so that evicted observations stop contributing to estimates. On a 12-hour
trace of 1.4 billion events from a production API gateway, Window-Sketch reports a mean
absolute relative error of 3.1% at the 99th percentile of heavy-hitter queries, versus
11.7% for a count-min sketch of the same memory. The sketch does not support range
queries, does not preserve exact counts for any key, and offers no error guarantee for
keys below the reporting threshold, which we discuss in Section 6.

## 1. Introduction

Telemetry pipelines frequently need to answer questions of the form "how often did this
endpoint 404 in the last ten seconds". The exact answer requires a hash table whose size
grows with the number of distinct endpoints. In the gateway we instrumented, distinct
keys over a ten-second window reach roughly 4 million under load, and the exact table
occupies about 190 MB, ten times the memory budget the gateway team would accept.

Frequency-estimation sketches trade accuracy for fixed memory. The count-min sketch of
Cormode and Muthukrishnan [3] hashes each key into several counter arrays and reports the
minimum over the probed counters, which can only overestimate. It performs well when the
distribution of interest is stationary over the whole stream. Telemetry does not behave
that way: the endpoints that matter are the ones that spiked recently, and a count-min
sketch never forgets the January traffic that made an endpoint famous.

Two obvious designs exist. Sliding-window exact counters keep a ring of per-interval
hash tables and sum across boundaries; they have exact error and unbounded memory. The
decaying count-min sketch multiplies every counter by a decay factor on each periodic
tick; it bounds memory but its decay is applied uniformly, so an infrequent but bursty
key decays at the same rate as a steadily noisy one.

**Contribution.** Window-Sketch keeps the count-min probing structure but attaches a
per-bucket last-touch timestamp and decays a counter only when that counter is probed.
The design targets three goals: constant memory independent of cardinality, error that
degrades gracefully with the reporting threshold, and a decay rule that is cheap on the
query path rather than on a background timer.

## 2. Background and Notation

Let *D* be the stream of events, each carrying a key and a timestamp. For a key *k* and
a query time *t*, the windowed frequency *f(k, t)* is the number of events with key *k*
in the half-open interval *(t − W, t]*, where *W* is the window length. A sketch returns
an estimate *f̂(k, t)*.

A count-min sketch uses *d* arrays of *w* counters, and *d* independent hash functions
*h₁ … h_d*. On an update it increments one counter in each array. On a query it returns
the minimum of the *d* probed counters, which may be written

    f̂(k) = min_{i=1..d} C_i[h_i(k)]

The classical error result of [3] gives, with probability at least 1 − δ,

    f̂(k) ≤ f(k) + εN

where *N* is the total count in the sketch and ε = e/w. This bound is over the whole
stream *N*, not over the window, and that is the source of the inaccuracy we address:
as *N* grows, the additive error grows with it even though the window is fixed.

## 3. Method

Window-Sketch stores, for every counter, a 32-bit count and a 16-bit last-touch stamp
quantized to 1/256 of the window length.

**Update.** Given an event with key *k* at time *t*, for each array *i*, let
*c = C_i[h_i(k)]*, and let *s* be its stamp. Before incrementing, apply

    c ← floor(c · γ^(t − s)) ,  where γ = 0.5^(1/W)

and then set *c ← c + 1*, stamp ← *t*. The decay is applied lazily, only to the counters
that an update or query actually touches, so a counter that no event has touched since
time *s* carries stale mass that is corrected the next time it is read.

**Query.** The query path repeats the same lazy decay for the *d* probed counters and
returns their minimum. Because decay is exponential and applied in closed form, the
estimate at a query time does not depend on how many updates happened in between, only
on elapsed time.

**Why lazy decay rather than a timer.** A periodic decay pass must traverse the whole
sketch, which costs O(w·d) every tick and makes tail latency unpredictable under load.
Lazy decay moves that cost onto the probe path, where it is O(d) and pays only for
counters in use. The trade-off is that the sketch is not self-consistent between
updates: reading a counter without probing it returns a stale value. Our query API does
not expose raw counters, so this is not observable to callers, but it does mean the
sketch cannot be snapshotted mid-stream and resumed later without a normalization pass.

**Parameters.** *d* = 4, *w* = 12,000, giving 96 KB for the whole sketch including
stamps. We chose *d* = 4 rather than 5 because the fifth row improved mean error by
0.2 percentage points in pilot runs while costing 24 KB, and the gateway memory budget
was the binding constraint.

## 4. Experimental Setup

**Trace.** 12 hours of production API-gateway telemetry from a single region,
1.4 × 10⁹ events, 3.9 × 10⁶ distinct endpoints per ten-second window, peak 41 K
events/second. Keys are endpoint paths with path parameters templated.

**Hardware.** One 16-core x86-64 server, 64 GB RAM, single-threaded sketch updates to
keep the measurement about the algorithm rather than the cache hierarchy.

**Baselines.** (a) exact hash table with window eviction, (b) count-min sketch with
*w* = 12,000, *d* = 4, no decay, (c) count-min sketch with a uniform global decay applied
every second, (d) sliding-window exact counters.

**Metrics.** Mean absolute relative error (MARE) over the top-1000 keys by true windowed
frequency, sampled every 10 seconds; and the fraction of heavy-hitter queries whose error
exceeds 10%. Baselines (a) and (d) are exact and are included only to establish memory,
not error.

## 5. Results

| Design | Memory | MARE p50 | MARE p99 | >10% error |
| --- | --- | --- | --- | --- |
| Exact table | 190 MB | 0.0% | 0.0% | 0.0% |
| Sliding-window exact | 310 MB | 0.0% | 0.0% | 0.0% |
| Count-min, no decay | 96 KB | 4.9% | 11.7% | 21.4% |
| Count-min, uniform decay | 96 KB | 4.1% | 9.3% | 14.8% |
| Window-Sketch | 96 KB | 1.8% | 3.1% | 2.0% |

The gain over the no-decay count-min sketch is largest exactly where we predicted, on
keys whose popularity is concentrated near the query time. The gain over uniform decay
is smaller but consistent, and we attribute it to the bursty-but-infrequent keys that a
global decay penalizes at the same rate as steady noise.

**Ablation on d.** Increasing *d* from 4 to 5 lowered MARE p99 from 3.1% to 2.8% at 20%
more memory; increasing *w* from 12,000 to 24,000 at *d* = 4 gave 2.2%. We report the
*d* = 4, *w* = 12,000 configuration throughout because it fits the stated budget.

**Throughput.** Updates run at 2.1 M events/second single-threaded, about 0.6× the
no-decay count-min sketch, because of the extra stamp update and the floating-point decay.
At the observed peak of 41 K events/second this leaves ample headroom, but a deployment
that tried to use one core for ten such gateways would need to reconsider.

## 6. Limitations

We state these plainly because the abstract's error numbers may invite more confidence
than the method supports.

1. **No error bound below the reporting threshold.** The lazily decayed counters carry no
   guarantee for low-frequency keys; our MARE numbers cover the top-1000 keys only. For
   the long tail, the relative error is unbounded and can exceed 100%.
2. **Single-region trace.** All results come from one gateway in one region with a
   particular endpoint-naming convention. We did not test traces with adversarial key
   distributions, nor with hash collisions induced deliberately.
3. **Stationarity of the decay constant.** γ is fixed at construction. If traffic volume
   changes by an order of magnitude within a window, the effective half-life in events
   changes too, and we did not evaluate an adaptive γ.
4. **No direct comparison at equal update cost.** The uniform-decay baseline applies its
   decay on a timer; we did not implement a version that decays lazily, so part of the gap
   in Section 5 may reflect implementation effort rather than the decay rule.
5. **Snapshot/resume unsupported**, as described in Section 3.

## 7. Reproduction Notes

The authors' prototype is a single C++ translation unit with no external dependencies
beyond the standard library. To reconstruct the results:

1. Generate or obtain a trace with (key, timestamp) pairs; the production trace is not
   distributable and is not included.
2. Implement the lazy decay exactly as in Section 3, including the 16-bit stamp
   quantization at 1/256 of *W*.
3. Reproduce the baselines; report MARE over the same top-1000 key set.
4. Expected result: MARE p99 near 3% for Window-Sketch and 11–12% for the no-decay
   count-min sketch.

We do not publish the trace, the seed for hash function selection, or the exact
quantization rounding mode, which means an independent reproduction is unlikely to
match our numbers to the digit. We consider the ordering of the designs, not the exact
percentages, to be the reproducible claim.

## 8. Conclusion

Bounding the memory of a frequency sketch is easy; bounding it while keeping the estimate
anchored to a recent window is the harder problem. Lazy exponential decay on the probe
path gives constant memory and a usable error profile for heavy hitters, at the cost of a
throughput penalty and no guarantee for the tail. The next step we would take is an
adaptive γ driven by observed update rate, and a lazy-decay baseline at equal update cost.

## References

[3] G. Cormode and S. Muthukrishnan. An improved data stream summary: the count-min
sketch and its applications. Journal of Algorithms, 55(1):58–75, 2005.