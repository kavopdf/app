# Stamps are textboxes, and that is why some are editable and some are not

The user reported two things from two screenshots on 26 Nov:

1. A stamp's outline and the text inside it are not aligned. Already known, not a surprise.
2. **Some .docx stamps are editable and some are not.** Called out as the more concerning of the two.

## Measured, on the corpus that is on the pod

    213 documents in /scratch/work/p2w/out
     47 carry a textbox          (wps:txbx > 0)
     17 carry a rot or vert attribute
     30 carry a textbox and no rot/vert at all

The twelve stamp documents kept in the shared store, counted one by one:

    document                                    txbx  rot  vert  draw
    01_stamp_LO.docx                             166    2     0    93
    01_stamp_OURS.docx                             2    1     0    11
    01_stamp_rotated_15deg_upright.docx            2    1     0    11
    02_stamp_current.docx                          0    0     0    11
    02_stamp_rotated_15deg_upleft.docx             4    0     0    23
    03_stamp_vertical_90deg.docx                   6    0     0    24
    08_two_overlapping_stamps.docx                 8    0     0     9
    12-01_stamp_rotated_15deg_upright.docx         2    1     0    11
    12-02_stamp_rotated_15deg_upleft.docx          2    1     0    10
    base-02_stamp_rotated_15deg_upleft.docx        2    1     0    10
    lo-02_stamp_rotated_15deg_upleft.docx        176    2     0   104
    stamp03.docx                                   2    0     0    22

Eleven of the twelve carry a textbox. One does not.

## What that means, and it is already proved

FINDINGS/TXBX-CAN-BE-REPLACED-BY-FLOW-TEXT-PROVEN-25NOV.md records five Google round-trips: Google
rasterises `w:txbxContent`. A stamp inside a textbox reaches Google as a picture, which is why it cannot
be edited in Docs. A stamp written as ordinary runs stays text and can.

So the editable / not-editable split the user is seeing is very likely the textbox split, and the
population is 47 of 213 rather than the stamp documents alone - any document with a textbox carries the
same defect, not only the ones whose text is a stamp.

**This is a hypothesis with a measured population, not a proved cause.** It is proved for textboxes in
general and it is not yet proved for these particular stamps, because nothing here has been exported to
Google and read back. The next run must do that before changing anything: pick one of the eleven, export
it, open the Google Doc, and try to put the cursor inside the stamp. If the cursor goes in, the textbox
is not the cause and this file is wrong.

## The alignment half, and a second thing found while counting

`03_stamp_vertical_90deg.docx` carries **6 textboxes and not one rot or vert attribute**, while
`01_stamp_rotated_15deg_upright.docx` carries **1 rot**. The user's second screenshot shows the 15-degree
stamp with its text crossing the box's top-left edge, and the first shows the vertical stamp with two
separate rectangles and the text between them.

30 documents in the corpus carry a textbox and no rotation attribute at all. A stamp that is meant to be
rotated and carries no transform cannot be rotated by the renderer, and a box and its text drawn as two
objects with two different transforms cannot line up. That is the shape the two screenshots show.

Neither half has been fixed here. Nothing was changed. The numbers above are the whole of this file.
