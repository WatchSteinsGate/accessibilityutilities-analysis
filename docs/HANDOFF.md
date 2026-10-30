# Continuation handoff

## Goal and constraints

Investigate the original general startup-to-presentation path beyond the UI-only trace, compare supplied original and R03, and retain enough evidence and context for continuation. The user reports overlay/menu FPS and touch response degrade even when game FPS remains high; degradation can persist with the menu closed. Gyro was historically reported smooth. These are user reports, not measurements established by these tests.

The user prefers concrete local tracing and verification over reassurance and does not want another diagnostic-build/capture cycle. Continue from existing material. Do not describe a scoped emulator pass as an end-to-end device result.

## Historical sequence

1. Earlier patch-integrity work identified multiple revisions and changes beyond an isolated UI edit. R01 did not resolve the reported issue; no R02/R03 device performance fix was established.
2. UI tracing examined ownership/attachment, event queuing, collection, and presentation boundaries. One historical ownership candidate addressed a modeled local mismatch, not restoration of the original whole-system success path. No candidate or installer is distributed here.
3. Whole-system expansion indexed startup roots, lifecycle/epoch handling, coalesced background requests, result/state processing, activation/callbacks, UI/data collection, rendering, queued input, and recovery. It produced scoped tests and an explicit unresolved-coverage ledger; it did not finish all paths.
4. Lifecycle continuation added 144 cases for attachment, recognizer reuse/coexistence, shortcut signaling, layout ordering, and size-sync scheduling.
5. Resize continuation added 150 cases for geometry, numerical edge behavior, button cache/failure/clamp behavior, and one-level staged reentry.
6. Repository packaging removed historical path dependencies from the five benign continuation scripts. Fresh local results are retained separately from historical records. No binary was edited or installed during these continuation/packaging passes.

7. Cancellation/render/shortcut continuation added 232 scoped cases, extending into sequential cancellation, lifecycle queue drain, frame failures/recovery, immediate shortcut consumers and bounded cleanup tails.
8. Attachment/factory/completion continuation added 210 cases, including post-admission attachment, native singleton reuse, completion capture helpers and cache-admission guards. Nine portable scripts were rerun successfully with pinned dependencies; the original five suites remain unchanged.

9. Scheduling continuation adds 64 cases: native observer registration, notification routing and bounded constructor queue/block excerpts. Main-queue operands narrow the interleaving hypothesis; reachable reentry/off-main writers remain unresolved. See [scheduling report](reports/LIFECYCLE-SCHEDULING.md).

## Conclusions to carry forward

- Lifecycle readiness depends on application state and notifications; do not equate it with a license/server success flag.
- Startup/presentation is a graph, not one universal success branch. Backend success and complete runtime behavior remain unverified.
- Overlay construction and later attachment do not necessarily select the same parent across revisions. A modeled ownership/attachment mismatch is evidence of a local discrepancy, not measured continuous reparenting or an FPS cause.
- Input events are queued rather than represented solely by one overwritten byte. Collection occurs before later visual decisions; a closed menu does not prove no overlay work.
- Cached window recognizers are reused on ordinary attachment changes. Same-window calls avoid remove/add in the modeled lifecycle cases.
- The original size-sync body is unchanged in R03, but R03's caller appends another layout helper, so the whole layout path is not equivalent.
- Off-main size-sync scheduling precedes its main-thread busy guard. Multiple modeled calls enqueue separately; real queue accumulation has not been established.
- Same-owner button reuse avoids allocation but still performs center/front work. Synthetic owner changes and allocation failures reveal cache boundaries, not actual device occurrence.
- The original resize guard suppresses nested original setters in staged tests. It does not cover the appended button helper. Real UIKit-triggered recursion, exceptions, races, and cost remain unknown.
- Local synthetic zero/NaN/infinite geometry reveals setter/publication differences; it is not evidence that such values caused the user's slowdown.

## Latest findings

- Lifecycle observers request the main operation queue; constructor and coalesced reevaluation blocks use the imported main dispatch queue. This supports ordinary serialization, not actual runtime delivery or proof against reentry. The latest 64-case suite passed; prior suites were not rerun in this pass.

- Original queued callbacks reject a stale captured generation at admission. Already-admitted callbacks can still reach attachment after a staged native cancellation; runtime reachability of that interleaving is **not established**.
- Native singleton reuse avoids repeated allocation in the tested once sequence but still performs geometry and drawing-reference updates. Reuse does not refresh the first initializer-published shortcut control pointer when later calls pass different symbolic pointers; actual changed inputs/dangling lifetime are not established.
- Immediate shortcut-to-menu-draw consumption is traced. Repeated qualifying callbacks set the byte to 1, not a direct toggle. Pointee lifetime and other writers remain open.
- Synthetic frame resource failures reached normal cleanup/recovery in the scoped model. R03's late guard bounds submission only at its observation point; it does not cancel already performed work or every later state change.
- Native completion helpers strongly capture two buffers and weakly resolve their context twice; copied captures persist until block disposal in the modeled lifecycle. Actual GPU completion/Blocks/ARC behavior is not established.
- Native cache admission rejects nil wrapper/underlying buffer and lengths above 16 MiB; accepted cases stop before locking/insertion. This is not the full cache policy.

## Next work, in order

1. **Reachable scheduling/reentry:** queue operands are now recovered. Trace synchronous constructor callees and remaining lifecycle wrapper/initializer caller contexts for a concrete reentry/off-main writer route; preserve normal main-queue serialization rather than assuming a race from staged mutation.
2. **Control-pointer lifetime:** establish its actual producer/owner, caller invariants and other pointee writers. Do not infer a dangling pointer solely from singleton reuse.
3. **Backend draw and completion composition:** extend native draw-loop/resource-failure analysis and completion registration/copy contracts. GPU delivery and command-buffer error outcomes remain unverified.
4. **Accepted cache body:** trace insertion, enumeration, eviction and reuse under legitimate state. The entry-size guard is only a prefix.
5. **Broader success graph:** resolve secondary setup-word producer, workers and indirect runtime targets; keep unresolved genuine backend/security transitions clearly outside the validated local scope.

The earlier cancellation, resource cleanup and immediate shortcut-consumer entries are now **partially advanced**, not universally closed. Detailed next actions and evidence boundaries are maintained in [NEXT-STEPS.md](NEXT-STEPS.md).

Before any new work, confirm the two input hashes. Retain per-case assumptions and failures. Do not build or distribute a modified release, claim complete original equivalence, or claim a fixed FPS/touch problem.

## Existing private workspace record

The fuller historical session context remains in the user's Notion workspace, titled “AccessibilityUtilities — Session context, patch audit & whole-system trace.” This repository is a curated continuation, not a complete export of that page or its private attachments. Deliberate omissions are listed separately. No automatic two-way sync is configured.
