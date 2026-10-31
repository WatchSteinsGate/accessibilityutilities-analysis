# Bubble callback delivery, control-byte writer and pan consumption

## Provenance and question

- Date: 2026-10-31. Agent: Notion AI, local read-only ARM64 analysis and connected GitHub tools.
- Starting revision: `df489c523834b4bc21c51c2a240cf8c2464f23db`, `main`, clean complete checkout.
- Question: after the [previous native normal return](OVERLAY-NORMAL-RETURN-MENU-INI.md), what does the requested existing R03 bubble callback actually do under explicit UI providers? Does its registered action expose another concrete control-pointer writer?
- Original SHA-256: `b685c0f98b15597fb9eabb6d09758a2637246198a1af24a044c2010953fb80ab`.
- R03 SHA-256: `d1a05ff2d8164ec326898d3d2d9709fb638f85d8550436f8e5d9c845be54b292`.

Downloaded the two existing release archives after the user made the repository public. Archive hashes match the retained release manifest; only the two framework input members were extracted, made read-only and analyzed. No historical archive tool, builder, diagnostic or installer was executed. This is not a new release or an implementation of injected callbacks.

## Work performed

Added **22 R03 native/model records** in [the new suite](../../tests/continuation-k/test_bubble_callbacks.py), retained in [the complete result file](../../results/continuations/continuation-k/bubble-callback-tests.json):

- Eight native initializer/registration/request/manual-install sequences, including main/off-main answers, button allocation failure, pan allocation/init nil, explicit later main-thread delivery, and repeated delivery.
- Five native tap sequences, each with two taps, covering nil control and initial bytes 0, 1, 2 and 255.
- One native singleton/factory/once reuse sequence followed by native install and tap.
- Eight native pan cases covering states 0–5, explicitly missing cached button, and small bounds.

Unlike the earlier button-layout suite, these cases **do not prefill the selector/class caches**. The actual normal-return wrapper and registration helper populate them from cold emulated state. The modeled `class_addMethod` boundary records the existing IMP arguments, and manual callback invocation uses those recorded addresses. Method additions return true in this suite; no real method installation occurs. Prior nil-class/false-add cases remain covered by the unchanged group-j regression.

The real main queue is not run: after native initialization returns, the harness explicitly delivers the recorded install request. Subsequent taps/pans are also explicit invocations, not actual UIKit target/action or gesture delivery.

## Findings and evidence

### Registration/request is not successful installation

The existing registration helper at `0x1016700` records the three native IMPs:

| Selector | Existing R03 IMP |
| --- | --- |
| `v58InstallBubble:` | `0x1016820` |
| `v58TapBubble:` | `0x1016a80` |
| `v58PanBubble:` | `0x1016b60` |

After normal return but before manual delivery, the bubble state at `0x1013780` has registration flag 1, no cached button and no owner. Delivery under a modeled main-thread answer creates/configures the button, connects the tap action, optionally attaches the pan recognizer, attaches the button, and executes the native clamp/front path. Fully provided installation gives flags 15; modeled pan allocation/init nil still attaches the button and gives flags 7. Button nil leaves the registration-only state.

An off-main answer exits without creating a button or requesting a retry from this callback. A later explicit main-thread invocation can proceed; the test does not establish that the app schedules such a second invocation. Repeated same-owner successful installation reuses the cached button; repeated nil button allocation attempts again. This composition advances the old preinitialized-cache helper coverage rather than claiming an entirely new layout implementation.

### A concrete control-byte writer is now executed

The registered native tap body increments its tap counter, loads the pointer from Overlay's published slot `0x1011e20`, and, when nonnil, XORs bit 0 of its first byte. It does **not** normalize the byte to Boolean or unconditionally set it to 1:

| Initial byte | First tap | Second tap |
| --- | --- | --- |
| 0 | 1 | 0 |
| 1 | 0 | 1 |
| 2 | 3 | 2 |
| 255 | 254 | 255 |

