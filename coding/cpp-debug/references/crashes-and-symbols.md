# Crashes, incorrect results and matching symbols

Load when the failure needs debugger evidence, a core/minidump, or a smaller reproducer. These are command recipes for an authorized local target, not commands already executed by this skill. Check `gdb --help` / `lldb --help` and installed-version documentation; OS packaging and debugger plugins differ.

## Evidence packet before a fix

Keep a small private record: failing revision and build identity; exact executable/libraries/symbol artifacts; invocation; input identity or random seed; expected result; first observed wrong state; frequency; supported platform/compiler/preset. Hashes identify retained files, but matching arbitrary hashes does not establish that a symbol file belongs to an executable.

For deterministic wrong results, reduce input while keeping the mismatch. Compare the first incorrect intermediate state against a reference/invariant, not only the final crash. For a missing reproducer, identify the next missing artifact or a bounded capture point; do not claim a speculative patch fixes the failure.

## Match artifacts before reading stacks

- ELF: examine the executable/debug-file build ID and debugger's symbol-loading messages. A source path and plausible function names are not identity checks.
- Mach-O: compare binary and dSYM UUIDs, including the selected architecture slice; an old dSYM does not become valid because its path matches.
- Windows: retain the matching module/PDB pair and verify identity using the chosen debugger's module/symbol diagnostics. Do not infer a match from filenames or timestamps alone.
- Preserve shared-library versions too. A correct executable plus wrong dependency symbols can still mislead.

On systems with the corresponding tools, these inspect rather than run the program:

```sh
readelf -n ./retained-program
# macOS alternative, with an existing dSYM:
dwarfdump --uuid ./retained-program
dwarfdump --uuid ./retained-program.dSYM
```

Use only the platform-appropriate line. Core dumps and full local-variable displays can contain credentials, personal data or proprietary input. Keep them private and review/redact before sharing.

## Existing core: start without target execution

For GDB, suppress startup/auto-loaded scripts when their trust has not been established. Use retained local symbols, not automatic symbol-server downloads. On GDB builds with debuginfod support, add the early option `-iex 'set debuginfod enabled off'` before loading artifacts; if the command is unsupported, that feature is not available in that build. Do not accept a network-fetch prompt in an offline investigation:

```sh
gdb -nx -iex 'set auto-load off' -iex 'set debuginfod enabled off' ./retained-program ./retained.core
```

Then inspect:

```text
info files
info sharedlibrary
info threads
thread apply all bt 20
frame 0
info locals
```

`20` bounds frames per thread; it is not a required universal depth. Begin with stacks, expand selected frames/variables as needed. Disabling auto-loading can remove useful printers or thread helpers; enable only a specifically trusted helper if required. Do not solve that by globally disabling safe-path checks. Do not call target functions or use expression commands with side effects merely to inspect a core.

An LLDB equivalent for trusted artifacts, suppressing init files:

```sh
lldb --no-lldbinit --core ./retained.core ./retained-program
```

Useful LLDB commands are `image list`, `thread list`, `thread backtrace all`, `frame select 0`, and `frame variable`. Check `help thread backtrace` to bound output for large processes. For untrusted artifacts, also inspect the installed LLDB's script-loading settings; avoiding init files is not a general sandbox. Loading a dump parses complex input, so keep debugger versions maintained.

These commands do not create a core. If none exists, choose the OS's approved crash collection facility and a bounded reproducer. Do not alter system-wide core policy or attach to somebody else's process without authorization.

## Live reproduction: stop at the first bad boundary

Only launch a trusted target when executing it is authorized; its normal filesystem/network effects still occur under a debugger. Supply the original arguments and input, not a similar invocation. These commands are an optional next step after artifact checks, not necessary for reading an existing core.

| Intent | GDB | LLDB |
| --- | --- | --- |
| Select program arguments before launch | `set args representative-input` | `settings set target.run-args representative-input` |
| Stop in a known function | `break parse_frame` | `breakpoint set --name parse_frame` |
| Launch the configured target | `run` | `run` |
| Continue to next stop | `continue` | `continue` |
| Inspect a local without intentionally calling code | `info locals` | `frame variable` |
| Inspect source/assembly relationship | `disassemble /m parse_frame` | `disassemble --name parse_frame --mixed` |

Function names and arguments are illustrative, not shell placeholders to execute blindly. Optimized/inlined code may not stop on the expected source line. If a field unexpectedly changes, a carefully scoped watchpoint can identify its writer, but hardware slots/size are limited and addresses can become stale after reallocation. Establish the object's live storage first. Do not evaluate user-defined getters or overloaded expressions just to “print” a value when they could change state.

## Interpreting the result

| Observation | Next discriminating check |
| --- | --- |
| Stack points inside allocator/vendor | Check earlier caller bounds/lifetime; crash location is not necessarily corruption origin |
| Locals optimized out | Keep original evidence; reproduce with symbols/appropriate optimization rather than invent values |
| Debug works, Release fails | Compare macros, UB-sensitive paths, timing and ABI; Debug success is not a cause |
| Stack lacks symbols or looks implausible | Resolve artifact identity/unwinding before trusting exact source lines |
| Pointer valid at capture, later stale | Establish owner/invalidation event; a non-null address does not prove lifetime |

End with the supported cause or remaining hypothesis, exact evidence, minimal proposed change and reproduction/regression check. State what could not be observed.

## Offline scenario checks

- **Release crash, only yesterday's symbols:** retain the failing executable/libraries; do not diagnose source lines from the mismatched set. Next request is the matching artifact or a fresh comparable reproducer, not a guessed patch.
- **Crash in allocator after frame processing:** inspect earlier ownership/bounds transitions and preserve sanitizer evidence; replacing the allocator without causality is not a correction.
- **Wrong deterministic output, no crash:** reduce input and locate the first violated invariant under a live authorized reproducer; a core dump is not required for every bug.
- **Missing debugger or symbolizer:** record the artifact gap, use existing logs/invariants and a minimal input, and state that stack attribution is unverified. No tool download or online lookup is required to proceed this far.

## Sources

- GDB [auto-loading controls](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Auto_002dloading.html), [threads](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Threads.html), [separate debug files](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Separate-Debug-Files.html).
- LLDB [command map](https://lldb.llvm.org/use/map.html) and [symbols on macOS](https://lldb.llvm.org/use/symbols.html).
- GNU binutils [readelf](https://sourceware.org/binutils/docs/binutils/readelf.html); LLVM [dwarfdump](https://llvm.org/docs/CommandGuide/llvm-dwarfdump.html).

The links describe current tools; match commands and identity mechanisms to the installed debugger/toolchain. This workflow is original guidance, not a copied debugger manual.

## Optional local context snapshot

From the skill directory, `python3 scripts/environment_snapshot.py --help` and `python3 scripts/environment_snapshot.py` use installed Python 3.9+ standard library only; on Windows use `py -3` or the explicit Python 3 executable. The script prints selected platform fields and discovered tool paths without running any tool, dumping environment variables, reading core data or using the network. Missing tools are JSON null; a discovered executable path does not establish working permissions/version. Review paths before sharing because they may contain a user-directory name. Redirect stdout only when intentionally saving a snapshot.
