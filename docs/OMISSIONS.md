# Deliberate omissions and provenance

This is a **curated safe handoff**, not “all historical files.” No omitted attachment should be assumed uploaded or recoverable from this repository.

## Excluded

- Proprietary game executables and original/modified framework binaries: no redistribution authorization established; exact identities are retained instead.
- Installable IPA/framework bundles, historical ownership candidates, patch builders, binary-edit scripts, removal/ablation patch recipes, and release assets: not needed for read-only lifecycle analysis; could alter access-control behavior.
- Authentication, certificate-trust, anti-cheat, or access-control bypass implementations and their operational tests/disassembly: outside this repository's scope.
- Full historical workpacks, evidence ZIPs, raw whole-system/session-context exports, and unreviewed logs: may contain binaries, operational bypass detail, temporary download URLs, private identifiers, or nonportable attachment references.
- Credentials, tokens, account email addresses, private input values, transient binary download URLs, and session attachment URIs: not included.
- Raw proprietary disassembly and large runtime dumps: the included written findings and modeled-case records provide the benign continuation without redistributing those sources.

## Included provenance

The two detailed continuation reports are repository editions of the existing lifecycle and resize reports. Findings and limits are retained; reproduction sections were corrected for portable paths and omitted artifacts. The broader handoff and integrity overview are curated summaries of the investigation, not a claim to reproduce every historical report verbatim.

The five test scripts were adapted from the recent read-only local suites. Shared native emulation and a read-only Mach-O parser were isolated into dedicated modules. Hardcoded sandbox paths were replaced with authorized-input environment variables and strict SHA-256 checks. Button selector/class names were extracted as declarative JSON; no historical builder is executed or distributed. Inputs are read only; test writes target emulated memory and result files.

Historical result JSON is preserved in two subdirectories. The fresh packaging rerun is separate in `results/portable-run/`, with its own summary. Case counts include repetitions and build pairs; models are not real UIKit/backend/device execution.

The user's fuller Notion context and private retained local artifacts remain separate. This commit does not move, delete, or automatically synchronize them. Future additions should maintain these boundaries and be reviewed for secrets and redistribution rights.

## New success-path continuation additions

The two new reports, nine portable read-only test suites and their modeled-case records were reviewed and added in expanded text form. Original evidence ZIPs are **not** uploaded verbatim; benign scripts/results were selected and adapted. Raw proprietary disassembly, symbol dumps, full function indices, source binaries, historical download links, patch/build/install tooling and private session material remain excluded under the policy above.

The new reports are repository editions: references to omitted local disassembly/ZIP packaging were corrected, reproduction uses `AU_ORIGINAL` / `AU_R03`, results use `AU_RESULTS`, and fresh portable reruns use the existing pinned dependencies. Source archive identities and the adaptation/review map are retained in `CONTINUATION-ARTIFACTS.md`. A missing raw artifact is deliberate, not evidence that the repo reproduces the entire historical investigation.

## Scheduling continuation additions

The scheduling report, two portable scripts, complete 64-case records and bounded static metadata are included. Local raw instruction windows, broad scratch reference files and unresolved-class debugging output are omitted; their role, corrected assumptions and limits are described in `reports/LIFECYCLE-SCHEDULING.md`. No proprietary binary, ZIP, backend/authentication implementation, secret or private download/session URI is added. The existing continuation-b helpers are reused unchanged.
