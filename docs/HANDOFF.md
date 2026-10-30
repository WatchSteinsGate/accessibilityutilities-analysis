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

## Latest continuation — startup registration and direct veneers

Starting at `62d05c2`, startup initializer `0x43850` is recovered enqueueing block invoke `0x4388c` on the imported main queue. That callback reaches producer `0x438b8` and a once block invoking observer registration `0x7aa4c`. The previously unresolved direct suspend/transition wrappers belong to the known transition/background routes and add no queue hop. Custom synchronous ObjC implementations, indirect callers and other state writers remain unresolved; staged cancellation is still not a proven runtime race.

Added 58 new native/model cases, bringing stored labeled cases to 858 (564 continuation + 294 earlier), not unique paths. Existing 64 scheduling and 110 attachment cases passed fresh reruns; other suites were not rerun. See [the focused report](reports/STARTUP-REENTRY-BOUNDARIES.md), [next steps](NEXT-STEPS.md) and [attachment intake](ATTACHMENT-INTAKE.md). No input binary edited, device performance fix claimed or modified release built.

## Factory/control-state follow-up

See [focused report](reports/FACTORY-CONTROL-PROVENANCE.md): 54 new passing scoped native/model cases. Four native factories and once blocks composed; FloatView/FieldView initializer normal/nil-return bodies executed, DrawWindow stopped at control publication, MenuWindow initializer still modeled. A concrete producer excerpt allocates 256 bytes and publishes slot `0x1011b68`; repeated/existing-slot execution skips allocation. Deallocation/replacement and real pointee lifetime remain open. Twelve selected windows match, one producer window differs. Stored totals: 618 continuation + 294 earlier = 912 labeled cases, not end-to-end paths. No older native suites rerun or device/performance fix claimed.

## Complete Draw/Menu initializer follow-up

[Report](reports/INITIALIZER-EFFECTS.md): 46 additional scoped cases, complete Draw/Menu native initializer normal/false/nil-return bodies and native once composition. File creation false is not an early exit; Menu config effects precede inherited init. Draw setup/control publication/size reset also occur before returning modeled inherited nil. Foundation/INI/ARC/once/inherited runtime remain modeled. Prior factory 54-case records are byte-identical after main-guard refactor. Totals: 664 continuation + 294 earlier = 958 labeled records, not end-to-end paths. Overlay initialization and real control-state ownership/writers remain open.

## Overlay resource guards and failed singleton reuse

[Report](reports/OVERLAY-RESOURCE-GUARDS.md), 34 additional labeled cases: five early failure routes, ready prefix and native factory/once failure-then-provider-recovery. Completed-once nil remains nil in three-call sequences. Control publication/property assignment precedes inherited init. Queue/loader failures follow delegate assignment, without a modeled lifetime conclusion. Successful prefix stops before `0x6849f8`; no backend success. Twelve equal windows and one genuinely unequal return tail are preserved; inherited-nil reaches the existing R03 trampoline with nil. Totals 698 continuation + 294 earlier = 992 labeled records. Only group g rerun/validated this pass. Next: remaining Overlay setup and control-state lifetime/writers, not a claimed performance fix.

## Configuration, font guards and backend return contracts

[Report](reports/OVERLAY-CONFIG-FONTS-BACKEND.md): 36 additional labeled cases (18 path/IO, 10 font guards, 8 standalone backend wrappers). Documents/imgui.ini path construction and IO writes now execute natively beyond the old stop. Failed file creation or UTF8/duplicate nil continues at this stage. First and third font results gate nil return; intermediate merge nil does not. Backend normal-return true/flags are not device-object-success evidence: modeled zero subordinate results are not propagated. Actual context/font/backend providers remain modeled; ready fonts stop before size synchronization. Existing 34 guard records rerun byte-identical after import-safe refactor. Totals 734 continuation + 294 earlier = 1028 labels, not unique paths. Next: size/attachment/menu-backreference composition and ownership/writers; no actual backend/device success or performance diagnosis.

## Size/backend/attachment composition

[Report](reports/OVERLAY-SIZE-ATTACHMENT-COMPOSITION.md): 30 new records, 24 composed native caller paths plus six native Menu setter normal-return guard cases. Ready paths stop before final cleanup/retain at 0x6854a8. Main-thread size publication precedes backend/attachment; forced off-main deferral is conditional, not a proven startup route or race. Float/Draw callbacks receive the device; Menu receives Overlay. Native Menu global strong publication remains after nil-device/cache/decode-false guards; readIniConfig modeled and nil INI skips later apply. Prior 34/36 regressions byte-identical. Totals 764 continuation + 294 earlier = 1058 labels. Next: nonnil R03 return tail, successful Menu texture/non-null INI, child callbacks and ownership/writers; no real GPU/device success or performance fix.

## Native normal return and Menu INI apply

[Report](reports/OVERLAY-NORMAL-RETURN-MENU-INI.md): 31 new labels (12 normal-return caller paths, three factory/once reuse sequences, 16 Menu nonnil-INI apply/reuse cases). Native original/R03 caller paths return the receiver with explicit providers; R03 wrapper/helper now executed rather than skipped. It attempts touch/bubble method registration and requests install callback; modeled runtime adds/requests are not executed. Native Menu normalizes enabled mask/style and its applied flag prevents repeated integer reads under a no-op readIniConfig boundary. Prior 30 composition records rerun byte-identical. Totals 795 continuation + 294 earlier = 1089 labels. Native caller normal return is not complete functional initialization. Next: requested callback, successful texture paths, ownership/writers and real runtime validation; no root cause or performance fix.
