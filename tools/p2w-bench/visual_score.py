#!/usr/bin/env python3
"""Score every document on how closely its .docx matches its PDF.

Runs verify_visual's three measures over a whole corpus and prints the worst
documents first, so a drift that is universal shows up as a number instead of a
complaint.

    python3 visual_score.py --corpus <pdfdir> --out <docxdir> [--top 20] [--json path]

Columns:
    dy_med   median vertical distance between a PDF line and the same line in the render
    dy_worst worst vertical distance
    w3       share of lines within 3 pt vertically
    w10      share of lines within 10 pt
    order    longest run of lines in PDF reading order, as a share - a low number here
             with a high w3 means the positions are right and the ORDER is wrong,
             which is what "paragraphs are mixed" means
    corr     correlation between a line's y and its error. Above 0.5 in absolute value
             means the error accumulates down the page
    pages    pdf pages -> docx pages
"""
import argparse
import glob
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify_visual as V


def correlation(rows):
    n = len(rows)
    if n < 5:
        return 0.0
    my = sum(y for y, _ in rows) / n
    md = sum(d for _, d in rows) / n
    cov = sum((y - my) * (d - md) for y, d in rows)
    sy = (sum((y - my) ** 2 for y, _ in rows)) ** 0.5
    sd = (sum((d - md) ** 2 for _, d in rows)) ** 0.5
    return cov / (sy * sd) if sy and sd else 0.0


def score_one(pdf_path, docx_path, tmpdir):
    struct = V.structural(docx_path)
    rendered = V.render_docx(docx_path, tmpdir)
    if rendered is None:
        return None
    cmp_ = V.compare(pdf_path, rendered)

    # correlation between position and error, on the matched pairs
    from collections import defaultdict
    a = V.lines_of(pdf_path)
    b = V.lines_of(rendered)
    pool = defaultdict(list)
    for ln in b:
        pool[ln['text']].append(ln)
    rows = []
    for ln in a:
        c = pool.get(ln['text'])
        if not c:
            continue
        best = min(c, key=lambda q: abs(q['y'] - ln['y']))
        c.remove(best)
        rows.append((ln['y'], best['y'] - ln['y']))
    corr = correlation(rows)

    return {
        'dy_med': cmp_.get('dy_median', 0.0),
        'dy_worst': cmp_.get('dy_worst', 0.0),
        'dx_med': cmp_.get('dx_median', 0.0),
        'w3': cmp_.get('within_3pt', 0.0),
        'w10': cmp_.get('within_10pt', 0.0),
        'order': cmp_.get('order_share', 0.0),
        'corr': round(corr, 2),
        'pages': '%d->%d' % (cmp_['pdf_pages'], cmp_['docx_pages']),
        'page_delta': cmp_['page_delta'],
        'lines': cmp_['pdf_lines'],
        'matched': cmp_['match_share'],
        'continuous': struct['continuous_sections'],
        'cols': struct['column_sections'],
        'txbx': struct['text_boxes'],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--corpus', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--top', type=int, default=25)
    ap.add_argument('--json', default='')
    args = ap.parse_args()

    pdfs = sorted(glob.glob(os.path.join(args.corpus, '*.pdf')))
    rows = []
    with tempfile.TemporaryDirectory() as td:
        for i, pdf in enumerate(pdfs, 1):
            name = os.path.splitext(os.path.basename(pdf))[0]
            docx = os.path.join(args.out, name + '.docx')
            if not os.path.exists(docx):
                continue
            try:
                s = score_one(pdf, docx, td)
            except Exception as e:
                print('  ! %s: %s' % (name, e), file=sys.stderr)
                continue
            if s is None:
                continue
            s['name'] = name
            rows.append(s)
            if i % 25 == 0:
                print('  %d/%d' % (i, len(pdfs)), file=sys.stderr)

    if not rows:
        print('nothing scored')
        return 1

    n = len(rows)
    clean3 = sum(1 for r in rows if r['w3'] >= 0.90)
    clean10 = sum(1 for r in rows if r['w10'] >= 0.90)
    order_ok = sum(1 for r in rows if r['order'] >= 0.90)
    pages_ok = sum(1 for r in rows if r['page_delta'] == 0)
    cumul = [r for r in rows if abs(r['corr']) > 0.5]
    med_all = sorted(r['dy_med'] for r in rows)[n // 2]

    print()
    print('=' * 78)
    print('VISUAL SCORE - %d documents' % n)
    print('  median of medians      %.1f pt' % med_all)
    print('  pages match the PDF    %d / %d' % (pages_ok, n))
    print('  within 3 pt  (>=90%%)   %d / %d' % (clean3, n))
    print('  within 10 pt (>=90%%)   %d / %d' % (clean10, n))
    print('  reading order (>=90%%)  %d / %d' % (order_ok, n))
    print('  cumulative drift       %d documents with |corr| > 0.5' % len(cumul))
    print('=' * 78)

    rows.sort(key=lambda r: (r['w10'], r['order'], -abs(r['dy_med'])))
    print()
    print('%-44s %6s %7s %5s %5s %5s %5s %8s' %
          ('worst documents', 'dy_med', 'dy_wr', 'w3', 'w10', 'order', 'corr', 'pages'))
    for r in rows[:args.top]:
        print('%-44s %6.1f %7.1f %4.0f%% %4.0f%% %4.0f%% %+5.2f %8s'
              % (r['name'][:44], r['dy_med'], r['dy_worst'], 100 * r['w3'],
                 100 * r['w10'], 100 * r['order'], r['corr'], r['pages']))

    if args.json:
        with open(args.json, 'w') as f:
            json.dump(rows, f, indent=1)
        print('\nwritten to %s' % args.json)
    return 0


if __name__ == '__main__':
    sys.exit(main())
