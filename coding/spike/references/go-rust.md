# Go and Rust spikes

Same placement rule: one file (or one tiny directory) named after the idea, in the experiments repo if present.

## Go

Stdlib only:

```sh
go run idea.go
```

When a module path is required, reuse the experiments repo's **one** `go.mod` at the root. Do not `go mod init` per idea.

```sh
go get github.com/example/mod@v1.2.3
go run idea.go
```

A single `package main` file is enough. `log.Fatal` / early `return` is fine. Skip per-idea modules, Docker, cobra, and a `cmd/` tree.

Background: [How to Write Go Code](https://go.dev/doc/code).

## Rust

No extra crates:

```sh
rustc idea.rs -o idea && ./idea
```

With crates, prefer a single file over a new package:

- **rust-script** (stable, practical): [rust-script](https://rust-script.org/)

```rust
#!/usr/bin/env rust-script
//! ```cargo
//! [dependencies]
//! anyhow = "1"
//! ```
fn main() -> anyhow::Result<()> {
    let v: i32 = "12".parse()?;
    println!("{v}");
    Ok(())
}
```

```sh
rust-script idea.rs
```

- **Nightly cargo script** is still unstable in 2026 ([Cargo unstable: script](https://doc.rust-lang.org/nightly/cargo/reference/unstable.html#script), goal: [Stabilize cargo-script](https://goals.rust-lang.org/2026/cargo-script.html)):

```sh
cargo +nightly -Zscript idea.rs
```

If the experiments repo already is a Cargo workspace, add a binary target or a small `examples/idea.rs` and reuse workspace deps. Do not `cargo new` for every idea.

`anyhow` and `unwrap()` are fine in a spike. Skip clippy-as-gate, `thiserror` trees, features matrices, and CI.

## Success signal

`go run idea.go` or `rust-script idea.rs` / `./idea` prints the result you named and exits 0.