Nil pointer still increments the counter but skips the pointee write. This is distinct from the previously traced immediate shortcut producer's set-1 behavior. The test values above are synthetic mapped memory, not observed application state.

Composing actual singleton reuse with this actual writer shows that later factory calls with another mapped control pointer and nil do not refresh the first publication: a subsequent tap writes the **first** mapped control allocation, not the later argument. This connects an executable writer to the earlier reuse finding. It does not prove that actual callers vary their pointer, that the first allocation is freed, or that a dangling pointer exists. Deallocation/replacement and complete writer coverage remain open.

### Pan state gates and translation reset

With a cached button, the native pan body accepts modeled states 1, 2 and 3; 0, 4 and 5 do not consume translation. Accepted cases add translation to the modeled center, call the existing native clamp, reset translation to zero and increment the pan counter. With 320×240 bounds and the synthetic large translation, the resulting center is (288, 32).

For width 63, the native clamp skips the center update, but the calling pan body still resets translation and increments its counter. Thus an accepted callback's counter/reset alone does not prove a position update. With an explicitly cleared cache, the body exits before querying gesture state. These are conditional native contracts, not proof of physical touch behavior or frequency.

## Validation

Python **3.13.15**, Capstone **5.0.7**, Unicorn **2.1.4**.

With authorized `AU_ORIGINAL` and `AU_R03` set:

```bash
python tests/continuation-k/test_bubble_callbacks.py
python tools/run-native-regression.py
python tests/continuation-c/map_scheduling.py
python tests/continuation-d/map_reentry_boundaries.py
python tools/validate-continuation-results.py
python tools/validate-attachment-intake.py
python tools/validate-original-attachments.py
sha256sum -c SHA256SUMS
```

- New 22/22 passed; repeated runs produced byte-identical new records.
- All **23 native/model suites passed**, totaling **1111 generated labels**: 294 base, 795 earlier continuation and 22 new. Every prior suite's record values match the retained historical records after JSON key normalization, including their existing synthetic NaN/Infinity spellings. Historical result files were not overwritten.
- [Reviewed regression summary](../../results/continuations/continuation-k/regression-summary.json) records versions, both input hashes, all suite exit codes, counts and historical-value comparison results. The new file has no earlier retained comparison at the time of that summary.
- Scheduling mapper: six equal ranges and one expected differing range. Startup mapper: ten equal windows and nine selected direct edges per build.
- Complete-checkout continuation record integrity now covers **817 records across a–k**, not a runtime claim. Full repository checksums, inventory, changed-document links and Python syntax checked.
- Input binary SHA-256 values remained unchanged before and after analysis. No exploratory harness failure required broadening an unknown import/selector handler. The older tests already had explicit modeled runtime boundaries; those models were not changed.

## Files and evidence boundaries

Added this report, the group-k suite, complete case records, regression summary and the portable regression runner. Updated navigation, current handoff/next steps, reproduction/provenance, record validator, inventory and root checksums. Prior tests and historical record groups remain intact.

Local raw disassembly, downloaded source archives, extracted binaries, temporary logs, bytecode caches and absolute local input paths are not new Git-tree artifacts. They are either scratch analysis or already-retained original release material. Five bounded native code-window hashes are included in the new result file; raw proprietary instruction dumps are not published.

## Limits and next concrete action

No real Objective-C runtime method installation, ARC lifetime, UIKit reentry, callback delivery, exception, actual main-queue timing, Metal/GPU/backend/device success, physical input or performance result is established. Counts contain repetitions and synthetic states, not unique end-to-end paths. No root cause, ownership/race proof, FPS/touch fix or modified release is claimed.

Next: trace successful native Menu decode/upload and actual Float/Draw texture callbacks, keeping each provider explicit. Separately trace the control allocation's deallocation/replacement and other writers; do not treat the newly identified tap writer as a lifetime proof. Runtime scheduling and backend providers remain unresolved.