# Local five-area continuation: textures, control lifetime, cache, scheduling and thread flags

## Provenance and question

- Date: 2026-10-31. Agent: Notion AI using local Python, Capstone and Unicorn; no subagents.
- Starting snapshot: previously checked main revision `120f87f3cb7341dfcc0afddd01b9646f16727864`. This is a separate local working copy, not a Git checkout or a newly published revision.
- User requested work on all five remaining areas. **User's later explicit permission boundary controls: no GitHub reading, fetching, commits, pushes, PRs, merges or publishing in this pass.** Earlier repository publication instructions are not authorization. This report, tests, records and manifests are local and unpublished.
- Goal: advance every listed area without substituting seeded success for genuine backend behavior or pretending an emulator provides iOS/GPU execution.

Authorized read-only inputs (verified by suite imports and again after execution):

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| Original | 17213264 | `b685c0f98b15597fb9eabb6d09758a2637246198a1af24a044c2010953fb80ab` |
| R03 | 17262416 | `d1a05ff2d8164ec326898d3d2d9709fb638f85d8550436f8e5d9c845be54b292` |

No input was edited, installed or executed on a device. Historical archive code was not executed. Writes occur only in emulated memory, local test/results files and this separate working copy.

## Outcome by requested area

| Area | Work completed locally | Still not established |
| --- | --- | --- |
| Menu / Float / Draw textures | 48 records: native loaders, Draw once callback, Float refresh/cache, Menu texture setter and Overlay normal-return composition | Actual image decode, Foundation/ObjC behavior, Metal allocation/upload and real UI success |
| Control-pointer lifetime / writers | Whole executable-text canonical global-reference index, previous allocation-publication result cross-check, three native destructor bodies | Complete alias-based writer inventory; actual free/replacement or valid lifetime of the 256-byte owner allocation |
| Backend / completion / cache | 40 cache-policy and 28 render/completion/device-state records, including native completion helpers composed with actual accepted cache body | Shader/pipeline internals, actual draw commands, GPU submission/error/completion, real ARC and concurrent cache safety |
| Reachable scheduling / reentry | Native secondary timer and callback truth table; selected direct-edge/root index; existing scheduling/reentry maps rerun | Positive runtime evidence of reentry between admission and attachment, queue accumulation, off-main UI writes or a race |
| Secondary setup producer / workers | 30 generic thread/atomic-flag records; concrete producer-to-launch and worker scope clear routes recovered | Execution of backend worker, real pthread scheduling/frequency, indirect success graph and genuine readiness/backend transitions |

**218 new labels passed. Full regression: 28 suites / 1329 labels passed, including all previous 1111 with equal retained record values.** These counts overlap, include paired builds and synthetic inputs, and are not unique end-to-end paths. All five areas were worked; none is falsely declared an all-path/device-level completion.

## Work performed and findings

### 1. Native texture callers — 48 records

Evidence: [test source](../../tests/continuation-l/test_textures.py), [complete records](../../results/continuations/continuation-l/texture-tests.json).

Executed the Draw initializer `0x17f28`, actual Draw once callback `0x18020`, Draw loader `0x18324`, Float initializer `0x123840`, Float loader `0x123b30`, and Menu setter `0x617460`. Composed their existing native calls with full Overlay normal return, including original/R03 return routes. Image decode, Foundation/base64, ObjC/ARC, texture descriptors/devices and upload are explicit providers, not actual decoder/GPU execution.

- Draw/Float entry guards reject nil device/source or zero source length. Decode-nil/nonpositive dimensions fail under the specified decode provider.
- Native callers request pixel format 70; provider inputs verify 2×3 dimensions, usage 1/storage mode 0, native region `[0,0,0,2,3,1]` and 8-byte row stride. The pixel free call is checked. This verifies caller construction, not image authenticity or memory/resource safety for every size.
- Nil descriptor alone does not force failure in the native caller: the device provider is still queried and can return a texture. Such cases are explicitly provider-conditioned, not genuine Metal success.
- Menu skips decoding on a subsequent setter call when its texture cache is nonnil in the model.
- Draw once skips repeated setup. Float refreshes its primary texture on repeat while reusing the optional cached texture. Its third texture stays absent under the native literal enabled mask 3 versus style-3 bit 4; this is a branch fact, not an assertion that a production asset is missing unexpectedly.

### 2. Pointer ownership, writers and destructor boundaries

Evidence: [bounded mapper](../../tests/continuation-l/map_state_and_roots.py), [static metadata](../../results/continuations/continuation-l/state-and-root-map.json), [72-record state/destructor suite](../../tests/continuation-l/test_state_routes.py), [records](../../results/continuations/continuation-l/state-route-tests.json).

The mapper scans aligned words in all executable `__text` sections, including appended R03 text. It follows canonical ADRP-derived addresses for at most 12 straight-line instructions, invalidating overwritten registers. It is deliberately not a full disassembler/data-flow/alias or heap-lifetime analysis. Its conservative branch-prefix cutoff can stop on some nonbranch mnemonics too; absence is weak negative evidence.

