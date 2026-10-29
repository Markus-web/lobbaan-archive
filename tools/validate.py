#!/usr/bin/env python3
"""Validate the archive's structure (README.md, "Verify the data"). Standard library only.

Checks every JSON file parses, and that state shards, daily change lists and manifests have the
shape documented in docs/schema/. Exits non-zero with one line per problem.

    python3 tools/validate.py            # whole repository
    python3 tools/validate.py --quick    # only files changed in the last commit
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
SHA256 = re.compile(r'^[0-9a-f]{64}$')
CHANGE_TYPES = {'added', 'edited', 'removed', 'restored'}
problems: list[str] = []


def fail(path: Path, message: str) -> None:
    problems.append(f'{path.relative_to(ROOT)}: {message}')


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (ValueError, UnicodeDecodeError) as err:
        fail(path, f'not valid JSON ({err})')
        return None


def check_state(path: Path, data) -> None:
    if not isinstance(data, dict):
        return fail(path, 'state shard must be an object keyed by record key')
    for key, entity in data.items():
        if not isinstance(entity, dict) or entity.get('key') != key:
            fail(path, f'{key}: entity key does not match')
            continue
        versions = entity.get('versions')
        if not isinstance(versions, list) or not versions:
            fail(path, f'{key}: no versions')
            continue
        previous = ''
        for i, v in enumerate(versions):
            where = f'{key} version {i + 1}'
            if not SHA256.match(str(v.get('hash', ''))):
                fail(path, f'{where}: hash is not SHA-256 hex')
            first = str(v.get('firstSeen', ''))
            if not DATE.match(first):
                fail(path, f'{where}: firstSeen is not YYYY-MM-DD')
            elif first < previous:
                fail(path, f'{where}: versions are not in date order')
            previous = first
            if 'until' in v and not DATE.match(str(v['until'])):
                fail(path, f'{where}: until is not YYYY-MM-DD')
            if not isinstance(v.get('data'), dict):
                fail(path, f'{where}: data must be an object')
            if not isinstance(v.get('observedVia'), str):
                fail(path, f'{where}: observedVia missing')
        if 'removedAt' in entity and not DATE.match(str(entity['removedAt'])):
            fail(path, f'{key}: removedAt is not YYYY-MM-DD')


def check_changes(path: Path, data) -> None:
    day = '-'.join(path.with_suffix('').parts[-3:])
    if not isinstance(data, list):
        return fail(path, 'change list must be an array')
    for i, c in enumerate(data):
        if not isinstance(c, dict):
            fail(path, f'entry {i}: not an object')
        elif c.get('date') != day or c.get('type') not in CHANGE_TYPES or not c.get('key') or not c.get('kind'):
            fail(path, f'entry {i}: needs date {day}, key, kind and type in {sorted(CHANGE_TYPES)}')


def check_manifest(path: Path, data) -> None:
    if not isinstance(data, dict) or not isinstance(data.get('sources'), list):
        return fail(path, 'manifest needs a sources array')
    if path.name != 'latest.json':
        day = '-'.join(path.with_suffix('').parts[-3:])
        if data.get('date') != day:
            fail(path, f'date {data.get("date")} does not match the path {day}')
    for s in data['sources']:
        if not isinstance(s.get('ok'), bool) or not s.get('source') or not s.get('url'):
            fail(path, f'source entry {s.get("source")}: needs source, url and ok')
        if 'sha256' in s and not SHA256.match(str(s['sha256'])):
            fail(path, f'{s.get("source")}: sha256 is not hex')


def check(path: Path) -> None:
    data = load(path)
    if data is None:
        return
    parts = path.relative_to(ROOT).parts
    if parts[0] == 'state' and len(parts) == 3:
        check_state(path, data)
    elif parts[0] == 'changes' and len(parts) == 4:
        check_changes(path, data)
    elif parts[0] == 'manifest':
        check_manifest(path, data)
    elif parts[0] == 'raw' and not isinstance(data, list):
        fail(path, 'raw source copy must be an array')


def main() -> int:
    if '--quick' in sys.argv:
        out = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
        files = [ROOT / f for f in out.stdout.split() if f.endswith('.json') and (ROOT / f).exists()]
    else:
        files = [p for d in ('state', 'changes', 'manifest', 'raw', 'imports') for p in (ROOT / d).rglob('*.json')]
    for path in sorted(files):
        if '.git' not in path.parts:
            check(path)
    for line in problems[:200]:
        print(line)
    print(f'{len(files)} files checked, {len(problems)} problems')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
