"""Synthetic fixtures only; no archaeological measurements."""
import copy
from pathlib import Path
import tempfile
import unittest
from PIL import Image
from phaistos.core import (FIELDS, IDS, normalized, validate, capture, read_rows,
                          write_rows, sha256, verified_image, overlay)


def blanks():
    return [dict.fromkeys(FIELDS, '') | {'group_id': gid, 'side': side, 'status': 'missing'}
            for gid, side in IDS.items()]


SOURCES = {side: dict(width=100, height=80, sha256='a'*64) for side in 'AB'}


def measured():
    rows = blanks()
    rows[0] = capture(rows[0], SOURCES['A'], 10, 20, 3, 'alice',
                      'synthetic-fixture-only', 'synthetic radius justification')
    return rows


class GeometryTests(unittest.TestCase):
    def test_pixel_extremes_and_y_down(self):
        self.assertEqual(normalized(0, 0, 100, 80), (0, 0))
        self.assertEqual(normalized(99, 79, 100, 80), (1, 1))
        self.assertEqual(normalized(49.5, 39.5, 100, 80), (.5, .5))

    def test_invalid_coordinates(self):
        for x, y in [(100, 20), (-1, 0), (0, 80), (float('nan'), 0), (0, float('inf'))]:
            with self.subTest(x=x, y=y), self.assertRaises(ValueError):
                normalized(x, y, 100, 80)

    def test_degenerate_dimensions(self):
        with self.assertRaises(ValueError):
            normalized(0, 0, 1, 80)


class DataTests(unittest.TestCase):
    def test_inventory_and_missing_release(self):
        report = validate(blanks(), SOURCES)
        self.assertTrue(report['valid'])
        self.assertEqual(report['counts']['missing'], 61)
        self.assertFalse(validate(blanks(), SOURCES, release=True)['valid'])

    def test_duplicate_missing_and_wrong_side(self):
        for change in ('duplicate', 'omit', 'side'):
            rows = blanks()
            if change == 'duplicate':
                rows[-1] = dict(rows[0])
            elif change == 'omit':
                rows.pop()
            else:
                rows[0]['side'] = 'B'
            self.assertFalse(validate(rows, SOURCES)['valid'])

    def test_draft_requires_source_and_uncertainty(self):
        self.assertTrue(validate(measured(), SOURCES)['valid'])
        for key, value in [('image_sha256', 'b'*64), ('uncertainty_px', 'NaN'),
                           ('uncertainty_px', '0'), ('width', '101'),
                           ('mapping_reference', ''), ('note', ''),
                           ('captured_utc', '2026-10-13T12:00:00')]:
            rows = measured()
            rows[0][key] = value
            with self.subTest(key=key, value=value):
                self.assertFalse(validate(rows, SOURCES)['valid'])

    def test_missing_is_not_zero_coordinate(self):
        rows = blanks()
        rows[0]['x_px'] = '0'
        self.assertFalse(validate(rows, SOURCES)['valid'])

    def test_independent_review_and_reset(self):
        rows = measured()
        row = rows[0]
        row.update(status='reviewed', reviewer='alice', review_note='synthetic check',
                   reviewed_utc=row['captured_utc'])
        self.assertFalse(validate(rows, SOURCES)['valid'])
        row['reviewer'] = 'bob'
        self.assertTrue(validate(rows, SOURCES)['valid'])
        row['reviewed_utc'] = '2000-01-01T00:00:00Z'
        self.assertFalse(validate(rows, SOURCES)['valid'])
        new = capture(row, SOURCES['A'], 11, 21, 4, 'alice', 'fixture', 'new synthetic capture')
        self.assertEqual(new['status'], 'draft')
        self.assertEqual(new['reviewer'], '')
        self.assertEqual(new['reviewed_utc'], '')

    def test_complete_release(self):
        rows = []
        for row in blanks():
            row = capture(row, SOURCES[row['side']], 10, 20, 3, 'alice', 'fixture', 'synthetic')
            row.update(status='reviewed', reviewer='bob', review_note='synthetic',
                       reviewed_utc=row['captured_utc'])
            rows.append(row)
        self.assertTrue(validate(rows, SOURCES, release=True)['valid'])

    def test_csv_roundtrip_and_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'groups.csv'
            rows = measured()
            rows[0]['note'] = 'synthetic, "quoted"\nsecond line'
            write_rows(path, rows)
            self.assertEqual(read_rows(path), rows)
            path.write_text('group_id,side\nA01,A\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                read_rows(path)

    def test_unexpected_status(self):
        rows = blanks()
        rows[0]['status'] = 'accepted'
        self.assertFalse(validate(rows, SOURCES)['valid'])


class ImageTests(unittest.TestCase):
    def test_image_lock_dimensions_and_overlay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root/'fixture.png'
            Image.new('RGB', (100, 80), 'white').save(path)
            source = dict(path='fixture.png', width=100, height=80, sha256=sha256(path))
            verified_image(source, root).close()
            output = root/'overlay.png'
            # A larger fixture leaves room below the attribution banner.
            Image.new('RGB', (600, 400), 'white').save(path)
            source.update(width=600, height=400, sha256=sha256(path))
            rows = blanks()
            rows[0] = capture(rows[0], source, 300, 200, 20, 'alice', 'fixture', 'synthetic')
            overlay(rows, 'A', source, output, root)
            with Image.open(output) as im:
                self.assertEqual(im.size, (600, 400))
                self.assertEqual(im.getpixel((300, 200)), (255, 156, 36))
                self.assertEqual(im.getpixel((500, 300)), (255, 255, 255))
            source['width'] = 601
            with self.assertRaises(ValueError):
                verified_image(source, root)
            source['width'] = 600
            source['sha256'] = 'b'*64
            with self.assertRaises(ValueError):
                verified_image(source, root)

    def test_exif_orientation_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'fixture.jpg'
            im = Image.new('RGB', (100, 80))
            exif = Image.Exif()
            exif[274] = 6
            im.save(path, exif=exif)
            source = dict(path='fixture.jpg', width=100, height=80, sha256=sha256(path))
            with self.assertRaises(ValueError):
                verified_image(source, Path(tmp))


if __name__ == '__main__':
    unittest.main()
