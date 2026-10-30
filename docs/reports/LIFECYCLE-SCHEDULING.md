# Lifecycle queue constraints and callback routing

## Provenance and question

- Date: 2026-10-30. Agent: Notion AI, using local read-only native analysis and connected GitHub tools.
- Starting revision: `ba6c9ff8340be1a766996f06ea63caa2d48f9a03`.
- Question: do the known notification and constructor scheduling routes establish a reachable lifecycle change after constructor admission but before attachment?
- Original SHA-256: `b685c0f98b15597fb9eabb6d09758a2637246198a1af24a044c2010953fb80ab`.
- R03 SHA-256: `d1a05ff2d8164ec326898d3d2d9709fb638f85d8550436f8e5d9c845be54b292`.

## Finding: main-queue routes constrain the staged interleaving

The native observer initializer at `0x7aa4c` obtains `mainQueue` for every recovered `addObserverForName:object:queue:usingBlock:` registration. Four application notification registrations are unconditional. Four scene notification registrations are added when the modeled scene-class lookup succeeds. All use a nil object filter.

The constructor producer loads the imported `__dispatch_main_q` pointer at `0xfd82e8`, preserves it in its frame, and passes it to `dispatch_async` through `0x1046a4` / `0x104694`. The constructed block invokes `0x76944` and captures the supplied generation at block offset 32. This pass executes only the queue-load prologue and block-building excerpt, with the intervening worker/backend body **skipped** and the generation explicitly seeded. It does not execute or authenticate a backend success.

These operands support the normal main-thread serialization constraint, under the external runtime contract for main operation/dispatch queues. They are not evidence of actual queue delivery or a measured total ordering. The model uses distinct symbolic operation-queue and dispatch-queue objects, not an assertion that they are one object.

**Conclusion:** merely queuing these lifecycle notifications does not establish that they can interrupt an already-running constructor. The previous staged cancellation result remains a conditional native behavior: attachment can continue after an injected post-admission cancellation, but a reachable runtime/reentrant route for that injection has not been established. Neither a real race nor universal race safety is proven.

## Native routing recovered

| Registration | Block invoke | Native route |
| --- | --- | --- |
| UIApplicationWillResignActiveNotification | `0x7b114` | transition boundary `0x7b188(false)` |
| UIApplicationDidBecomeActiveNotification | `0x7b77c` | transition boundary `0x7b188(true)` |
| UIApplicationDidEnterBackgroundNotification | `0x7b7f0` | wrappers to transition boundary `0x7b188(false)` |
| UIApplicationWillEnterForegroundNotification | `0x7b864` | coalescing enqueue `0x7b8d0` |
| UISceneDidActivate / WillDeactivate / DidEnterBackground / DidDisconnect notifications | `0x7b938` | coalescing enqueue `0x7b8d0` |

`0x7b8d0` sets pending byte `0x1010a58` and dispatches block invoke `0x7ba04` to the imported main dispatch queue only when the byte was clear. An already-set byte suppresses another enqueue in these sequential cases. The callback payload is retained/released through modeled ownership boundaries but does not change the tested routing. This is not a concurrent atomicity test or notification-payload lifetime proof.

The initializer computes readiness from `applicationState == 0`; states 1 and 2 reach a recorded initial-suspend boundary. The suspend implementation and complete `0x7b188` transition body are not executed by this new suite. Earlier tests retain their own distinct scope.

## Evidence and coverage

- [Runnable tests](../../tests/continuation-c/test_scheduling.py): **64 labeled cases**, 32 per supplied build.
  - 12 observer-initialization cases: 3 application states × scene-class availability × 2 builds; 72 total registration observations.
  - 40 notification-routing cases: 5 callback bodies × pending 0/1 × nil/non-nil symbolic payload × 2 builds.
  - 12 producer excerpts: 3 seeded generations × 2 symbolic main-queue bindings × 2 builds.
- [Complete case records](../../results/continuations/continuation-c/scheduling-tests.json).
- [Static mapping script](../../tests/continuation-c/map_scheduling.py) and [mapping output](../../results/continuations/continuation-c/scheduling-map.json): import identities, seven bounded byte comparisons, nine direct immediate B/BL references to selected lifecycle targets, and direct branches in the constructor body.
- Six selected queue/callback/excerpt ranges are byte-identical. The adjacent resume-mutator range is deliberately recorded as **different**: R03 changes instructions at `0x7b9d4` and `0x7b9d8`. This is an expected revision discrepancy, not a scheduling-test failure or a new patch proposal.

The direct-reference map covers aligned immediate B/BL instructions in original `__text` only. It is not an exhaustive caller/indirect-edge index. Wrapper callers, observer-initializer caller thread, other state writers, Objective-C dispatch, custom initializer behavior and nested runtime delivery remain unresolved. A body-level direct-branch list cannot establish the transitive absence of run-loop pumping or reentry.

## Validation and corrections

Run from the repository root with Python 3.13, Capstone **5.0.7** and Unicorn **2.1.4**, after setting authorized `AU_ORIGINAL` and `AU_R03` as in [reproduction](../CONTINUATION-REPRODUCTION.md):

```bash
export AU_RESULTS="$PWD/results/generated/continuation-c"
python tests/continuation-c/test_scheduling.py
python tests/continuation-c/map_scheduling.py
python tools/validate-continuation-results.py
```

- New native/model suite: 64/64 expected assertions passed. Existing 442 continuation records were reconstructed/validated, **not** rerun. Existing 294 lifecycle/resize cases were also not rerun.
- A preliminary class-name resolver incorrectly followed an unresolved raw-image class pointer and failed; the final harness binds class references symbolically, while the map resolves relevant pointer imports through Mach-O indirect-symbol metadata. It does not dereference unresolved class metadata or fabricate recovered class identities.
- Initial broad equality assertion incorrectly included the changed resume mutator. It failed; boundaries were corrected, the resume difference was retained explicitly, and the final map passed with six equal ranges and one expected unequal range. No input was edited.
- Both input SHA-256 identities were checked before analysis and after final runs. Source syntax, local documentation links and staged-file checksums were checked. This workspace is a partial checkout: no claim of a full-repository `sha256sum -c` run is made.

## Files, omissions and next action

This report, two portable scripts and two structured result files are new; handoff, next steps, worklog, README, provenance/reproduction/omissions, validator, inventory and checksums are updated. The new scripts reuse the existing `tests/continuation-b/` parser/emulator without changing it. No duplicate helper tree is needed.

Local raw disassembly, broad reference scratch files and binaries are not uploaded. The reviewed metadata and complete modeled records preserve the bounded result under [the omissions policy](../OMISSIONS.md). No archive, diagnostic build, installer or operational security-bypass implementation is added.

Next: bound synchronous callees between constructor admission and `addSubview:` and follow remaining lifecycle wrapper/initializer caller contexts. A concrete reentry/off-main writer route with its scheduling provenance is required to upgrade the conditional staged-cancellation finding. If none is found in that bounded scope, record the negative result and move to actual shortcut control-pointer producer/owner lifetime. GPU delivery, complete cache policy, other workers, device FPS and physical touch latency remain open.
