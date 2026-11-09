#!/usr/bin/env python3
"""Visual verification without a device.

Renders the generated .docx back to PDF and compares it against the source PDF,
line by line, plus structural checks for the patterns that break specific readers
(Google Docs in particular) even when LibreOffice renders them fine.

Usage:
    python3 verify_visual.py <source.pdf> <generated.docx> [--json]
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

import fitz  # PyMuPDF


# ---------------------------------------------------------------- structural

def structural(docx_path):
    """Patterns that a reader can trip over regardless of how the file renders here."""
    z = zipfile.ZipFile(docx_path)
    x = z.read('word/document.xml').decode('utf-8', 'replace')
    styles = ''
    if 'word/styles.xml' in z.namelist():
        styles = z.read('word/styles.xml').decode('utf-8', 'replace')

    checks = {}

    # A continuous section break becomes a page break in Google Docs.
    checks['continuous_sections'] = x.count('<w:type w:val="continuous"/>')
    checks['sections'] = x.count('<w:sectPr>')

    # w:cols is flow-based: Word decides where a column ends, so a paragraph can
    # move between columns. A column that must hold a position needs to be a cell.
    checks['column_sections'] = len(re.findall(r'<w:cols[^>]*w:num="([2-9])"', x))

    # A stamp inside a text box is not editable in Google Docs.
    checks['text_boxes'] = x.count('<wps:txbx>')

    # Shapes: each one is separately addressable, which is what stops drift.
    checks['shapes'] = x.count('<wps:wsp>')
    checks['shapes_with_rot'] = len(re.findall(r'<a:xfrm[^>]*\brot="', x))
    checks['shapes_consumed'] = x.count('<w:drawing>')

    # White-patch causes, measured against the commercial files.
    checks['shd_fills'] = len(re.findall(r'<w:shd[^>]*w:fill="[0-9A-Fa-f]{6}"', x))
    checks['scheme_clr'] = x.count('<a:schemeClr')
    checks['nofill'] = x.count('<a:noFill/>')
    checks['docdefaults_colour'] = 1 if re.search(r'docDefaults.*?<w:color', styles, re.S) else 0
    checks['has_settings'] = 1 if 'word/settings.xml' in z.namelist() else 0
    checks['has_background'] = 1 if '<w:background' in x else 0

    # Line weight and opacity, which the user reports as uniform.
    sz = re.findall(r'<w:(?:top|left|bottom|right|insideH|insideV)[^>]*w:sz="(\d+)"', x)
    checks['border_sz_distinct'] = len(set(sz))
    checks['border_sz_values'] = sorted(set(sz))
    ln_w = re.findall(r'<a:ln w="(\d+)"', x)
    checks['stroke_width_distinct'] = len(set(ln_w))
    checks['stroke_alpha'] = len(re.findall(r'<a:ln[^>]*>(?:(?!</a:ln>).)*<a:alpha', x, re.S))

    return checks


# -------------------------------------------------------------------- render

def render_docx(docx_path, outdir):
    """LibreOffice render of the .docx. Returns the PDF path or None."""
    cmd = ['soffice', '--headless', '--convert-to', 'pdf', '--outdir', outdir, docx_path]
    try:
        subprocess.run(cmd, capture_output=True, timeout=180, check=False)
    except Exception:
        return None
    base = os.path.splitext(os.path.basename(docx_path))[0] + '.pdf'
    out = os.path.join(outdir, base)
    return out if os.path.exists(out) else None


def lines_of(pdf_path):
    """Every text line with its baseline and extent, in reading order."""
    doc = fitz.open(pdf_path)
    out = []
    for pno, page in enumerate(doc):
        d = page.get_text('dict')
        for block in d.get('blocks', []):
            if block.get('type') != 0:
                continue
            for line in block.get('lines', []):
                text = ''.join(s.get('text', '') for s in line.get('spans', []))
                if not text.strip():
                    continue
                x0, y0, x1, y1 = line['bbox']
                out.append({'page': pno, 'x': round(x0, 1), 'y': round(y0, 1),
                            'x1': round(x1, 1), 'text': text.strip()})
    return out


def compare(src_pdf, rendered_pdf):
    """Per-line comparison of the render against the source."""
    a = lines_of(src_pdf)
    b = lines_of(rendered_pdf)
    res = {
        'pdf_pages': fitz.open(src_pdf).page_count,
        'docx_pages': fitz.open(rendered_pdf).page_count,
        'pdf_lines': len(a),
        'docx_lines': len(b),
    }
    res['page_delta'] = res['docx_pages'] - res['pdf_pages']

    # Match by text, then measure how far each matched line moved.
    from collections import defaultdict
    pool = defaultdict(list)
    for ln in b:
        pool[ln['text']].append(ln)

    dx, dy, matched = [], [], 0
    for ln in a:
        cands = pool.get(ln['text'])
        if not cands:
            continue
        best = min(cands, key=lambda c: abs(c['y'] - ln['y']) + abs(c['x'] - ln['x']))
        cands.remove(best)
        matched += 1
        dx.append(abs(best['x'] - ln['x']))
        dy.append(abs(best['y'] - ln['y']))

    # Reading order: walk the render in document order and ask how often the next line
    # is the one the PDF reads next. Position can be perfect while the order is wrong -
    # that is what makes a two-column page select as interleaved text.
    # Duplicate-aware. A document that repeats the same line - a timetable's DS, M-III and CO
    # dozens of times, an invoice's "Nos" eleven times - used to have every copy mapped to the
    # FIRST occurrence in the PDF, so its reading order could never exceed a low ceiling no matter
    # how right the output was: on 02_stamp_rotated_15deg_upleft the ceiling was 23 % and the
    # document was already at 90 %. Each render line is now matched to a DISTINCT PDF line, by
    # text and then by nearest y, so repeated text is consumed once per copy.
    from collections import defaultdict as _dd
    _pool = _dd(list)
    for _i, _ln in enumerate(a):
        _pool[_ln['text']].append(_i)
    seq = []
    for _ln in b:
        _cand = _pool.get(_ln['text'])
        if not _cand:
            continue
        _best = min(_cand, key=lambda _k: abs(a[_k]['y'] - _ln['y']))
        _cand.remove(_best)
        seq.append(_best)
    longest = 0
    cur = 0
    prev = -1
    for v in seq:
        cur = cur + 1 if v > prev else 1
        prev = v
        longest = max(longest, cur)
    res['order_share'] = round(longest / len(seq), 3) if seq else 0.0

    res['matched'] = matched
    res['match_share'] = round(matched / len(a), 3) if a else 0.0
    if dx:
        dx.sort(); dy.sort()
        res['dx_median'] = round(dx[len(dx) // 2], 1)
        res['dy_median'] = round(dy[len(dy) // 2], 1)
        res['dx_worst'] = round(dx[-1], 1)
        res['dy_worst'] = round(dy[-1], 1)
        res['within_3pt'] = round(sum(1 for v in dy if v <= 3) / len(dy), 3)
        res['within_10pt'] = round(sum(1 for v in dy if v <= 10) / len(dy), 3)
    return res


# ------------------------------------------------------------------- verdict

def verdict(struct, cmp_):
    """What is wrong, in plain words. Empty list means clean."""
    bad = []
    if cmp_.get('page_delta', 0) > 0:
        bad.append('extra %d page(s): pdf %d, docx %d'
                   % (cmp_['page_delta'], cmp_['pdf_pages'], cmp_['docx_pages']))
    if struct['continuous_sections']:
        bad.append('%d continuous section break(s) - Google Docs turns these into page breaks'
                   % struct['continuous_sections'])
    if struct['column_sections']:
        bad.append('%d multi-column section(s) - w:cols is flow-based, so paragraphs can move '
                   'between columns' % struct['column_sections'])
    if struct['text_boxes']:
        bad.append('%d text box(es) - not editable in Google Docs' % struct['text_boxes'])
    if struct['shd_fills']:
        bad.append('%d explicit shading fill(s) - a white patch in dark mode' % struct['shd_fills'])
    if struct['scheme_clr']:
        bad.append('%d schemeClr reference(s) - neutralised in Google Docs' % struct['scheme_clr'])
    if struct['docdefaults_colour']:
        bad.append('a colour inside docDefaults - removes the dark-mode adaptation hook')
    if not struct['has_settings']:
        bad.append('no word/settings.xml')
    if struct['has_background']:
        bad.append('a page background - suppresses Word\'s automatic dark page')
    if struct['border_sz_distinct'] <= 1 and struct['border_sz_values']:
        bad.append('all %d border sides share one weight %s - the page may rule them differently'
                   % (len(struct['border_sz_values']), struct['border_sz_values']))
    if cmp_.get('match_share', 0) < 0.95:
        bad.append('only %.0f%% of pdf lines found in the render' % (100 * cmp_['match_share']))
    if cmp_.get('within_10pt', 1) < 0.90:
        bad.append('only %.0f%% of lines within 10 pt vertically'
                   % (100 * cmp_.get('within_10pt', 0)))
    if cmp_.get('order_share', 1) < 0.90:
        bad.append('reading order: the longest run in pdf order is only %.0f%% of the lines - '
                   'side-by-side text is interleaved' % (100 * cmp_.get('order_share', 0)))
    return bad


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    src, docx = sys.argv[1], sys.argv[2]
    as_json = '--json' in sys.argv

    struct = structural(docx)
    with tempfile.TemporaryDirectory() as td:
        rendered = render_docx(docx, td)
        if rendered is None:
            print('RENDER FAILED - LibreOffice could not convert the docx')
            return 1
        cmp_ = compare(src, rendered)
    bad = verdict(struct, cmp_)

    if as_json:
        print(json.dumps({'structural': struct, 'compare': cmp_, 'problems': bad}, indent=1))
        return 0 if not bad else 1

    print('=' * 70)
    print(os.path.basename(src))
    print('  pages   pdf %d  docx %d %s'
          % (cmp_['pdf_pages'], cmp_['docx_pages'],
             '' if cmp_['page_delta'] == 0 else '  <-- %+d' % cmp_['page_delta']))
    print('  lines   pdf %d  docx %d   matched %.0f%%'
          % (cmp_['pdf_lines'], cmp_['docx_lines'], 100 * cmp_['match_share']))
    if 'dy_median' in cmp_:
        print('  move    median dx %.1f pt  dy %.1f pt   worst dy %.1f pt'
              % (cmp_['dx_median'], cmp_['dy_median'], cmp_['dy_worst']))
        print('  within 3 pt %.0f%%   10 pt %.0f%%   reading order %.0f%%'
              % (100 * cmp_['within_3pt'], 100 * cmp_['within_10pt'],
                 100 * cmp_.get('order_share', 0)))
    print('  struct  sections %d (continuous %d)  cols %d  txbx %d  shapes %d'
          % (struct['sections'], struct['continuous_sections'],
             struct['column_sections'], struct['text_boxes'], struct['shapes']))
    print('  colour  shd %d  schemeClr %d  docDefaultsColour %d  settings %d  bg %d'
          % (struct['shd_fills'], struct['scheme_clr'], struct['docdefaults_colour'],
             struct['has_settings'], struct['has_background']))
    print('  stroke  border sz %s  distinct stroke widths %d  with alpha %d'
          % (struct['border_sz_values'], struct['stroke_width_distinct'], struct['stroke_alpha']))
    if bad:
        print('  PROBLEMS:')
        for b in bad:
            print('    - ' + b)
    else:
        print('  clean')
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
