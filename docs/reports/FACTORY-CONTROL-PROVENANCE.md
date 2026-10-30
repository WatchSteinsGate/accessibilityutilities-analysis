# Factory composition and control-state publication

## Provenance and question

2026-10-30; Notion AI, local read-only ARM64 execution. Starting published revision: `cb50b04337c2174f01bd4a3faabfcb4f6e755cc1`. Continue beyond constructor veneers into actual singleton factories/initializers and identify the producer of the control slot. Original/R03 SHA-256 identities remain unchanged from [the handoff](../HANDOFF.md).

## Findings

1. **Four native singleton factories and their once blocks are composed.** DrawWindow, FloatView, FieldView and MenuWindow allocate at most once in the modeled completed-once sequence. Three sequential calls with synthetically changed control arguments return the first singleton; forced allocation/initialization failure leaves the completed singleton nil and does not retry. Real libdispatch concurrency/throw behavior is not exercised. MenuWindow's initializer remains a return-value model, not an executed body.
2. **FloatView and FieldView initializer normal/nil-return bodies now execute natively.** Inherited initialization, ARC and UIKit responses remain modeled. FieldView skips later UI configuration if inherited initialization returns nil; missing backing child suppresses messaging to that nil child. FloatView publishes its supplied raw control pointer before inherited initialization, including the modeled nil-return case.
3. **DrawWindow's native prefix publishes the control argument after inherited initialization even when the modeled inherited return is nil.** Execution stops at `0x10c2c`, before its remaining setup helper; that remainder is not validated. These publication observations do not establish dangling lifetimes or real allocation failures.
4. **The constructor's control slot has a concrete allocation/publication source.** The bounded producer excerpt `0x70e68` → `0x71008` checks slot `0x1011b68`, requests **256 bytes** through native wrappers `0x1037b8`/`0x1037a8` ending at imported `__Znwm`, initializes selected fields, and publishes the result at `0x70fb0`. If the slot is already nonnil, this excerpt skips allocation/initialization; a second sequential invocation reuses it. Allocation and four subobject-construction boundaries are modeled. The enclosing producer/backend is deliberately not executed: reaching this local excerpt is not genuine backend-success evidence.
5. **The selected producer excerpt differs between original and R03.** The tested allocation/reuse/publication assertions pass in both; that does not make the initialized states or complete producer equivalent. Of thirteen compared windows, twelve match and the producer window is explicitly retained as unequal with both hashes.

The published slot therefore is not demonstrated to point to a constructor-stack local: the recovered producer uses an allocation import. Its complete ownership/deallocation/replacement lifetime remains unresolved. No actual changed-pointer event, use-after-free, reachable lifecycle interruption or device FPS/touch cause is established.

## Evidence and reproduction

- [Portable native/model suite](../../tests/continuation-e/test_factories.py).
- [All 54 records and thirteen window comparisons](../../results/continuations/continuation-e/factory-tests.json): 24 factory sequences, 16 FloatView/DrawWindow initializer cases, 8 FieldView initializer cases and 6 producer-excerpt cases. Paired builds, repeated calls and synthetic faults are not independent end-to-end paths.
- Python 3.13.15, Capstone 5.0.7, Unicorn 2.1.4. **54/54 passed**, twelve equal windows plus one expected unequal window. No older native suite was rerun in this pass.

With authorized `AU_ORIGINAL` / `AU_R03` set:

```bash
python tests/continuation-e/test_factories.py
python tools/validate-continuation-results.py --group continuation-e
```

The default output is ignored `results/generated/continuation-e/`; `AU_RESULTS` overrides it. Input hashes are checked by the shared loader before execution and were checked again afterward. The new 54-record group, Python syntax, changed-document links and every present publication-file checksum were checked. This remains a partial checkout: no full 618-record validator or whole-repository checksum run. Continuation records now total 618; adding the earlier 294 gives 912 stored labeled cases, not unique paths.

## Harness corrections and limits

An initial attempt to nest Unicorn runs inside active import hooks exhausted its bound at a forwarding return. Replaced it with an explicit yield/pause–run–restore–resume driver: child native execution begins only after the parent emulator call returns to Python. This models sequential call composition, not runtime reentry. A broad code-equality assertion also failed on the producer excerpt; the final suite asserts/preserves that inequality rather than hiding it or claiming whole-producer equivalence.

Real ObjC/ARC/Blocks, allocation/once exceptions and concurrency, UIKit behavior, MenuWindow initialization, DrawWindow setup after the stop, most of OverlayView initialization, other state writers, deallocation and genuine backend transitions remain unexecuted/unresolved. No binary edited, installable release built or device timing measured. Raw disassembly and the broad exploratory reference list remain local; only reviewed scripts/records are published.

## Next concrete action

Follow control-state deallocation/replacement and pointee writers to establish lifetime. Continue the actual MenuWindow/OverlayView initializer and DrawWindow remainder for synchronous callbacks or state writes; do not infer absence of reentry from stubbed UIKit. Keep the main-queue serialization result and conditional nature of the staged-cancellation hypothesis intact.
