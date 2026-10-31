"""Run portable native/model suites and compare historical record values.

Requires AU_ORIGINAL/AU_R03 and pinned requirements. No source archive code is
executed. Outputs are ignored generated artifacts until explicitly reviewed.
"""
from pathlib import Path
import os
import sys
import json
import hashlib
import subprocess
import platform
import importlib.metadata

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('AU_REGRESSION_RESULTS',
                          ROOT / 'results/generated/regression')).resolve()


def load_records(path):
    data = json.loads(path.read_text())
    if data.get('recordFormat') == 'partitioned-v1':
        records = []
        for part in data['parts']:
            source = (path.parent / part['path']).resolve()
            assert source.is_relative_to((ROOT / 'results/continuations').resolve())
            assert hashlib.sha256(source.read_bytes()).hexdigest() == part['sha256']
            rows = json.loads(source.read_text())['records']
            assert len(rows) == part['records']
            records.extend(rows)
    else:
        records = data['records']
    assert data['passed'] and data['cases'] == len(records)
    return data, records


def main():
    assert os.environ.get('AU_ORIGINAL') and os.environ.get('AU_R03')
    OUT.mkdir(parents=True, exist_ok=True)
    suites = []
    groups = set()
    for suite in sorted((ROOT / 'tests').glob('**/test_*.py')):
        group = suite.parent.name if suite.parent.name != 'tests' else 'base'
        groups.add(group)
        env = dict(os.environ, AU_RESULTS=str(OUT / group))
        run = subprocess.run([sys.executable, str(suite)], cwd=ROOT, env=env,
                             capture_output=True, text=True)
        suites.append(dict(suite=str(suite.relative_to(ROOT)),
                           returncode=run.returncode))
        if run.returncode:
            # Keep failure diagnostics local; review before any publication.
            (OUT / 'failure.txt').write_text(run.stdout + '\n' + run.stderr)
            raise RuntimeError(f"Suite failed: {suite.relative_to(ROOT)}")
        print(f'{suite.relative_to(ROOT)} PASS', flush=True)
    artifacts = []
    for group in sorted(groups):
        for generated in sorted((OUT / group).glob('*-tests.json')):
            data, records = load_records(generated)
            retained = (ROOT / 'results/portable-run' / generated.name if group == 'base'
                        else ROOT / 'results/continuations' / group / generated.name)
            same = None
            if retained.exists():
                _, prior = load_records(retained)
                # Preserve synthetic NaN/Infinity spellings while normalizing keys.
                same = (json.dumps(records, sort_keys=True) ==
                        json.dumps(prior, sort_keys=True))
                assert same, f'Historical record discrepancy: {group}/{generated.name}'
            artifacts.append(dict(group=group, file=generated.name, cases=len(records),
                                  passed=data['passed'], retained_records_equal=same))
    summary = dict(passed=True, python=platform.python_version(),
                   capstone=importlib.metadata.version('capstone'),
                   unicorn=importlib.metadata.version('unicorn'),
                   input_sha256={key: hashlib.sha256(
                       Path(os.environ[var]).read_bytes()).hexdigest()
                       for key, var in [('original', 'AU_ORIGINAL'), ('r03', 'AU_R03')]},
                   suite_count=len(suites), suites=suites, artifacts=artifacts,
                   cases=sum(a['cases'] for a in artifacts),
                   scope='Bounded native/model regression, not real UIKit/GPU/device execution. '
                         'Counts include paired builds, repetitions and synthetic cases; '
                         'not unique or independent end-to-end paths. Comparison concerns '
                         'record values after JSON key normalization, not byte-identical files.')
    assert len(artifacts) == len(suites), 'Missing or stale generated output files'
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(dict(passed=True, suites=len(suites), cases=summary['cases'])))


if __name__ == '__main__':
    main()