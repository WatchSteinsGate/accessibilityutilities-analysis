# Complete DrawWindow and MenuWindow initializer effects

## Provenance and scope

2026-10-30, Notion AI. Starting published revision: `29e4e16cc5f99b7f4c89fcfcc78025b322202088`. Continue the two initializer bodies left partial/modeled by the [factory/control-state pass](FACTORY-CONTROL-PROVENANCE.md). Authorized original/R03 hashes are unchanged from the handoff.

Both native initializer normal/false/nil-return bodies now execute through return. Inherited initialization, ObjC/ARC/Blocks, Foundation paths/data/file operations, INI load/read/write, allocation and dispatch_once remain modeled external boundaries. No actual filesystem write, UIKit, backend or device execution occurs. “Complete body” does not mean complete transitive runtime execution or exception coverage.

## Findings

### DrawWindow setup continues after modeled inherited nil

The earlier control-publication prefix is extended through native setup helper `0x10cac`, native state-getter/boolean-store forwarding, the imported CGSizeZero read, size-vector reset and normal return. In the tested inherited-nil case it still publishes the supplied control pointer, sets setup byte `0xff2784` to 1 and resets the 16-byte vector at `0x1011a28` before returning nil. Ordinary success performs the same selected effects and returns the receiver.

This narrows the unresolved synchronous work: the recovered helper performs local state writes, not a queue-dispatch operation. Actual inherited initialization and runtime memory-order/concurrency behavior remain unverified. A synthetic nil return is not evidence that it occurs on the device.

### MenuWindow file-create false does not abort initialization

The native body constructs a modeled preferences path, queries file existence and attempts empty-file creation when missing. It does **not** test the creation call's Boolean return before proceeding to UTF8 conversion and `ini_load`. The explicit false-return case still reaches INI loading and inherited `init`; no real file is created by the harness.

INI load nil skips subsequent integer read/write work but does not itself prevent inherited initialization. A nonnil modeled INI pointer is published to `0x1011c80`, then the native setting helper normalizes the tested integers: only input 1 selects true at `0xff2780`; tested -1, 0 and 2 select false. Noncanonical -1/2 cause a modeled configuration write of 0; canonical 0/1 avoid that rewrite in these cases. These are bounded integer contracts, not a recovered complete settings schema.

### Configuration effects precede inherited initialization

MenuWindow performs the path/file/INI work and selected state/config writes before reaching inherited initialization. The late inherited-nil case still retains those selected effects before returning nil. No rollback, ownership leak or runtime resource lifetime is inferred solely from this ordering.

### Once composition bounds repeated work

The actual native DrawWindow/MenuWindow factories and once blocks are composed with these newly executed bodies. Across three sequential changed-control calls, the modeled completed-once sequence allocates/initializes once. Forced allocation or inherited-init failure leaves the completed singleton nil without retry. Menu path/INI work occurs once in these modeled sequences, not on each later factory call. This does not establish dispatch_once exception/concurrency semantics or all callers; no device FPS cause is assigned.

## Evidence and validation

- [Native/model suite](../../tests/continuation-f/test_initializer_effects.py) and [all case records](../../results/continuations/continuation-f/initializer-tests.json).
- **46 new labeled cases:** 8 complete Draw initializer cases, 18 complete Menu cases, 8 native setting-helper cases, 12 factory/complete-initializer sequences. Counts include paired builds, synthetic false/nil inputs and repeated calls, not independent end-to-end paths.
- Four selected native ranges are byte-identical between the supplied images. This does not establish whole-framework equivalence.
- Python 3.13.15, Capstone 5.0.7, Unicorn 2.1.4: new **46/46** cases passed. The previous factory suite **54/54** was rerun because its executable tests were placed behind `main()` for safe model import; its generated records remain byte-identical. Other native suites were not rerun.

With authorized `AU_ORIGINAL` / `AU_R03` set:

```bash
python tests/continuation-e/test_factories.py
python tests/continuation-f/test_initializer_effects.py
python tools/validate-continuation-results.py --group continuation-f
```

Default generated output: `results/generated/continuation-f/`, overridden by `AU_RESULTS`. Group-f record integrity, Python syntax, changed-document links, present-file checksums and unchanged input hashes were checked. Default complete continuation validation now expects 664 records; only the new group was integrity-validated this pass. Including earlier lifecycle/resize records gives 958 stored labeled cases, not unique paths. This is a partial checkout, not a whole-repository checksum/full-664-record run.

## Harness corrections

An initial false-return test incorrectly expected file-creation failure to exit early. Its trace also exposed unbound raw class references: the final harness explicitly binds the two selector-provider slots (`0xff08f8` and `0xff0990`) symbolically for `defaultManager`/`data`; it does not claim to reconstruct the real loader or prove class identity from nil raw pointers. Rechecking the native branch and retesting with those providers confirmed the creation Boolean is ignored on this normal path. The incorrect early-exit assumption was removed, not silently reported as a passing failure-recovery result. No native input was edited.

## Remaining work

Actual allocation ownership/deallocation/replacement and pointee writers remain unresolved. Most of OverlayView initialization, throwing paths, real Foundation/INI and UIKit callbacks, synchronous reentry and runtime scheduling remain open. The earlier staged-cancellation result is still conditional. No use-after-free, actual race, crash cause, FPS/touch improvement or genuine backend success is established; no modified release built.

Next: continue the actual OverlayView initializer boundaries and control-state lifetime/writers. Retain the recovered main-queue constraint; require concrete callback/state-writer provenance before claiming a reachable interruption. Raw instruction scratch material remains local; reviewed test source and complete scoped records are published.
