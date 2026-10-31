# Supplied attachment intake

## Current batch — 2026-10-31

The [new intake manifest](../results/source-attachments/2026-10-31-intake.json) accounts for all **11 supplied occurrences / 10 unique SHA-256 identities**. Eight occurrences match the seven unique identities in the earlier intake; three identities are new to that manifest. `workpack-original-reference.zip` and this batch's single `workpack.zip` are identical copies. The earlier nine-occurrence record remains historical and unchanged.

### Organized additions

- [Reviewed historical session context through R03](source-reports/SESSION-CONTEXT-THROUGH-R03-REVIEWED.md): a curated edition, not the raw export or a complete source recovery.
- [T01/T02 diagnostic provenance](source-reports/TIMING-DIAGNOSTICS-PROVENANCE.md): distinct input identities, source-reported diagnostic corrections and validation/measurement limits; no new diagnostic-build/capture cycle.
- An eleven-item provenance manifest with source sizes/hashes, archive member counts/CRC checks, duplicate dispositions and safe repository destinations.
- Updated intake validation, navigation, omissions, inventory and checksums.

### What was already accounted for

The original workpack pair, R01, R03, whole-system evidence, lifecycle evidence, resize evidence and standalone resize report match previously recorded source identities. The standalone resize report also matches the already retained exact historical report hash. Existing curated reports, tests and result records are retained without duplicate uploads or replacement by older nonportable copies.

### Publication and validation boundary

No opaque ZIP, proprietary framework, patch/apply/build tool, binary delta, raw operational disassembly or unredacted session/capture export is published. Original/R03/R01 member hashes were rechecked read-only. T01/T02 members match their own package output declarations; their declared V58 baseline is not substituted for the repository's supplied reference input. All nine supplied ZIPs passed member CRC checks. No attachment code, native suite, installer or device test was run. No new native/model cases or performance claims are added.

Run `python tools/validate-attachment-intake.py` to validate both dated manifests and the retained narratives. This checks committed provenance/retained-file integrity, not recovery of omitted source archives or independent reproduction of package claims. See [omissions](OMISSIONS.md).

## Previous batch — 2026-10-30

All nine supplied attachment occurrences are accounted for in [the intake manifest](../results/source-attachments/2026-10-30-intake.json). There are seven unique SHA-256 identities: `workpack-original-reference.zip` and both attachments named `workpack.zip` are byte-identical copies. No copy was silently treated as a different baseline.

The supplied original and R03 framework members match the previously recorded input identities. They were extracted locally for read-only native analysis; neither was edited, installed or redistributed. The R01 candidate was identified separately and not executed.

### What is committed

- [Exact supplied resize report](source-reports/Resize-layout-continuation.md), byte-for-byte, also identical to the report inside the resize evidence archive. This is a historical source report: its relative harness dependencies and next-work list are not the current portable recipe.
- [Current portable resize edition](RESIZE-LAYOUT-CONTINUATION.md), [lifecycle edition](LIFECYCLE-CONTINUATION.md), their existing tests and historical/portable records remain canonical repository material.
- Archive-level names, sizes, SHA-256 identities, member counts, verified baseline identities, duplicate accounting and explicit dispositions for all nine inputs.
- New reviewed startup/reentry [report](reports/STARTUP-REENTRY-BOUNDARIES.md), native tests, static metadata and all 58 scoped new case records.

### What is not committed

The workpacks and R01/R03 packages contain installable framework binaries and patch/build/apply material; the whole-system archive contains mixed raw disassembly, broad indices and security/validation details. Those archives are not uploaded wholesale. Raw lifecycle/resize disassembly and historical nonportable harness copies are also not added as opaque ZIPs. The existing curated editions are not asserted byte-identical to original archive test records.

The intake manifest is an accounting record, not a promise that an omitted archive or binary can be recovered from Git. Keep the authorized source attachments separately. No private attachment IDs, sandbox locations, credentials or temporary download URLs are published. See [omissions](OMISSIONS.md).

### Verify retained material

```bash
python tools/validate-attachment-intake.py
python tools/validate-continuation-results.py --group continuation-d
```

The first check verifies retained report bytes and intake consistency without requiring private archives. The second verifies all 58 new records and their partition hashes. At that historical checkpoint, default continuation validation covered four groups and 564 records. The current continuation total is maintained in README and the continuation validator; this attachment-intake check does not rerun those native suites.