- Original: 286 mapped references across seven declared globals; R03: 294. Both have 143 direct owner-slot reads and one canonical owner-slot store at `0x70fb0` in the already known allocation/publication function. This agrees with the previous 256-byte allocation excerpt. It does not prove one allocation for the process lifetime or no indirect replacement.
- Each build has one mapped direct publication into each Overlay/Draw/Float control slot. Later pointer arguments in synthetic reuse tests are not evidence of real replacement.
- Across 23 functions with mapped owner-slot references, no direct imported free/C++ delete call was found. That limited search excludes aliasing, indirect callees, other functions and custom deallocation; **it does not prove that the allocation cannot be freed**.
- Actual `.cxx_destruct` metadata/body tests for OverlayView, MetalContext and MetalBuffer clear their strong fields but leave the four tracked raw control globals unchanged. These are not complete `dealloc`/heap-free/ARC executions and do not prove dangling pointers.
- Appended R03 references without finite known function boundaries are attributed to `null` (three references), not the last original function. This corrects a provisional mapper attribution before records were retained.

The existing native tap test still establishes an XOR of bit 0 through the first Overlay control pointer. This pass does **not** turn the bounded global index into an exhaustive list of pointee writers. Allocation lifetime and aliased writers remain open, explicitly.

### 3. Accepted cache policy — 40 records

Evidence: [source](../../tests/continuation-l/test_cache_policy.py), [records](../../results/continuations/continuation-l/cache-policy-tests.json). Native enqueue `0x12c06c` and dequeue `0x12b6f4` execute through return. Foundation arrays/dates/enumeration, getters, ARC and lock effects are modeled. Both complete selected body windows match between original/R03.

- Admission requires incoming size at most 16 MiB, fewer than eight current entries, and aggregate size plus incoming at most 16 MiB. Exact budget limits pass. A rejected incoming buffer does not evict existing entries in these cases.
- Dequeue chooses the smallest fitting length, retaining the first encountered tie, and removes by object identity. Allocation fallback occurs after unlock.
- Purge occurs when elapsed time is **strictly greater than one second**, not at equality. It keeps entries whose last-reuse timestamp is **strictly greater than the previous purge timestamp**, then advances the purge time to now.
- The native caller has no duplicate admission check in the tested same-wrapper sequence. This is synthetic duplicate delivery, not an observed runtime bug.
- A nil underlying buffer can coexist with a nonnil wrapper if the explicitly modeled wrapper initializer allows it. That boundary is not evidence the real initializer behaves that way.

No actual mutex exclusion, contention, concurrent mutation or allocator behavior is established.

### 4. Render registration → completion helpers → accepted cache — 28 records

Evidence: [source](../../tests/continuation-l/test_backend_completion.py), [records](../../results/continuations/continuation-l/backend-completion-tests.json).

Executed native `MetalContext renderDrawData:commandBuffer:commandEncoder:` at `0x12e2d0` with synthetic zero/tiny geometry. Native caller copy sizes are checked (0/20 vertex bytes, 0/2 index bytes). The one command list contains **zero draw commands**. `setupRenderState`, pipeline and dequeue providers remain modeled.

- `addCompletedHandler:` receives native invoke `0x12edb8` and actual captured vertex/index wrappers. The harness models heap block allocation, then executes native copy helper `0x12eea8`.
- After caller return, the harness manually invokes completion and native dispose `0x12ef14`. With modeled live weak context, actual native enqueue bodies receive both captured wrappers. With modeled nil weak context they are not recycled. The helper capture fields are cleared by modeled strong-store effects during native disposal.
- Width-zero/no-list guards return without setup/copy/registration in these cases.
- Pipeline nil can still reach registration under the explicit no-op setup provider; command nil suppresses effective handler messaging. Neither is a genuine successful render.
- Native device-object/depth-state caller `0x12b364` requests depth-write disabled and compare function 7. Nil state is propagated into the property setter. Descriptor/device results are providers; the void return is not interpreted as a success flag.

No actual Blocks runtime ownership duration, GPU submission, command-buffer error, real callback delivery, shaders or physical rendering was tested.

### 5. Scheduling and secondary request/worker flag — 72 state + 30 thread records

Evidence: [state suite](../../tests/continuation-l/test_state_routes.py), [thread suite](../../tests/continuation-l/test_thread_flags.py), [thread records](../../results/continuations/continuation-l/thread-flag-tests.json), static map above. The 72 state records include six destructor cases already discussed, two repeated-timer sequences, and 64 callback truth-table cases.

