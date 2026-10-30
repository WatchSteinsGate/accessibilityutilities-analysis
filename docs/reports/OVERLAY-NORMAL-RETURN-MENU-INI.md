# Overlay normal return, R03 UI registration and Menu INI application

## Scope and provenance

2026-10-30, Notion AI. Starting revision `3c48d6b68e5631bea93b49e1e57733eaf6979403`; follows [size/backend/attachment composition](OVERLAY-SIZE-ATTACHMENT-COMPOSITION.md). Both authorized binary hashes remain unchanged.

**31 new labeled native/model cases:** 12 complete normal-return Overlay caller paths, three actual singleton/once/normal-return reuse sequences, and 16 Menu nonnil-INI apply/reuse cases. Native ready caller paths now execute final cleanup and return, including the existing R03 nonnil return wrapper and its native helpers. They return the supplied receiver in the tested conditions.

This is completion of the native caller's tested normal-return path, **not proof of complete functional GUI initialization**. GUI ABI/context/style/font providers, real ObjC/ARC/Blocks/scheduling, class/selector lookup and method-add outcomes, backend/device-object work, child texture callbacks, Menu readIniConfig and INI integer reads remain modeled. No real runtime methods are installed and no binary is changed.

## Native final return

The prior pre-return stop `0x6854a8` is removed for these cases. Original follows its retain call and normal epilogue. R03 follows its existing branch at `0x6854ec` into `0x1017600`, through native helper `0x1016700` and epilogue `0x1017700`. The result is the same receiver for all/none/missing child-object cases and the tested symbolic class/method-add outcomes.

The original/R03 final-return window remains genuinely unequal, with both hashes retained. Same selected return values do not establish equivalent side effects, ownership or runtime behavior.

### R03 does more than a retain

The existing native R03 wrapper increments its emulated invocation counter, retains the receiver through a modeled ARC boundary, asks for its class and, when that symbolic class is nonnil, attempts four touch-method additions. It accumulates modeled method-add return bits into its native status word.

Its native helper resolves a 34-selector/six-class cache, queries the receiver class and attempts three bubble-method additions. With a nonnil class, it sets its local registration-attempt flag and sends `performSelectorOnMainThread:withObject:waitUntilDone:` for `v58InstallBubble:`, nil object, wait=false. The request is recorded, **not executed**. No claim is made about when the real runtime would execute it.

Seven modeled method-add calls returning zero do not suppress that install request. Zero is not classified as an installation failure: a method may already exist. Synthetic nil class skips additions/request but does not prevent returning the receiver. The nil-class case is a boundary test, not evidence of a real ObjC object lacking a class.

No patch builder or hook payload is produced. Existing native code executes in emulated memory; class-add and lookup imports only record symbolic operations.

### Actual successful-once composition bounds repeated initialization

The real Overlay factory and once block now compose with the normal-return caller. Three sequential factory calls return the same receiver; native singleton/token state is populated and initialization runs once under modeled completed-once semantics. Changed later control arguments do not replace the first raw control publication. R03 return-wrapper counter remains one in these sequences, not one per later factory call.

Newly reached factory frame/bounds/autoresizing callbacks are explicitly modeled. Factory frame arguments are seeded as 0,0,320,240, consistent with the synthetic geometry providers. Real UIKit frame application and dispatch_once concurrency are not tested.

## Menu nonnil-INI application

The actual Menu setter now executes its nonnil INI guard/read/apply route, using a preinitialized native style-state object. Native constructor guard is seeded complete; constructor/guard acquisition is not tested. The preceding readIniConfig callback is modeled without state mutation, so the tested state inputs are explicit conditions after that boundary, not a reconstruction of the callback.

Actual native wrappers obtain defaults 2 and 3, then modeled integer reads supply `menuAppearance.style` and `menuAppearance.enabledStyles`. Native `0x617c8c` and its helper chain apply normalization:

- Enabled mask is ANDed with 3; a zero result becomes 3.
- A requested style is accepted only if its native style bit belongs to that mask. Otherwise default style 2 is used when enabled; the fallback is the first enabled style.
- Selected/current fields are updated, applied flag set, dirty flag cleared and transition field assigned -1 in the tested branch.

Seven style/mask pairs per build cover accepted, disabled, unsupported, negative and zero inputs. Each case calls the native Menu setter twice: after first application, the native applied flag prevents further integer reads in the second call. An initially applied case skips both reads and preserves seeded state on both calls. Both calls still reach the modeled readIniConfig callback; the native guard does not prove that callback is side-effect free in the real app.

No actual INI file is opened or written. Cached texture state bypasses successful decode/upload work; that work remains unresolved. The global Overlay reference is published before these checks as in the preceding pass.

## Evidence and validation

- [Suite](../../tests/continuation-j/test_overlay_return_menu.py)
- [All 31 labeled records and hashes](../../results/continuations/continuation-j/overlay-return-menu-tests.json)

With authorized AU_ORIGINAL and AU_R03 configured:

```bash
python tests/continuation-j/test_overlay_return_menu.py
python tests/continuation-i/test_overlay_attachment.py
python tools/validate-continuation-results.py --group continuation-j
```

Python 3.13.15 / Capstone 5.0.7 / Unicorn 2.1.4: **31/31 passed**. Of three selected comparison windows, two are equal and the known final-return window differs. The previous **30-case composition suite was rerun with byte-identical records**; older native suites were not rerun. Dependencies were restored at their pinned versions in the current workspace environment; no shared harness source changed.

Initial normal-return factory tests failed closed at newly reached setFrame and setAutoresizingMask messages. Explicit geometry/autoresizing boundaries were added only to the new test model; no unknown-import bypass or blanket message handler was added.

Generated output defaults to results/generated/continuation-j/, overridden by AU_RESULTS. New-group integrity, Python/JSON, changed links, present-file hashes and input identities checked. This is a partial checkout, not a full-repository checksum run or full 795-record continuation validation. Totals: **795 continuation + 294 earlier = 1089 labeled records**, including paired builds and repeated calls, not unique end-to-end paths.

## Remaining work

Execute the requested bubble-install callback under explicit UI providers, then trace successful Menu texture decode/upload and actual Float/Draw texture callbacks. Control-state replacement/deallocation/pointee writers, real GUI/font/device-object providers, exceptions, actual scheduling and runtime performance remain unresolved. Native caller normal-return completion does not settle them. No real GPU/backend/device success, lifetime/race proof, root cause, FPS/touch fix or modified release is claimed.
