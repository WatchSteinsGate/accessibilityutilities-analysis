<!-- Repository edition: curated from this session continuation; see OMISSIONS.md. -->

# Lifecycle cancellation, render cleanup and shortcut consumer — continuation

## Outcome

Continued the remaining framework-local trace using the supplied original and R03 ARM64 images. **232 labeled scoped cases passed**, across original/R03, synthetic failures, sequential compositions and manually seeded cleanup states. These are not 232 independent end-to-end paths or device runs. No binary was modified, patched, signed, installed or executed on iOS. Native ARM64 instructions were executed locally in Unicorn with explicitly modeled boundaries.

The original and R03 input hashes were checked before investigation and after the final rerun:

| Input | SHA-256 |
| --- | --- |
| Supplied original workpack reference | `b685c0f98b15597fb9eabb6d09758a2637246198a1af24a044c2010953fb80ab` |
| Supplied R03 | `d1a05ff2d8164ec326898d3d2d9709fb638f85d8550436f8e5d9c845be54b292` |

The game executable was not needed or downloaded for this framework-local pass.

## 1. Cancellation and previously queued constructor callbacks

**94 cases** in [cancellation-tests.json](../results/continuations/continuation-a/cancellation-tests.json).

Executed the native suspend mutator `0x7b0b8` and resume mutator `0x7b9a4`, then the queued constructor's eligibility prefix at `0x76944`, stopping before UI construction. Shared-state mutex construction/destruction and the R03 journal sink were modeled.

- Suspend clears readiness and active state and advances both attempt/event generations.
- Resume restores readiness, leaves active cleared, and advances both generations again.
- A block retaining its earlier attempt-generation value is rejected by the original constructor prefix after these transitions.
- Seeding active true after resume does not make the old captured generation current again. This is a deliberately seeded local state, not an executed genuine activation pipeline.
- R03's already documented constructor redirect reaches the UI boundary without those native generation/readiness/active/blocking checks. This pass composes that existing change with cancellation; it does not discover a new patch or establish a visible stale-overlay event on device.
- Counter values near unsigned wrap were included. Wrap is ordinary 64-bit arithmetic in these executions, not proof of behavior after a full generation cycle.

The remaining original predicate bodies were executed natively: attempt generation and shared-state eligibility checks, followed by the separate blocking-flag accessor. The tests stop at `0x769b4` (UI boundary) or `0x76dc8` (early exit). They do not run UI construction, authentication, backend transitions or actual asynchronous ownership.

## 2. Lifecycle re-evaluation queue

**24 cases** in [lifecycle-queue-tests.json](../results/continuations/continuation-a/lifecycle-queue-tests.json).

The helper `0x7b8d0` and callback `0x7ba04` are byte-identical across these builds.

- Three sequential helper invocations before draining generate one modeled dispatch enqueue request.
- The callback clears the pending marker before its blocking checks.
- With either blocking flag set, it does not ask for application state or invoke the transition boundary.
- Otherwise, it queries `sharedApplication` / `applicationState` when drained and passes whether that returned state is zero to the transition callee.
- A subsequent invocation can enqueue again after either a normal or blocked callback.

The transition callee `0x7b188` was a boundary in these tests; its full body was not executed. Thus this confirms scheduling/drain-time argument behavior, not the full lifecycle notification-to-UI pipeline. The coalescing byte is tested sequentially; dispatch ordering, simultaneous producers, real queue retention and races remain unverified.

## 3. Render resource failures, normal cleanup and recovery

Part of **104 cases** in [render-tests.json](../results/continuations/continuation-a/render-tests.json).

Executed the native `drawInMTKView:` control flow at `0x685d6c`, including native wrappers, normal exits and R03 observation trampolines. Explicitly modeled Objective-C calls, retain/release accounting, clock results, context/IO/draw-data providers, ImGui/Metal frame/encoding callees, and the journal sink.

Synthetic failure coverage:

- Nil view, nil device, nil command queue.
- Inactive application state.
- Nil context, command buffer, render-pass descriptor, drawable, draw data, or render encoder.

For both images:

- Each tested failure suppresses the present/commit sequence.
- Acquired modeled strong references balance on the tested normal exit paths.
- Restoring valid provider results permits the following modeled frame to reach present/commit; no stuck frame-local cleanup state was observed in these sequences.
- Both the render-pass descriptor and drawable are requested before the combined nil check. A nil descriptor therefore does not by itself skip the drawable getter.
- A missing draw-data/encoder result can occur after frame/UI-producing callees have already been reached. Skipping submission is not equivalent to skipping all frame work.

