# Overlay size, backend and attachment composition

## Scope and provenance

2026-10-30, Notion AI. Starts at `8889c84899a5dafb5f1addc94d466fad8eda540d`; continues [configuration/font/backend contracts](OVERLAY-CONFIG-FONTS-BACKEND.md). Authorized original/R03 inputs remain unchanged.

**30 new native/model records:** 24 composed caller paths and six standalone Menu setter guard cases. The composed paths begin at the actual Overlay initializer with resource/font-ready providers, execute native size synchronization and native backend wrappers, then exercise selector-gated child/Menu calls. They stop at `0x6854a8`, before final cleanup/retain/return. **No successful full initializer return or real GPU/device execution is claimed.**

GUI ABI/context creation, style, font-add providers, child texture callbacks, Menu `readIniConfig`, backend registration/device-object work, Foundation/ObjC/ARC/Blocks/queues and allocation remain modeled. Selected native property methods, geometry math and display-size stores execute. Six standalone Menu cases execute its full normal-return body only with a nil INI pointer and texture guard paths; the successful decode/upload route is not executed.

## Findings

### Size synchronization is composed with the actual caller

On the modeled main thread, native `syncOverlaySize` (`0x6855c0`) reaches screen `nativeScale`, bounds and drawable-size providers. With modeled 320-by-240 bounds and scale 2, native calculations request drawable size 640-by-480, update content scale to 2 and publish IO display size 640-by-480. The actual synchronization flag getter/setter execute. These inputs are synthetic and do not measure a device's dimensions, display latency or rendering throughput.

This size call precedes the style boundary, native backend initializer/helper and the selected child/Menu calls. Native backend wrappers from the previous standalone pass are now part of this caller composition, with their lower-level providers still modeled.

### Forced off-main invocation defers size work but not the rest of this caller

The native off-main route constructs a block and reaches the actual dispatch forwarding wrappers. The modeled queue copies its capture and defers execution. Backend setup and eligible child/Menu calls reach the caller stop while IO display size remains zero in the seeded model. Manually invoking the captured native block `0x685b98` on the modeled main thread then runs native size synchronization and publishes 640-by-480.

The copied block retains the tested self capture; actual Blocks ownership is not implemented. **This does not prove startup can reach the off-main route**, contradict the previously recovered main-queue constraint, or demonstrate a race/interleaving on a device. It is a conditional ordering contract. No queue draining, deallocation or cancellation guarantee is inferred.

### Optional callbacks are selector-gated, in Float/Draw/Menu order

For stable modeled property results, the caller checks Float then Draw for `initImageTexture:` and Menu for `setOverlayView:`. Native getters and forwarding wrappers execute; missing objects or false selector responses skip the corresponding call. Variants cover all/none/single eligible callback and all three objects nil, in both builds and thread modes.

The texture callback argument is the modeled device, not the Overlay receiver. Texture callbacks remain explicit modeled boundaries. Menu receives the Overlay receiver. The actual Menu setter executes when eligible, rather than being treated as a trivial setter. Repeated getters are stable in these tests; changing-object/time-of-check behavior is not tested.

### Menu publishes the Overlay reference before device/cache guards

Native `MenuWindow setOverlayView:` (`0x617460`) strong-stores the supplied Overlay reference into global `0x1011c88` before querying its device. In standalone nil-device, existing-texture-cache and modeled decode-false cases, that publication remains, and the native body still reaches the modeled `readIniConfig` callback before normal return.

Device nil skips texture work. A nonnil cache at `0x10112f8` skips decode. With a device and empty cache, modeled decoder failure at `0x6374b4` also skips texture allocation/upload without undoing the reference store. The stored cache remains unchanged in these three tested routes. Nil INI pointer skips the later integer-read/apply branch; that branch is not covered here.

These are native ordering and selected memory effects with modeled ARC. They do not establish retain counts, a cycle/leak, pointee validity, heap lifetime or a dangling reference.

## Evidence and validation

- [Suite](../../tests/continuation-i/test_overlay_attachment.py)
- [Complete 30 records and hashes](../../results/continuations/continuation-i/overlay-attachment-tests.json)

With authorized inputs configured:

```bash
python tests/continuation-i/test_overlay_attachment.py
python tests/continuation-g/test_overlay_resources.py
python tests/continuation-h/test_overlay_config.py
python tools/validate-continuation-results.py --group continuation-i
```

Python 3.13.15, Capstone 5.0.7, Unicorn 2.1.4: **30/30 new cases passed**; three selected native ranges equal between builds. Earlier unequal R03 final-return instrumentation remains outside this pass's stop and is not declared equivalent.

The shared initializer model now accepts optional Draw/Menu/Float arguments, preserving existing defaults. A broad text replacement initially changed a regression factory call too; its NameError was caught and corrected before publication. The existing **34-case and 36-case suites were rerun with byte-identical records**. Initial `scale` provider naming was also rejected by the fail-closed model and corrected to the actual `nativeScale` selector. Other older native suites were not rerun.

Default generated output: `results/generated/continuation-i/`, overridden by `AU_RESULTS`. Only the new group was artifact-integrity validated; present-file hashes, changed links, Python/JSON and input identities checked. Not a complete-repository checksum run or full 764-record continuation validation. Totals: **764 continuation + 294 earlier = 1058 labeled records**, not independent end-to-end paths.

## Remaining work

Continue the final return tail, preserving the nonnil R03 trampoline boundary rather than assuming it matches a retain. Then trace successful Menu texture decode/upload and its nonnil INI read/apply branch, actual child texture callbacks and control-state ownership/writers. Real context/font/device-object internals, exceptions, scheduling and deallocation remain unresolved. No binary modification, real backend/device success, race/lifetime proof or FPS/touch fix is claimed.
