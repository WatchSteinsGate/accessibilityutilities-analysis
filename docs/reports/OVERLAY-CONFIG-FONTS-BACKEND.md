# Overlay configuration, font guards and backend return contracts

## Provenance and execution boundaries

2026-10-30, Notion AI. Starts at published `fa1acfb4f7641e48dbcb7a109e37748127b977b9` and continues the [resource-guard pass](OVERLAY-RESOURCE-GUARDS.md). Both authorized input hashes are unchanged.

This pass adds **36 labeled native/model records**: 18 path/IO cases, 10 font-guard cases and 8 standalone backend-initializer cases. These are paired-build contracts under modeled providers, not actual runtime failures or unique end-to-end paths.

The resource-ready initializer now runs past `0x6849f8`. GUI compatibility check `0x14e514` and context creation `0x13813c` are explicitly modeled native-call boundaries, not executed GUI internals. Their arguments are recorded; context creation supplies a synthetic current-context pointer. Native current-context getter `0x138548`, forwarding wrappers, path/IO stores and font-config constructors execute. Font-add providers, Foundation/ObjC/ARC, allocation and filesystem operations remain modeled. Ready font paths stop before `syncOverlaySize` at `0x684e74`; failed required-font paths execute to nil return.

Separately, native backend initializer `0x12a0c8` and its native helper `0x12a1cc` execute through normal return. Backend registration and device-object work below them are modeled. No successful whole Overlay initializer, actual GUI/context/GPU/backend/device execution or performance improvement is established.

## Findings

### Native configuration path tolerates modeled file-create and string-copy failure

The native path appends **Documents**, then **imgui.ini**, to the modeled home directory. File existence skips creation; missing-file cases attempt creation. Both true and false creation returns continue to UTF8 conversion and the next setup boundary. No file is created by the harness.

At the modeled IO pointer, native code assigns flags `0x200000`, clears offset `+0x20` (log-filename slot) and writes offset `+0x18` (INI-filename slot). A nonnil UTF8 pointer reaches modeled `strdup`; its returned copy is stored. UTF8 nil skips duplication and stores zero; duplicate-allocation nil also stores zero. All these cases reach the pre-constructor stop `0x684cec`, rather than returning nil at this stage.

Existing synthetic IO fields are seeded nonzero to verify native overwrites. This is not evidence that the real context constructor reuses an object or that an old string is leaked: actual context construction and prior ownership are not executed. No persistence success, later file-open behavior or string lifetime is inferred.

### Two font results are required; the intermediate merge result is not checked here

The first native font-add call is modeled at `0x6601a0`; a nonnil result enables the intermediate merge call through native wrappers. The third call, at `0x660340`, runs even if the first returns nil. The native final guard requires first and third results to be nonnil. Either required result nil leads to a normal nil return before size synchronization or backend initialization.

When both required results are nonnil, a nil intermediate merge result still reaches `0x684e74`. This proves only that this caller does not reject that modeled merge result. Font parsing, glyph completeness, atlas validity and actual allocation behavior are not tested.

Native font-config constructors `0x65ef08` / `0x65ee88` and their small vector constructors execute with bounded modeled `memset`. Font data is not decoded, uploaded or redistributed. Font-provider call roles and returned pointers are retained in the records.

### Backend wrapper return and flags are not proof of device-object success

Native `0x12a0c8` publishes the backend-name pointer at IO `+0x80`, ORs bit `8` into IO flags at `+4`, invokes modeled registration, then calls native `0x12a1cc`. The helper sends `makeDeviceObjectsWithDevice:` to a symbolic backend object and calls modeled `0x12a434` device-object work. Both native wrappers return literal true on their tested normal paths without propagating those modeled results.

Across nil/nonnil device arguments and zero/one device-object-helper results, the top-level return remains 1 and seeded flags `0x20` become `0x28`. A deliberately zero modeled message result is also not propagated. Thus the wrapper return and published flags alone are insufficient evidence of successful GPU resource creation. These are normal-return contracts; no exception, real nil-device behavior or actual device-object construction is established.

The Overlay caller at `0x684ecc` does not branch on that return before continuing. This is a static caller observation; the standalone backend tests are not presented as one composed full-initializer trace.

## Evidence and reproduction

- [Suite](../../tests/continuation-h/test_overlay_config.py)
- [All records and hashes](../../results/continuations/continuation-h/overlay-config-tests.json)

With authorized `AU_ORIGINAL` and `AU_R03` configured:

```bash
python tests/continuation-h/test_overlay_config.py
python tests/continuation-g/test_overlay_resources.py
python tools/validate-continuation-results.py --group continuation-h
```

Python 3.13.15, Capstone 5.0.7, Unicorn 2.1.4: new **36/36 passed**, six selected code windows byte-identical. The existing **34/34** resource-guard regression passed with byte-identical records after its test entry point became import-safe and its stop address became an optional argument. Other native suites were not rerun. These selected equal windows do not erase the previously documented unequal R03 return tail.

Generated output defaults to `results/generated/continuation-h/`; override with `AU_RESULTS`. New-group record integrity, changed-document links, Python syntax/JSON, present-file hashes and unchanged input identities checked. Only group h was integrity-validated; not a complete-repository checksum run or full 734-record continuation validation. Total retained labels: **734 continuation + 294 earlier = 1028**, including synthetic inputs and repetitions.

The first path test failed closed at an unmodeled `_objc_retainAutorelease` import. The final model explicitly handles this ARC boundary as identity with no real lifetime semantics. No input binary was altered.

## Remaining boundary

Next: compose actual `syncOverlaySize`, subsequent parent/child attachment checks and the late nontrivial MenuWindow `setOverlayView:` call. Backend device-object internals, actual GUI construction/font providers, exceptions, control-state writers/replacement/deallocation and real runtime scheduling remain unresolved. No race, ownership defect, crash cause, FPS/touch fix or modified release is claimed.
