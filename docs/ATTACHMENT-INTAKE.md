# Supplied attachment intake — 2026-10-30

All nine supplied attachment occurrences are accounted for in [the intake manifest](../results/source-attachments/2026-10-30-intake.json). There are seven unique SHA-256 identities: `workpack-original-reference.zip` and both attachments named `workpack.zip` are byte-identical copies. No copy was silently treated as a different baseline.

The supplied original and R03 framework members match the previously recorded input identities. They were extracted locally for read-only native analysis; neither was edited, installed or redistributed. The R01 candidate was identified separately and not executed.

## What is committed

- [Exact supplied resize report](source-reports/Resize-layout-continuation.md), byte-for-byte, also identical to the report inside the resize evidence archive. This is a historical source report: its relative harness dependencies and next-work list are not the current portable recipe.
- [Current portable resize edition](RESIZE-LAYOUT-CONTINUATION.md), [lifecycle edition](LIFECYCLE-CONTINUATION.md), their existing tests and historical/portable records remain canonical repository material.
- Archive-level names, sizes, SHA-256 identities, member counts, verified baseline identities, duplicate accounting and explicit dispositions for all nine inputs.
- New reviewed startup/reentry [report](reports/STARTUP-REENTRY-BOUNDARIES.md), native tests, static metadata and all 58 scoped new case records.

## What is not committed

The workpacks and R01/R03 packages contain installable framework binaries and patch/build/apply material; the whole-system archive contains mixed raw disassembly, broad indices and security/validation details. Those archives are not uploaded wholesale. Raw lifecycle/resize disassembly and historical nonportable harness copies are also not added as opaque ZIPs. The existing curated editions are not asserted byte-identical to original archive test records.

The intake manifest is an accounting record, not a promise that an omitted archive or binary can be recovered from Git. Keep the authorized source attachments separately. No private attachment IDs, sandbox locations, credentials or temporary download URLs are published. See [omissions](OMISSIONS.md).

## Verify retained material

```bash
python tools/validate-attachment-intake.py
python tools/validate-continuation-results.py --group continuation-d
```

The first check verifies retained report bytes and intake consistency without requiring private archives. The second verifies all 58 new records and their partition hashes. Full default continuation validation requires all four continuation groups and expects 564 records, separate from the 294 earlier lifecycle/resize records.
