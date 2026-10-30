# Startup registration and synchronous reentry boundaries

## Provenance and bounded question

- Date: 2026-10-30. Agent: Notion AI, connected GitHub tools and local read-only ARM64 analysis.
- Starting revision: `62d05c2eb1615baef92d0446e5e70c92a3c72805`.
- Question: where does lifecycle observer registration originate, do the remaining direct wrapper callers introduce another scheduling route, and which constructor synchronous boundaries remain unresolved?
- Supplied original SHA-256: `b685c0f98b15597fb9eabb6d09758a2637246198a1af24a044c2010953fb80ab`.
- R03 SHA-256: `d1a05ff2d8164ec326898d3d2d9709fb638f85d8550436f8e5d9c845be54b292`.

## Findings

### 1. Lifecycle registration has a recovered startup main-queue route

The image's `__mod_init_func` table contains startup initializer `0x43850`. Native execution reaches a main-queue getter chain (`0xf6ce4` → `0xf6ccc`) that loads the imported main dispatch pointer at `0xfd82e8`, then passes global block `0xfd99d0` to `dispatch_async`. The block invokes `0x4388c`.

That callback synchronously calls registration producer `0x438b8` before the separate `0x438dc` secondary-setup boundary. The producer supplies once token `0x1010a50` and global block `0xfd9cd0` to native forwarding helpers ending at imported `dispatch_once`. The registration block's invoke pointer is `0x7aa4c`, the observer body exercised in the prior scheduling suite.

The new tests execute the initializer and callback/helper routing with modeled enqueue/once boundaries; they do not drain a real queue, execute the observer body inside once, or claim actual libdispatch/ARC behavior. Initializer main-queue provenance is now recovered for this route. Other indirect invocations or state writers remain unproven, so this is not universal thread-affinity proof.

### 2. Remaining direct lifecycle veneers fold into the known graph

Two previously unresolved wrapper chains are now followed:

- Transition body `0x7b188`, call site `0x7b230`, reaches suspend through `0x10792c` → `0x10791c` → `0x7b0b8`.
- Background callback `0x7b7f0`, call site `0x7b820`, reaches transition through `0x107c08` → `0x107bf4` → `0x7b188`.

These small forwarding bodies add no queue dispatch or thread switch. Suspend wrappers preserve the argument; transition wrappers mask it to the low bit. Thirty-two native forwarding cases verify those argument contracts in both builds, with terminal transition/suspend bodies recorded rather than executed by these cases.

The two-build immediate B/BL index contains exactly nine edges to the ten declared routing targets. This closes these direct wrapper provenance questions, not every possible caller. In particular, an empty direct-call list for `0x7aa4c` is expected because the recovered path uses a block invoke pointer; it is not evidence that registration is unreachable.

### 3. Constructor synchronous boundaries are narrower, not eliminated

Twelve new admitted-callback cases traverse the native Objective-C forwarding veneers `0x105cec`/`0x105cdc`, `0x105d0c`/`0x105cfc`, `0x105d2c`/`0x105d1c` and `0x105d4c`/`0x105d3c`. They forward to `objc_msgSend`; the local rectangle helper `0x76e20` only copies four scalar bit patterns in the six tested rectangle cases. Those native veneers do not themselves introduce queue delivery.

Actual custom factory/initializer/getter/setter implementations and UIKit are still modeled. They cannot be declared non-reentrant from these tests. No staged lifecycle mutation is injected in the twelve new constructor cases; absence of a lifecycle callback in a non-reentrant stub does not prove absence at runtime.

The constructor reads control-pointer slot `0x1011b68` and forwards its current value to the three `sharedInstance:` factories and the overlay `sharedInstance:::::` factory. The new tests vary the slot synthetically to verify this argument flow, not to establish real pointer changes. The slot's producer, pointee ownership/lifetime and remaining writers are still open; the singleton's old-pointer retention must not be called a dangling pointer solely from these seeded inputs.

