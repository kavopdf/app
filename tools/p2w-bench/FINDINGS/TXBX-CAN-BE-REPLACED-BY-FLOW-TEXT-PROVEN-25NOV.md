
## Test 3 — does Google re-sample an embedded image, or keep its resolution?

One document, two PNGs of the same text, both placed in a 2.00 inch box:

    96 dpi source   192 x 57 px
    300 dpi source  600 x 180 px

After the Google Doc round-trip, read out of Google's own PDF export:

    image 0: 192x57 px    placed at 144.0 x 43.5 pt  (2.00 inch)  =  96 dpi effective
    image 1: 600x180 px   placed at 144.0 x 43.5 pt  (2.00 inch)  = 300 dpi effective

**Google keeps both at their source resolution and neither is re-sampled.** A 300 dpi stamp stays a
300 dpi stamp after import, so zooming into it does not pixelate — the pixels are there. A 96 dpi stamp
stays 96 dpi and pixelates exactly as it did before.

So the pixelation half of the stamp problem is not a Google behaviour to work around. It is a source
choice: rasterise the stamp at 300 dpi and Google will carry it.
