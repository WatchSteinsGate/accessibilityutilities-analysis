# Continuation artifact provenance and organization

## Local source-package identities

These local session packages were reviewed as sources, **not uploaded as opaque archives**. No binary download link or session attachment URI is included.

| Local source package | Bytes | SHA-256 |
| --- | ---: | --- |
| `Lifecycle-render-shortcut-continuation-evidence.zip` | 68836 | `57435c9cbcad97fca4346443ac7d27c4260460c19f94d6ebb0af6c16d629ae71` |
| `Attachment-factory-completion-evidence.zip` | 68303 | `36cf5a5343ebc71cb77390fbd54e8e0ae3344879e93e87e96fb6e668bdfe0dc2` |

## Expanded repository mapping

| Material | Repository destination |
| --- | --- |
| First continuation report, repository edition | `docs/CANCELLATION-RENDER-SHORTCUT.md` |
| Second continuation report, repository edition | `docs/ATTACHMENT-FACTORY-COMPLETION.md` |
| What changed / pending work | `docs/NEXT-STEPS.md` and updated `docs/HANDOFF.md` |
| First group's parser/emulator/native metadata + four suites | `tests/continuation-a/` |
| Second group's parser/emulator/native metadata + five suites | `tests/continuation-b/` |
| First group's fresh portable records and reference-candidate metadata | `results/continuations/continuation-a/` |
| Second group's fresh portable records and code-equality metadata | `results/continuations/continuation-b/` |
| Input/environment setup and model boundaries | `docs/CONTINUATION-REPRODUCTION.md` |

## Validation and curation

- Original run dependencies: Capstone 5.0.9 / Unicorn 2.1.4.
- Fresh repository rerun: Python 3.13 / Capstone 5.0.7 / Unicorn 2.1.4, using root pinned requirements.
- New rerun record totals: 232 + 210 = 442 labeled scoped cases, all passing expected assertions.
- Existing 294-case suites were not changed or rerun in this update. Their earlier records remain separate.
- Some assertions deliberately reproduce an expected ownership discrepancy; “passed” does not mean the underlying patched behavior is correct.
- Compact JSON preserves every modeled record/value; summary files retain per-suite scopes.
- Raw disassembly/reference instruction windows, ZIPs, binaries, private identities, temporary links and release/patch tooling are omitted. See `OMISSIONS.md`.
- The root checksum manifest preserves prior entries for untouched files and replaces/adds entries for this update. It excludes itself.

## Indexed record parts

Large `*-tests.json` files are `partitioned-v1` indexes. Each lists relative part paths, record counts and SHA-256 values; every original record is retained in the adjacent text JSON parts. Runnable tests still emit ordinary complete JSON into generated results. The checked-in validator verifies both formats. Partitioning addresses connector request limits without publishing opaque archives.

## Scheduling pass

The later scheduling continuation starts at `ba6c9ff8340be1a766996f06ea63caa2d48f9a03`. It adds `docs/reports/LIFECYCLE-SCHEDULING.md`, two scripts under `tests/continuation-c/`, and complete 64-case records plus bounded static metadata under `results/continuations/continuation-c/`. It reuses unchanged continuation-b helpers; no evidence ZIP or duplicate helper tree is required.

The new suite and mapper ran with Python 3.13 / Capstone 5.0.7 / Unicorn 2.1.4. The prior 442 records were integrity-validated, not rerun. The indexed validator deliberately expands from 442 to 506 records. Across all groups there are 800 stored labeled cases, not 800 independent paths. Raw local disassembly and scratch reference maps remain excluded; retained metadata contains reviewed address roles, hashes and direct-edge provenance rather than instruction dumps. Changed-file checksums are verified locally; untouched remote manifest entries are retained in this partial checkout.

## Reattached sources and startup/reentry pass

[Attachment intake](ATTACHMENT-INTAKE.md) and its [manifest](../results/source-attachments/2026-10-30-intake.json) account for nine attachment occurrences / seven unique hashes, including three byte-identical original workpacks. The exact supplied resize source report is preserved; mixed archives, proprietary inputs and build/apply/bypass material are not uploaded wholesale. Existing curated records are not asserted byte-identical to archive source JSON.

The new startup/reentry pass contributes 58 cases and ten equal code/data ranges. Existing scheduling (64) and attachment (110) suites passed fresh reruns; those reruns are not new cases. Continuation records total 564; including earlier lifecycle/resize gives 858 stored labeled records. Group-d integrity and all present staged hashes were checked; the complete repository/564-record dataset was not downloaded or fully revalidated in this partial checkout. The earlier groups retain their historical meaning.
