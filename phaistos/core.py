"""Strict measurement validation and deterministic overlays."""
import csv
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['group_id', 'side', 'x_px', 'y_px', 'uncertainty_px', 'status',
          'image_sha256', 'width', 'height', 'operator', 'captured_utc',
          'mapping_reference', 'note', 'reviewer', 'reviewed_utc', 'review_note']
IDS = {f'{side}{i:02d}': side for side, n in [('A', 31), ('B', 30)]
       for i in range(1, n + 1)}


def sha256(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read_rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError('CSV schema mismatch: expected ' + ','.join(FIELDS))
        rows = list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError('Malformed CSV row')
    return rows


def write_rows(path, rows):
    path = Path(path)
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    temp.replace(path)


def normalized(x, y, width, height):
    if width < 2 or height < 2:
        raise ValueError('Image dimensions must be >= 2')
    if not all(math.isfinite(v) for v in (x, y)):
        raise ValueError('Nonfinite coordinates')
    if not (0 <= x <= width - 1 and 0 <= y <= height - 1):
        raise ValueError('Coordinates outside image')
    return x / (width - 1), y / (height - 1)


def manifest():
    return json.loads((ROOT / 'data/sources.json').read_text(encoding='utf-8'))


def verified_image(source, root=ROOT):
    path = root / source['path']
    if not source.get('sha256') or sha256(path) != source['sha256']:
        raise ValueError('Image SHA-256 mismatch or missing lock: ' + str(path))
    with Image.open(path) as im:
        if list(im.size) != [source['width'], source['height']]:
            raise ValueError('Image dimension mismatch')
        if im.getexif().get(274, 1) != 1:
            raise ValueError('EXIF orientation requires an explicit transform')
        return im.convert('RGB')


def _timestamp(value):
    from datetime import datetime
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.utcoffset() is None or dt.utcoffset().total_seconds() != 0:
        raise ValueError('UTC timestamp required')
    return dt


def validate(rows, sources, release=False):
    errors = []
    seen = set()
    counts = dict(missing=0, draft=0, reviewed=0)
    for row in rows:
        gid, side = row['group_id'], row['side']
        prefix = gid + ': '
        if gid not in IDS or IDS.get(gid) != side:
            errors.append(prefix + 'unknown group or wrong side')
        if gid in seen:
            errors.append(prefix + 'duplicate group')
        seen.add(gid)
        status = row['status']
        if status not in counts:
            errors.append(prefix + 'unknown status')
            continue
        counts[status] += 1
        if status == 'missing':
            if any(row[k] for k in FIELDS if k not in ('group_id', 'side', 'status', 'note')):
                errors.append(prefix + 'missing row contains measurement metadata')
            if release:
                errors.append(prefix + 'missing measurement')
            continue
        try:
            source = sources[side]
            width, height = int(row['width']), int(row['height'])
            if (width, height) != (source['width'], source['height']):
                raise ValueError('dimensions differ from source')
            if not source.get('sha256') or row['image_sha256'] != source['sha256']:
                raise ValueError('source hash missing or mismatched')
            x, y, radius = (float(row[k]) for k in ('x_px', 'y_px', 'uncertainty_px'))
            normalized(x, y, width, height)
            if not math.isfinite(radius) or not 0 < radius <= math.hypot(width, height):
                raise ValueError('invalid uncertainty radius')
            for key in ('operator', 'mapping_reference', 'note'):
                if not row[key].strip():
                    raise ValueError('required ' + key)
            captured = _timestamp(row['captured_utc'])
            if status == 'reviewed':
                if not row['reviewer'].strip() or not row['review_note'].strip():
                    raise ValueError('reviewer and review note required')
                if row['reviewer'].strip().casefold() == row['operator'].strip().casefold():
                    raise ValueError('independent reviewer required')
                if _timestamp(row['reviewed_utc']) < captured:
                    raise ValueError('review predates capture')
            elif any(row[k] for k in ('reviewer', 'reviewed_utc', 'review_note')):
                raise ValueError('draft contains stale review metadata')
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(prefix + str(exc))
        if release and status != 'reviewed':
            errors.append(prefix + 'independent review outstanding')
    if seen != set(IDS):
        errors.append('group inventory differs: missing=' + ','.join(sorted(set(IDS) - seen)))
    return {'counts': counts, 'release_requested': release,
            'valid': not errors, 'errors': errors}


def capture(row, source, x, y, radius, operator, reference, note):
    from datetime import datetime, timezone
    result = dict(row)
    result.update(x_px=format(x, '.6f'), y_px=format(y, '.6f'),
                  uncertainty_px=format(radius, '.6f'), status='draft',
                  image_sha256=source['sha256'], width=str(source['width']),
                  height=str(source['height']), operator=operator.strip(),
                  mapping_reference=reference.strip(), note=note.strip(),
                  captured_utc=datetime.now(timezone.utc).isoformat(),
                  reviewer='', reviewed_utc='', review_note='')
    return result


def overlay(rows, side, source, output, root=ROOT):
    im = verified_image(source, root)
    draw = ImageDraw.Draw(im)
    for row in rows:
        if row['side'] != side or row['status'] == 'missing':
            continue
        x, y, r = (float(row[k]) for k in ('x_px', 'y_px', 'uncertainty_px'))
        color = '#00df80' if row['status'] == 'reviewed' else '#ff9c24'
        draw.ellipse((x-r, y-r, x+r, y+r), outline=color, width=3)
        draw.line((x-8, y, x+8, y), fill=color, width=3)
        draw.line((x, y-8, x, y+8), fill=color, width=3)
        draw.text((x+12, y+12), row['group_id'], fill=color, stroke_width=2,
                  stroke_fill='black', font_size=26)
    missing = sum(r['side'] == side and r['status'] == 'missing' for r in rows)
    draw.rectangle((0, 0, im.width, 100), fill='black')
    draw.text((15, 10), f'PHAISTOS {side} | missing {missing} | image-space only',
              fill='white', font_size=25)
    draw.text((15, 47), 'C messier / Wikimedia Commons / CC BY-SA 4.0; overlay added',
              fill='white', font_size=22)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    im.save(output)