### 4. Net result for the race hypothesis

Known startup and notification routes support ordinary main-thread serialization. The direct veneers examined here do not supply an independent off-main writer or a reachable post-admission interruption. The earlier staged cancellation finding remains conditional. **No real race, absence of all reentry, crash cause or FPS fix is established.** Next work should enter the actual custom synchronous factory/initializer callees, retaining indirect-call uncertainty, before upgrading the race hypothesis.

## Evidence and validation

- [Native boundary suite](../../tests/continuation-d/test_reentry_boundaries.py): **58 new labeled cases**, 29 per build: 4 startup enqueues, 4 callback/once-routing cases, 32 forwarding cases, 12 constructor message traces, 6 rectangle-helper cases. Cases include paired builds, sequential calls and synthetic arguments, not independent end-to-end paths.
- [Complete partitioned records](../../results/continuations/continuation-d/reentry-boundary-tests.json); all records retained with relative part hashes.
- [Static mapper](../../tests/continuation-d/map_reentry_boundaries.py) and [map](../../results/continuations/continuation-d/reentry-boundary-map.json): ten equal code/data windows, two block descriptors, startup table membership and nine immediate direct edges per build.
- Fresh regression reruns: existing scheduling suite **64/64**, existing attachment suite **110/110**. Existing scheduling mapper also passed. Other suites were not rerun.
- Python 3.13.15, Capstone 5.0.7, Unicorn 2.1.4. [Run summary](../../results/continuations/continuation-d/summary.json).

From the root, with authorized `AU_ORIGINAL` and `AU_R03` set:

```bash
python tests/continuation-c/test_scheduling.py
python tests/continuation-c/map_scheduling.py
python tests/continuation-b/test_attachment.py
python tests/continuation-d/test_reentry_boundaries.py
python tests/continuation-d/map_reentry_boundaries.py
python tools/validate-continuation-results.py --group continuation-d
python tools/validate-attachment-intake.py
```

`test_attachment.py` was refactored only to put its existing executable suite behind `main()` so the new suite can reuse its model without rerunning tests on import. Its 110-case regression passes and generated record contents match the prior run in this session. No native input changed. Hashes were checked before and after analysis.

## Corrections and limits

A preliminary search for direct callers/address construction of `0x7aa4c` found none. Following its pointer in `__const` instead recovered the global block and actual producer; no direct-call absence was turned into an unreachable-code claim. A broad data-pointer scratch scan then hit an unmapped zero-fill section and stopped; its partial scan is not used as exhaustive pointer evidence. Final checks use explicit file-backed block/range/table reads and bounded immediate branch indices.

This is a partial local repository checkout. New 58-record integrity validation and all present staged-file hashes/changed-document links were checked, not a full 564-record validator run or whole-repository checksum run. The validator now supports explicit `--group` validation; default requires all 564 continuation records (506 previous + 58 new). Including the earlier 294 lifecycle/resize records gives 858 stored labeled cases, not 858 unique paths. Source-report copies and regression reruns are not counted as new cases.

Real dispatch/once concurrency, ObjC/ARC/Blocks, UIKit exceptions/reentry, backend transitions, Metal/GPU completion, device FPS and physical touch latency are unverified. No patch, installer or modified release was built. Local raw instruction scratch files and binaries are not published.

## Files and next action

Added this report, two portable scripts, complete new records/static metadata, source intake manifest and exact supplied resize source report. Updated navigation, handoff/next steps, worklog, reproduction/provenance/omissions, validator, inventory and checksums. See [attachment intake](../ATTACHMENT-INTAKE.md) for all nine supplied occurrences and explicit omissions.

Next: follow actual `MenuWindow`/`DrawWindow`/`FloatView`/`FieldView` and `OverlayView` factory/initializer callees between admission and attachment, focusing on synchronous delivery/reentry and state-writer provenance. Then resolve the control slot's real producer/owner rather than inventing pointer changes. Keep cache/backend/other workers as separate unresolved questions.