- Native timer `0x438dc` requests `dispatch_time(DISPATCH_TIME_NOW, 2,000,000,000 ns)`, then `dispatch_after` on the imported main queue with global block `0xfd9dd0`, invoke `0x7bae0`. Three manual calls issue three requests; the helper itself does not coalesce. This is not observed runtime queue growth.
- Callback routing: if startup gate is set, exit. Otherwise a false readiness provider schedules retry. With readiness true, work-boundary `0x3973c` is reached unless guard, lifecycle predicate and request byte are all true. The genuine readiness/lifecycle callees and work body are not executed. Flags are unchanged by the tested native atomic loads.
- At static caller `0x73cdc`–`0x73cf4`, thread storage `0x1011b08`, request-byte address `0x1010a37` and worker entry `0x4137c` feed generic launch `0x104488` → `0x104474` → `0x74d08`. The enclosing producer/backend function is **not executed** or claimed reachable under genuine success.
- Native launch does compare-exchange 0→1. Already-set flag returns true without `pthread_create`; this is launch suppression, not evidence a thread was successfully started by that call.
- On modeled create failure it clears the flag, zeroes thread storage and returns false. On modeled create success it requests detach and returns true even when detach provider reports nonzero. These are generic caller contracts; no real thread runs.
- Native worker prefix calls scope constructor `0x2d3f0` → `0xed510` → `0xed4f0` → `0x622dc`, storing the flag address and setting it to one. Normal worker tail calls `0xf6694` → `0xf6674` → `0x3527c` → `0x679fc`, which clears that byte. The exception edge uses the same cleanup. Scope constructor and both cleanup helpers are executed **manually in isolation**; worker body/completion and exception unwinding are not.
- Duplicate, failure-then-retry, and manual-cleanup-then-relaunch sequences pass with native atomics. Unicorn sequential execution is not a proof of architecture-wide memory ordering, fairness, actual thread overlap or production frequency.

The bounded mapper records 13 initializer roots/build and 25 original/26 R03 selected direct edges. Seven selected benign windows match. Existing main-queue scheduling and startup maps were rerun; this still provides **no positive evidence of synchronous reentry between callback admission and attachment**. An available pthread route does not establish off-main UIKit mutation. Remaining indirect targets/genuine backend transitions stay unresolved; authentication/trust/anti-cheat/access-control bypass work is excluded.

## Validation and corrections

- Environment: Python 3.13.15, Capstone 5.0.7, Unicorn 2.1.4, Linux ARM64 emulation. Both authorized input identities match before/after.
- Full native/model runner: 28 suites / 1329 labels pass. All 1111 earlier retained record values match after key normalization (including stable synthetic nonfinite spellings); five new suites add 218 labels. [Complete regression summary](../../results/continuations/continuation-l/regression-summary.json).
- The continuation artifact validator now explicitly expects **1035 continuation records across a–l**, separate from the 294 base records. No earlier record was overwritten.
- Existing scheduling/reentry static mappers, intake/publication-metadata validators, Python syntax, internal relative links, complete local inventory and checksums checked. Publication validator reads old local metadata only: no release/GitHub request was made.
- Harness corrections retained honestly: standalone Menu initially omitted modeled device state; the new texture alloc override initially failed on an inherited known allocation and was corrected to delegate explicitly. Cache failed closed on an initially expected `removeObject:` selector; actual native selector is `removeObjectIdenticalTo:`. Completion encountered previously unmodeled `_objc_retainAutorelease`; an explicit identity ARC boundary was added. Provisional static attribution for appended text was corrected to unknown. No unknown-selector blanket fallback or native patch was added to make tests pass.
- Generic scope-helper exploration initially looked at an unrelated constructor; only the actual worker tail's normal/exception cleanup edges described above are retained as evidence.

Reproduce with authorized inputs configured (no archive code/network needed):

```bash
export AU_ORIGINAL="/absolute/path/to/authorized/original/AccessibilityUtilities"
export AU_R03="/absolute/path/to/authorized/r03/AccessibilityUtilities"
python tools/run-native-regression.py
python tests/continuation-l/map_state_and_roots.py
python tests/continuation-c/map_scheduling.py
python tests/continuation-d/map_reentry_boundaries.py
python tools/validate-continuation-results.py
python tools/validate-attachment-intake.py
python tools/validate-original-attachments.py
sha256sum -c SHA256SUMS
```

## Files and retention

New scripts live in `tests/continuation-l/`; complete five-suite records, static map, regression summary and provenance in `results/continuations/continuation-l/`. This report and navigation/worklog/integrity files are updated in the separate local copy. Earlier files/results remain intact, except the explicitly expanded validator/navigation.

Inputs, downloaded source ZIPs, raw proprietary instruction scratch, bytecode caches, transient paths and unreviewed logs are not included in the curated handoff. The local evidence archive is a convenience wrapper around reviewed text files, **not a build or source binary release**. Existing historical release links in older documents are not evidence this pass was published.

## Limits and next concrete work

There is no established FPS/touch root cause, fixed binary, actual race, valid/dangling pointer proof, complete image/GPU success or complete original success graph. More synthetic cases alone cannot settle those claims.

Using existing authorized captures only, the next useful questions are: correlate any concrete control-pointer alias/free/replacement chain; inspect decoder/pipeline/draw-command internals within benign scope; and look for an actual synchronous callback path that reenters construction. Genuine iOS/Metal/ARC/thread-delivery behavior remains unavailable in this Linux environment. Do not request a new diagnostic build or invent real backend success. Do not perform any GitHub action without a new explicit user request.
