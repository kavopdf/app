# "White patches" are content that never reached the render. Nothing in the docx paints white.

## What was ruled out, by measurement

Every construct that can paint white, counted across all 213 documents in `word/document.xml`:

    w:shd w:fill="auto"         0
    w:shd w:fill="FFFFFF"       0
    <w:highlight w:val="white"> 0
    <a:schemeClr val="bg1">     0
    <a:srgbClr val="FFFFFF">    0
    fillcolor="white"  (VML)    0
    <w:background>              0
    <w:pgBorders>               0
    <w:pBdr>                    0

Zero, in every one of the nine patterns. And the fills that do exist are all dark:

    000000  5992 instances    2A2076  4694    C9C9C9   271
    231F20   176             111111   130    9B9B9B   103

There is no white fill anywhere in the corpus.

The rasterised textbox was checked too: the image Google produces for a shape carries **0.0 % white
pixels**. It is transparent, not a white plate.

## What it actually is

The page is white. Content that is absent from the render therefore reads as a white patch. Measured by
comparing source ink against render ink, page one, 80 dpi, on 60 documents:

    041122-Account_Opening_Form     97.5 % of source ink absent from the render
    318_court_summons_form          69.6 %
    313_power_of_attorney           67.2 %
    317_rti_response                66.4 %
    310_court_judgment              66.3 %
    316_contract_with_schedules     65.5 %
    312_affidavit_stamp_paper       65.0 %
    311_fir_police_form             61.2 %

    16 of 60 documents lose more than half their ink
     1 of 60 loses less than a tenth

So this is not a colour problem and not an overpaint problem. It is the same failure the textbox work has
been chasing all along, seen from the reader's side: text that lived inside a shape did not come through.

## Why the first measurement pointed the wrong way

`01_stamp_rotated_15deg_upright` showed 38.8 % of its source ink missing but 54 % *extra* ink elsewhere —
the render carried more ink than the source. That document is displaced, not emptied. Reading one document
and generalising would have produced the wrong diagnosis; the 60-document scan is what separates
"moved" from "absent".

## What follows

Fixing the textbox construct is not one of the possible fixes for this — it is the fix, and the 97.5 %
figure says how much rides on it for the worst document. `041122-Account_Opening_Form` carries 189
textboxes and loses almost all of its content.

## Reproduce

    python3 - <<'PY'
    import pymupdf, numpy as np
    s=pymupdf.open('/scratch/work/p2w/corpus/041122-Account_Opening_Form.pdf')[0]
    g=pymupdf.open('/scratch/work/renders25/041122-Account_Opening_Form.pdf')[0]
    ink=lambda p:(np.frombuffer((lambda x:x.get_pixmap(dpi=80).samples)(p),dtype=np.uint8)
                  .reshape(p.get_pixmap(dpi=80).height,p.get_pixmap(dpi=80).width,p.get_pixmap(dpi=80).n)[:,:,:3].mean(axis=2)<200)
    A,B=ink(s),ink(g); h=min(A.shape[0],B.shape[0]); w=min(A.shape[1],B.shape[1])
    print((A[:h,:w]&~B[:h,:w]).sum()/A[:h,:w].sum())
    PY
