import argparse
from datetime import datetime, timezone
import json
import sys
import urllib.request
from .core import ROOT, manifest, read_rows, write_rows, validate, verified_image, sha256, overlay


def fetch(sources):
    for side, source in sources.items():
        path = ROOT / source['path']
        if path.exists():
            verified_image(source).close()
            print(side, 'existing image verified')
            continue
        if not source.get('sha256'):
            raise ValueError('No pinned SHA-256; source enrollment required before fetch')
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix('.download.tmp')
        request = urllib.request.Request(source['url'], headers={'User-Agent': 'PHAISTOS-research/0.1'})
        try:
            with urllib.request.urlopen(request, timeout=45) as response, temp.open('wb') as out:
                import shutil
                shutil.copyfileobj(response, out)
            if sha256(temp) != source['sha256']:
                raise ValueError('Downloaded bytes differ from pinned source: ' + side)
            # Validate image metadata before installing the download.
            check = dict(source, path=str(temp))
            verified_image(check).close()
            temp.replace(path)
            print(side, 'downloaded and verified')
        finally:
            temp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description='PHAISTOS D21 image digitization')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('fetch')
    check = commands.add_parser('validate')
    check.add_argument('--release', action='store_true')
    for command in ('annotate', 'overlay'):
        sub = commands.add_parser(command)
        sub.add_argument('--side', choices=['A', 'B'], required=True)
        if command == 'annotate':
            sub.add_argument('--operator', required=True)
            sub.add_argument('--mapping-reference', required=True)
    review = commands.add_parser('review')
    review.add_argument('--group', required=True)
    review.add_argument('--reviewer', required=True)
    review.add_argument('--note', required=True)
    args = parser.parse_args()
    sources = manifest()
    if args.command == 'fetch':
        fetch(sources)
        return 0
    path = ROOT / 'data/groups.csv'
    rows = read_rows(path)
    result = validate(rows, sources, release=getattr(args, 'release', False))
    if args.command == 'validate':
        if args.release:
            state = json.loads((ROOT / 'data/project_state.json').read_text(encoding='utf-8'))
            if not (state.get('checkpoint_sha256') and state.get('d21_originals_imported')
                    and state.get('group_numbering_verified') and state.get('mapping_evidence')):
                result['errors'].append('Original checkpoint/D21 import and numbering verification outstanding')
        result['csv_sha256'] = sha256(path)
        result['source_sha256'] = {k: s['sha256'] for k, s in sources.items()}
        result['checked_utc'] = datetime.now(timezone.utc).isoformat()
        # Working templates can be checked before source images are available.
        for side, source in sources.items():
            if args.release or (ROOT / source['path']).exists():
                try:
                    verified_image(source).close()
                except (OSError, ValueError) as exc:
                    result['errors'].append(side + ': ' + str(exc))
        result['valid'] = not result['errors']
        report = ROOT / 'reports' / ('release.json' if args.release else 'validation.json')
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(result, indent=2))
        return 0 if result['valid'] else 1
    if not result['valid']:
        raise ValueError('\n'.join(result['errors']))
    if args.command == 'annotate':
        if not args.operator.strip() or not args.mapping_reference.strip():
            raise ValueError('operator and mapping reference required')
        from .annotator import run
        run(rows, sources[args.side], args.side, args.operator, args.mapping_reference, path)
    elif args.command == 'overlay':
        output = ROOT / 'reports' / f'overlay_{args.side}.png'
        overlay(rows, args.side, sources[args.side], output)
        print(output)
    elif args.command == 'review':
        row = next((r for r in rows if r['group_id'] == args.group), None)
        if row is None or row['status'] != 'draft':
            raise ValueError('Review requires an existing draft group')
        verified_image(sources[row['side']]).close()
        row.update(status='reviewed', reviewer=args.reviewer.strip(),
                   reviewed_utc=datetime.now(timezone.utc).isoformat(), review_note=args.note.strip())
        result = validate(rows, sources)
        if not result['valid']:
            raise ValueError('\n'.join(result['errors']))
        write_rows(path, rows)
        print(args.group, 'review declaration saved')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, urllib.error.URLError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
