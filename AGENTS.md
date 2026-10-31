# Instructions for every agent working in this repository

## Current original-source retention exception

The user explicitly clarified that the original ZIP files themselves must be uploaded. Those eleven unchanged originals are now repository release assets, indexed in `archives/2026-10-31/README.md`. Earlier curated-text-only omission statements below describe the research code tree and prior publication, not current absence of these source assets from GitHub. Keep original sources distinct from curated tests/reports; archive retention does not authorize executing or modifying its contents, making a release build, or changing the research safety/evidence boundaries. Do not substitute a summary for an explicitly requested original-file upload.


These instructions apply to research, code, tests, documentation, artifact uploads and handoffs anywhere in this repository. **Report meaningful work directly in the repository, not only in a chat.** This file defines a standing workflow; it is not an automatic synchronization service or proof that an external agent has read it.

## 1. Read before doing work

Read `README.md`, `docs/HANDOFF.md`, `docs/NEXT-STEPS.md`, `docs/OMISSIONS.md`, the latest relevant reports, and the most recent entries in `docs/WORKLOG.md`. Consult `docs/CONTINUATION-REPRODUCTION.md` before running the continuation suites. Later specific corrections supersede older descriptions; retain evidence for the correction.

Check current branch, commit and working-tree changes. Do not overwrite another agent's or the user's work. Identify a bounded question and continue the current success-path investigation; do not restart resolved work or silently change scope.

## 2. Project scope and input integrity

- Recover the original startup-to-presentation **success-path graph**, comparing supplied original/R03 behavior and its failure, cancellation and recovery dependencies.
- Keep original, R03 and any historical candidates distinct. Verify exact input hashes before native analysis and after any process that could have touched inputs. Authorized source inputs remain read-only.
- Use existing captures, static analysis and bounded local tests. Do not introduce a diagnostic-build/capture cycle or make an installable/modified release as a substitute for analysis.
- Do not implement or extend authentication, certificate-trust, anti-cheat or access-control circumvention. Never turn an unresolved genuine backend transition into a seeded-success claim.
- Report native execution, modeled runtime boundaries, staged mutations, manually seeded state, synthetic failures and actual device evidence separately. Unsigned arithmetic, green assertions or graph indexes do not establish all-path coverage, race safety or FPS improvement.

## 3. Report every meaningful session directly here

Before handing off or declaring a task complete:

1. Append a concise entry to `docs/WORKLOG.md`: date, agent/tool identity as actually known, starting revision, question, work performed, evidence/file paths, commands/checks and outcomes, limitations, and next action. Record negative or inconclusive results and corrected harness assumptions as well as successful tests.
2. For new technical findings, add a focused report under `docs/reports/` using `docs/REPORT-TEMPLATE.md`, or make the smallest targeted update to an existing report when clearly continuing the same topic. Do not rewrite old findings without recording why they changed.
3. Put reviewed reusable scripts/tests in the relevant `tests/` or `tools/` group. Put complete reviewed case records and their scope/provenance summaries in a distinct `results/` group. Preserve earlier result sets rather than overwriting their historical meaning.
4. Add every related **permitted** new file needed to understand/reproduce the work. Do not leave the only copy in a chat attachment or sandbox path. If a related file cannot be included, record its role, omission reason and a safe identity/hash where appropriate; never invent a repository link to an absent file.
5. Update `docs/NEXT-STEPS.md` with what was advanced, what remains and the next concrete question. Update `docs/HANDOFF.md` when the overall continuation state changes; update `README.md` when navigation, counts or reproduction change.
6. Update `docs/INVENTORY.md`, `SHA256SUMS` and relevant provenance/omissions documentation for added/changed files. Checksums exclude `SHA256SUMS` itself. Include newly staged files; do not accidentally include ignored generated outputs or private local inputs.

Documentation-only work still needs a worklog entry and integrity/navigation updates, but does not need a fabricated technical report or new test cases.

## 4. Organize and review artifacts

- Follow the existing curated text-only policy in `docs/OMISSIONS.md`. Do not upload proprietary game/framework binaries, raw proprietary disassembly, unreviewed historical archives, installers, patch builders, credentials, tokens, private identifiers, temporary binary-download URLs or session attachment URIs.
- Prefer reviewed expanded scripts, structured results, reports and safe metadata over opaque ZIPs. Review every proposed artifact before publication; a request for “all files” does not remove these restrictions.
- Keep filesystem paths portable through `AU_ORIGINAL`, `AU_R03` and `AU_RESULTS`. Do not add hardcoded sandbox paths or private input locations to committed files.
- Preserve each result's scope and environment. If JSON is partitioned for size limits, retain every record and use relative part paths, counts and hashes; validate reconstruction. Source archives may be identified by hash without being uploaded.
- Label expected discrepancy tests: a passing assertion reproducing an ownership bug is not proof the underlying implementation is correct.

## 5. Validate before publishing

- Run the affected suites with the pinned dependencies; list exact commands, versions, counts and failures. Do not claim older untouched suites were rerun if they were not.
- Run `python tools/validate-continuation-results.py` for the existing indexed records. It currently expects the published 795-record continuation dataset (442 earlier + 64 scheduling + 58 startup/reentry + 54 factory/control-state + 46 initializer effects + 34 Overlay resource guards + 36 configuration/font/backend + 30 size/attachment composition + 31 normal return/Menu INI); use `--group continuation-j` only for explicitly scoped partial-checkout validation; if deliberately expanding its scope, update that expectation and documentation transparently rather than ignoring a failure.
- Check documentation links, Python syntax, artifact manifests and `sha256sum -c SHA256SUMS` from a complete checkout. Clearly distinguish a partial local/staged-file checksum check from checking every repository file.
- Review the diff for unintended edits, missing records and secrets. Retain failed-test explanations/harness corrections in the report, not as unexamined success claims.
- For docs-only changes, say that research tests were not rerun and validate the changed documentation/integrity files instead.

## 6. Publish and hand off

When repository write access is available and the task authorizes updates, commit/push reviewed reports and permitted artifacts as part of finishing the work. Use a focused commit or a review branch/PR when appropriate; respect branch protections and any required human review. Do not force-push, discard unrelated changes or claim an unmerged branch is on `main`.

If connector limits require upload batches, stage them on a branch and prefer a single reviewed/squashed final change on `main` when allowed. Verify the published files/revision before reporting completion. If upload/access is blocked, state the blocker and what remains unpublished; do not say it was saved to the repo.

End with the repository commit/PR link, what changed, validation performed, important limits and the next action. Chat is the brief handoff; the repository must contain the durable work and evidence.