These are return-value faults at modeled boundaries, not observed device resource failures. The encoding backend itself and collector internals were not executed. Balanced test counters are not a proof of real ARC correctness.

### R03 late-inactivity guard scope

Two staged boundaries were tested per build:

1. Change the readiness byte to inactive at the modeled draw-data provider, before the late guard. Original continues to the submission path; R03 skips it, clears its timing baseline and performs normal resource cleanup.
2. Change that byte during the modeled encoding boundary, after the guard. Both images still reach the subsequent present/commit messages.

This bounds the guard's observation point. It neither cancels earlier UI/collection work nor establishes protection against every later state change. These are synchronous staged mutations, not real concurrent lifecycle events and not evidence of a race occurring on the user's device.

## 4. Shortcut signal consumer and publication

Also within the **104 render/shortcut cases**.

A bounded whole-original-`__text` ADRP-window scan found seven direct-reference candidates for the control-pointer global. Reference-candidate addresses are retained in `../results/continuations/continuation-a/shortcut-reference-candidates.json`; raw instruction windows are deliberately omitted. It is not a proof that no indirect references exist.

- The initializer prefix at `0x684454` publishes its raw `x2` argument to the control-pointer global. Executed only through that store, stopping before subsequent construction; tested nil and two distinct pointers in both images.
- The unchanged shortcut callback `0x686f8c`, for recognizer state numeric 3 and a nonnil pointer, writes byte 1 to the first control byte.
- Native frame control flow reads that first byte as part of deciding whether to call the menu's drawing method, assuming a nonnil modeled menu object and valid frame prerequisites.
- The adjacent second control byte separately inhibits the float-window branch when set.
- The composed tests cover six gesture states, pointer present/absent and both second-byte values. Repeated qualifying callbacks leave the first byte at 1; the tested frame path does not consume/reset it.

This closes the immediate shortcut-to-frame-menu-branch edge. It does **not** establish the full ownership/lifetime of the caller-provided pointer, all later writers of its pointee, actual UIKit gesture delivery, visible menu behavior, or every caller that constructs an overlay.

## 5. Native exceptional-cleanup tails — bounded only

**10 cases** in [cleanup-tail-tests.json](../results/continuations/continuation-a/cleanup-tail-tests.json).

Entered five native landing-pad tails per image, using manually seeded stack-frame locals and modeled ownership counters, then stopped at `_Unwind_Resume`.

The tested tails clear their expected strong locals, release the seeded temporary where applicable, and preserve the exception argument delivered to the unwind boundary.

These tests do not throw an exception, select a landing pad using unwind metadata, execute real unwinding, or establish Objective-C/Metal exception safety. They are cleanup-tail bookkeeping tests, not true exceptional runtime executions.

## 6. Harness corrections and safeguards

The first frame-test attempt exposed a harness binding issue: an unresolved imported UIKit class reference was zero in the raw Mach-O. The model had therefore returned zero application state through a nil receiver. A symbolic class receiver was explicitly bound, and the entire final suite was rerun. This was a harness correction, not a framework change.

The emulator also explicitly binds the external stack-canary reference when unresolved and rejects unexpected low-page data reads. Unmodeled imported calls raise errors rather than silently returning success. The R03 journal implementation remains a modeled sink, so logger safety/cost is not tested.

Inputs are hash-checked on module load. The repository edition contains the parser, emulator, scripts, JSON records and scoped metadata; raw proprietary disassembly and source ZIP archives remain deliberately omitted. It contains no original or patched framework binary and no release tooling. Repository reproduction is documented in [CONTINUATION-REPRODUCTION.md](CONTINUATION-REPRODUCTION.md).

## 7. What remains open

This is a continuation, not all-path completion:

- Real asynchronous callback ownership, interleavings, cancellation after eligibility checks, and notification/queue races.
- Full lifecycle transition body and downstream UI-construction composition under actual runtime behavior.
- Real exception throwing, unwind metadata/landing-pad selection and runtime cleanup.
- Collector/render-backend internals, GPU outcomes, physical touch latency and device FPS.
- Full callers and lifetime of the shortcut control pointer, and indirect/other pointee writers.
- The secondary setup-word producer and intended trigger frequency.
- Additional workers, indirect runtime calls and outstanding changed-function semantic coverage.
- Genuine backend transitions remain unestablished; no authentication, certificate-trust, anti-cheat or access-control bypass was implemented or extended.

No evidence here proves a minimal patch set, complete original-success equivalence, a device crash cause or an FPS repair. The next useful benign work is to inspect the callback's post-check lifetime/attachment composition and legitimate render-backend resource/cleanup contracts, without a new diagnostic build.
