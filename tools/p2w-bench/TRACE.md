# Trace - what the tools were actually asked to do

Written by the tools themselves, not by the run. A run that dies mid-way leaves its
path here, which is the one thing the run's own report cannot do. Commit it with the
claim and after each step; it is not code and cannot break anything.

| time | run | tool | what happened |
|---|---|---|---|
| 12 Nov 18:41 | fixer | claim | fixer claimed the slot |
| 12 Nov 18:42 | fixer | build-engine | started |
| 12 Nov 18:43 | fixer | classify | 43 classes from 208 documents |
| 12 Nov 18:43 | fixer | classify --txt | 4 classes from 208 documents |
| 12 Nov 18:46 | fixer | build-engine | started |
| 12 Nov 18:46 | fixer | build-engine | started |
| 12 Nov 18:47 | fixer | build-engine | started |
| 12 Nov 18:52 | fixer | ratchet | held or rose |
| 12 Nov 18:52 | fixer | ratchet --txt | held or rose |
| 12 Nov 18:52 | fixer | hypothesis | 20_within_10pt (+4) -> confirmed |
| 12 Nov 18:52 | fixer | hypothesis | 20_within_10pt (+4) -> ruled-out |
| 12 Nov 18:52 | fixer | hypothesis | 20_within_10pt (+4) -> untested |
| 12 Nov 18:52 | fixer | classify | 43 classes from 208 documents |
| 12 Nov 18:52 | fixer | ratchet | held or rose |
| 12 Nov 18:52 | fixer | ratchet --txt | held or rose |
| 12 Nov 18:52 | fixer | attempt | 20_within_10pt (+4) -> reverted (OPEN) |
| 12 Nov 18:52 | fixer | classify | 43 classes from 208 documents |
| 12 Nov 18:52 | ? | commit-gate | started |
| 12 Nov 19:46 | fixer | claim | fixer claimed the slot |
| 12 Nov 19:46 | fixer | classify | 43 classes from 208 documents |
| 12 Nov 19:46 | fixer | classify --txt | 4 classes from 208 documents |
| 12 Nov 19:47 | fixer | build-engine | started |
| 12 Nov 19:48 | fixer | build-engine | started |
| 12 Nov 19:52 | fixer | hypothesis | 53_embedded_faces -> ruled-out |
| 12 Nov 19:52 | ? | classify | 43 classes from 208 documents |
| 12 Nov 19:52 | ? | classify | 43 classes from 208 documents |
| 12 Nov 20:43 | fixer | claim | fixer claimed the slot |
| 12 Nov 20:44 | fixer | build-engine | started |
| 12 Nov 20:45 | fixer | classify | 43 classes from 208 documents |
| 12 Nov 20:45 | fixer | classify --txt | 4 classes from 208 documents |
| 12 Nov 20:49 | fixer | hypothesis | 20_within_10pt (+4) -> ruled-out |
| 12 Nov 20:49 | fixer | hypothesis | 20_within_10pt (+4) -> untested |
| 12 Nov 20:49 | fixer | attempt | 20_within_10pt (+4) -> error (OPEN) |
| 12 Nov 20:49 | fixer | classify | 43 classes from 208 documents |
| 12 Nov 20:49 | fixer | classify --txt | 4 classes from 208 documents |
| 12 Nov 20:50 | ? | commit-gate | started |
| 12 Nov 21:47 | fixer | claim | fixer claimed the slot |
| 12 Nov 21:47 | fixer | build-engine | started |
| 12 Nov 21:48 | fixer | classify | 43 classes from 208 documents |
| 12 Nov 21:48 | fixer | classify --txt | 4 classes from 208 documents |
| 12 Nov 21:51 | fixer | build-engine | started |
| 12 Nov 21:54 | fixer | hypothesis | 20_within_10pt (+4) -> confirmed |
| 12 Nov 21:54 | fixer | hypothesis | 20_within_10pt (+4) -> confirmed |
| 12 Nov 21:54 | fixer | attempt | 20_within_10pt (+4) -> error (OPEN) |
| 12 Nov 21:54 | fixer | classify | 43 classes from 208 documents |
| 12 Nov 21:54 | ? | commit-gate | started |
| 12 Nov 22:46 | fixer | claim | fixer claimed the slot |
| 12 Nov 22:46 | fixer | build-engine | started |
| 12 Nov 22:48 | fixer | build-engine | started |
| 12 Nov 22:52 | fixer | hypothesis | 20_within_10pt (+4) -> confirmed |
| 12 Nov 22:52 | fixer | attempt | 20_within_10pt (+4) -> error (OPEN) |
| 12 Nov 22:52 | fixer | classify | 43 classes from 208 documents |
| 12 Nov 23:48 | fixer | claim | fixer claimed the slot |
| 12 Nov 23:49 | fixer | build-engine | started |
| 12 Nov 23:50 | fixer | classify | 43 classes from 208 documents |
| 12 Nov 23:50 | fixer | build-engine | started |
| 13 Nov 00:00 | fixer | ratchet | held or rose |
| 13 Nov 00:00 | fixer | ratchet --txt | held or rose |
| 13 Nov 00:00 | fixer | hypothesis | 20_within_10pt (+4) -> confirmed |
| 13 Nov 00:00 | fixer | attempt | 20_within_10pt (+4) -> error (OPEN) |
| 13 Nov 00:00 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 00:00 | ? | commit-gate | started |
| 13 Nov 00:46 | fixer | claim | fixer claimed the slot |
| 13 Nov 00:47 | fixer | build-engine | started |
| 13 Nov 00:48 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 00:48 | fixer | classify --txt | 4 classes from 208 documents |
| 13 Nov 00:48 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 00:53 | fixer | ratchet | held or rose |
| 13 Nov 00:53 | fixer | ratchet --txt | held or rose |
| 13 Nov 00:53 | fixer | ratchet | REGRESSED 4 |
| 13 Nov 00:53 | fixer | hypothesis | 20_within_10pt (+4) -> confirmed |
| 13 Nov 00:53 | fixer | hypothesis | 20_within_10pt (+4) -> ruled-out |
| 13 Nov 00:53 | fixer | hypothesis | 20_within_10pt (+4) -> untested |
| 13 Nov 00:53 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 00:54 | fixer | attempt | 20_within_10pt (+4) -> reverted (OPEN) |
| 13 Nov 00:54 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 00:54 | fixer | build-engine | started |
| 13 Nov 00:57 | fixer | hypothesis | 20_within_10pt (+4) -> ruled-out |
| 13 Nov 00:57 | fixer | hypothesis | 20_within_10pt (+4) -> confirmed |
| 13 Nov 00:58 | fixer | attempt | 20_within_10pt (+4) -> error (OPEN) |
| 13 Nov 00:58 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 00:58 | ? | commit-gate | started |
| 13 Nov 01:45 | fixer | claim | fixer claimed the slot |
| 13 Nov 01:45 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 01:45 | fixer | classify --txt | 4 classes from 208 documents |
| 13 Nov 01:45 | fixer | build-engine | started |
| 13 Nov 01:47 | fixer | build-engine | started |
| 13 Nov 01:49 | fixer | hypothesis | 20_within_10pt (+4) -> ruled-out |
| 13 Nov 01:49 | fixer | hypothesis | 20_within_10pt (+4) -> untested |
| 13 Nov 01:49 | fixer | attempt | 20_within_10pt (+4) -> reverted (OPEN) |
| 13 Nov 01:49 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 02:50 | fixer | claim | fixer claimed the slot |
| 13 Nov 02:51 | fixer | build-engine | started |
| 13 Nov 02:54 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 02:54 | fixer | hypothesis | 47_margins -> confirmed |
| 13 Nov 02:54 | fixer | hypothesis | 47_margins -> confirmed |
| 13 Nov 02:54 | fixer | hypothesis | 47_margins -> untested |
| 13 Nov 02:54 | fixer | attempt | 47_margins -> error (OPEN) |
| 13 Nov 03:44 | fixer | claim | fixer claimed the slot |
| 13 Nov 03:44 | fixer | build-engine | started |
| 13 Nov 03:45 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 03:45 | fixer | classify --txt | 4 classes from 208 documents |
| 13 Nov 03:45 | fixer | attempt | 47_margins -> error (OPEN) |
| 13 Nov 03:46 | fixer | build-engine | started |
| 13 Nov 03:48 | fixer | hypothesis | 47_margins -> ruled-out |
| 13 Nov 03:48 | fixer | hypothesis | 47_margins -> ruled-out |
| 13 Nov 03:48 | fixer | hypothesis | 47_margins -> confirmed |
| 13 Nov 03:48 | fixer | attempt | 47_margins -> reverted (OPEN) |
| 13 Nov 04:40 | fixer | claim | fixer claimed the slot |
| 13 Nov 04:41 | fixer | build-engine | started |
| 13 Nov 04:41 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 04:43 | fixer | hypothesis | 20_within_10pt (+4) -> confirmed |
| 13 Nov 04:43 | fixer | hypothesis | 20_within_10pt (+4) -> confirmed |
| 13 Nov 04:43 | fixer | hypothesis | 20_within_10pt (+4) -> untested |
| 13 Nov 04:43 | fixer | attempt | 20_within_10pt (+4) -> error (OPEN) |
| 13 Nov 04:43 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 04:43 | ? | commit-gate | started |
| 13 Nov 05:41 | fixer | claim | fixer claimed the slot |
| 13 Nov 05:41 | fixer | build-engine | started |
| 13 Nov 05:42 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 05:42 | fixer | classify --txt | 4 classes from 208 documents |
| 13 Nov 05:44 | fixer | hypothesis | 20_within_10pt (+4) -> ruled-out |
| 13 Nov 05:44 | fixer | hypothesis | 20_within_10pt (+4) -> untested |
| 13 Nov 05:44 | fixer | attempt | 20_within_10pt (+4) -> error (OPEN) |
| 13 Nov 05:44 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 05:44 | ? | commit-gate | started |
| 13 Nov 05:44 | ? | commit-gate | started |
| 13 Nov 06:47 | fixer | claim | fixer claimed the slot |
| 13 Nov 06:48 | fixer | build-engine | started |
| 13 Nov 06:50 | fixer | build-engine | started |
| 13 Nov 06:55 | fixer | ratchet | held or rose |
| 13 Nov 06:55 | fixer | ratchet | held or rose |
| 13 Nov 06:55 | fixer | ratchet | REGRESSED 6 |
| 13 Nov 06:56 | fixer | hypothesis | 20_within_10pt (+4) -> confirmed |
| 13 Nov 06:56 | fixer | hypothesis | 20_within_10pt (+4) -> ruled-out |
| 13 Nov 06:56 | fixer | hypothesis | 20_within_10pt (+4) -> untested |
| 13 Nov 06:56 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 06:56 | fixer | attempt | 20_within_10pt (+4) -> reverted (OPEN) |
| 13 Nov 06:56 | fixer | ratchet | held or rose |
| 13 Nov 06:56 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 06:56 | ? | commit-gate | started |
| 13 Nov 06:57 | fixer | claim | fixer claimed the slot |
| 13 Nov 06:57 | fixer | build-engine | started |
| 13 Nov 07:00 | fixer | ratchet | REGRESSED 7 |
| 13 Nov 07:00 | fixer | hypothesis | 20_within_10pt (+4) -> ruled-out |
| 13 Nov 07:00 | fixer | hypothesis | 20_within_10pt (+4) -> untested |
| 13 Nov 07:00 | fixer | attempt | 20_within_10pt (+4) -> reverted (OPEN) |
| 13 Nov 07:00 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 07:00 | fixer | commit-gate | started |
| 13 Nov 07:00 | ? | commit-gate | started |
| 13 Nov 07:40 | fixer | claim | fixer claimed the slot |
| 13 Nov 07:40 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 07:40 | fixer | classify --txt | 4 classes from 208 documents |
| 13 Nov 07:40 | fixer | build-engine | started |
| 13 Nov 07:43 | fixer | hypothesis | 20_within_10pt (+4) -> ruled-out |
| 13 Nov 07:43 | fixer | hypothesis | 20_within_10pt (+4) -> confirmed |
| 13 Nov 07:43 | fixer | hypothesis | 20_within_10pt (+4) -> untested |
| 13 Nov 07:43 | fixer | attempt | 20_within_10pt (+4) -> error (OPEN) |
| 13 Nov 07:43 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 07:43 | ? | commit-gate | started |
| 13 Nov 08:40 | fixer | claim | fixer claimed the slot |
| 13 Nov 08:41 | fixer | build-engine | started |
| 13 Nov 08:43 | fixer | build-engine | started |
| 13 Nov 08:45 | fixer | hypothesis | 20_within_10pt (+4) -> ruled-out |
| 13 Nov 08:45 | fixer | attempt | 20_within_10pt (+4) -> error (OPEN) |
| 13 Nov 08:45 | fixer | ratchet | held or rose |
| 13 Nov 08:45 | ? | commit-gate | started |
| 13 Nov 09:45 | fixer | claim | fixer claimed the slot |
| 13 Nov 09:46 | fixer | build-engine | started |
| 13 Nov 09:53 | fixer | ratchet | REGRESSED 2 |
| 13 Nov 09:54 | fixer | ratchet | REGRESSED 2 |
| 13 Nov 09:54 | fixer | ratchet | REGRESSED 2 |
| 13 Nov 09:54 | fixer | hypothesis | 53_embedded_faces -> confirmed |
| 13 Nov 09:55 | fixer | attempt | 53_embedded_faces -> error (OPEN) |
| 13 Nov 09:55 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 09:55 | fixer | classify --txt | 4 classes from 208 documents |
| 13 Nov 09:55 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 09:55 | fixer | commit-gate | started |
| 13 Nov 09:56 | fixer | hypothesis | 32_stroke_lines -> untested |
| 13 Nov 09:56 | fixer | attempt | 32_stroke_lines -> error (OPEN) |
| 13 Nov 09:56 | fixer | classify | 43 classes from 208 documents |
| 13 Nov 09:56 | fixer | hypothesis | 32_stroke_lines -> untested |
| 13 Nov 09:56 | ? | commit-gate | started |
| 13 Nov 11:24 | classifier | claim | classifier claimed the slot |
| 13 Nov 11:24 | classifier | classify | 45 classes from 211 documents |
| 13 Nov 11:24 | classifier | classify --txt | 4 classes from 211 documents |
| 13 Nov 11:24 | classifier | ratchet --txt | held or rose |
| 13 Nov 11:24 | classifier | ratchet | held or rose |
| 13 Nov 11:59 | ? | ratchet | REGRESSED 191 |
| 13 Nov 11:59 | ? | ratchet | REGRESSED 191 |
| 13 Nov 11:59 | ? | ratchet | REGRESSED 191 |
| 13 Nov 11:59 | ? | ratchet | held or rose |
| 13 Nov 11:59 | ? | ratchet | held or rose |
| 13 Nov 11:59 | ? | ratchet | REGRESSED 1 |
| 13 Nov 11:59 | ? | ratchet | REGRESSED 1 |
| 13 Nov 11:59 | ? | ratchet | held or rose |
| 13 Nov 11:59 | ? | ratchet | held or rose |
| 13 Nov 13:25 | ? | ratchet | held or rose |
| 13 Nov 13:25 | ? | ratchet | held or rose |
| 13 Nov 14:17 | ? | ratchet | held or rose |
| 13 Nov 14:46 | ? | ratchet | FAIL DRIFT 211 rows/211 marks; STALE 211 |
| 13 Nov 14:46 | ? | ratchet | NOT COMPARED (--allow-stale) DRIFT 211 rows/211 marks; STALE 211 |
| 13 Nov 14:46 | ? | ratchet --txt | held or rose |
| 13 Nov 14:51 | ? | ratchet | FAIL DRIFT 211 rows/211 marks; STALE 211 |
| 14 Nov 15:57 | ? | build-engine | started |
| 14 Nov 15:57 | ? | build-engine | started |
| 14 Nov 15:58 | ? | build-engine | started |
| 14 Nov 15:59 | ? | build-engine | started |
| 14 Nov 16:04 | ? | build-engine | started |
| 14 Nov 21:41 | ? | build-engine | started |
| 14 Nov 21:45 | ? | build-engine | started |
| 14 Nov 21:58 | ? | build-engine | started |
| 14 Nov 22:16 | ? | build-engine | started |
| 14 Nov 22:40 | ? | build-engine | started |
| 16 Nov 06:07 | baseline | claim | baseline claimed the slot |
| 16 Nov 07:46 | classifier | claim | classifier claimed the slot |
| 16 Nov 07:48 | fixer | claim | fixer claimed the slot |
| 16 Nov 07:49 | fixer | build-engine | started |
| 16 Nov 07:59 | fixer | build-engine | started |
| 16 Nov 08:04 | fixer | commit-gate | started |
| 16 Nov 08:53 | fixer | claim | fixer claimed the slot |
| 16 Nov 08:53 | fixer | stale-claim | fixer slot was stale (65 min) - the previous run ended without releasing it |
| 16 Nov 08:54 | fixer | build-engine | started |
| 16 Nov 09:54 | fixer | claim | fixer claimed the slot |
| 16 Nov 09:55 | fixer | build-engine | started |
| 16 Nov 09:56 | fixer | build-engine | started |
| 16 Nov 09:59 | fixer | classify | 45 classes from 211 documents |
| 16 Nov 10:50 | fixer | claim | fixer claimed the slot |
| 16 Nov 10:52 | fixer | build-engine | started |
| 16 Nov 10:52 | fixer | build-engine | started |
| 16 Nov 10:52 | fixer | build-engine | started |
| 16 Nov 10:52 | fixer | build-engine | started |
| 16 Nov 11:11 | fixer | attempt | content-missing-partly-replaced -> error |
| 16 Nov 11:53 | fixer | claim | fixer claimed the slot |
| 16 Nov 11:54 | fixer | build-engine | started |
| 16 Nov 11:54 | fixer | build-engine | started |
| 16 Nov 11:55 | fixer | build-engine | started |
| 16 Nov 11:55 | fixer | build-engine | started |
| 16 Nov 11:55 | fixer | build-engine | engine unchanged, compile skipped |
| 16 Nov 12:24 | fixer | hypothesis | content-missing-nothing-in-its-place -> confirmed |
| 16 Nov 12:24 | fixer | attempt | content-missing-nothing-in-its-place -> kept (22/30 moved) |
| 16 Nov 12:46 | fixer | claim | fixer claimed the slot |
| 16 Nov 13:51 | fixer | hypothesis | content-missing-partly-replaced -> untested |
| 16 Nov 13:51 | fixer | hypothesis | content-missing-partly-replaced -> confirmed |
| 16 Nov 13:51 | fixer | attempt | content-missing-partly-replaced -> error |
| 16 Nov 13:52 | fixer | attempt | content-missing-nothing-in-its-place -> kept (31/212 moved) |
| 16 Nov 14:55 | fixer | claim | fixer claimed the slot |
| 16 Nov 14:58 | fixer | build-engine | started |
| 16 Nov 15:00 | fixer | build-engine | engine built in 72s |
| 16 Nov 15:28 | fixer | build-engine | started |
| 16 Nov 15:29 | fixer | build-engine | engine built in 47s |
| 16 Nov 15:48 | fixer | attempt | content-missing-partly-replaced -> kept (1/30 moved) |
| 16 Nov 16:14 | fixer | build-engine | started |
| 16 Nov 16:15 | fixer | build-engine | engine built in 40s |
| 16 Nov 16:17 | fixer | build-engine | started |
| 16 Nov 16:18 | fixer | build-engine | engine built in 59s |
| 16 Nov 16:18 | fixer | attempt | content-missing-nothing-in-its-place -> kept (31/212 moved) |
| 16 Nov 17:23 | fixer | claim | fixer claimed the slot |
| 16 Nov 17:23 | fixer | stale-claim | fixer slot was stale (65 min) - the previous run ended without releasing it |
| 17 Nov 09:21 | fixer | claim | fixer claimed the slot |
| 17 Nov 09:30 | fixer | build-engine | started |
| 17 Nov 09:31 | fixer | build-engine | engine built in 41s |
| 17 Nov 09:35 | fixer | build-engine | started |
| 17 Nov 09:36 | fixer | build-engine | engine built in 40s |
| 17 Nov 09:39 | fixer | build-engine | started |
| 17 Nov 09:40 | fixer | build-engine | engine built in 42s |
| 17 Nov 09:43 | fixer | build-engine | started |
| 17 Nov 09:44 | fixer | build-engine | engine built in 46s |
| 17 Nov 10:27 | fixer | build-engine | started |
| 17 Nov 10:28 | fixer | build-engine | engine built in 40s |
| 17 Nov 10:49 | fixer | build-engine | started |
| 17 Nov 10:50 | fixer | build-engine | engine built in 51s |
| 17 Nov 11:16 | fixer | attempt | content-missing-partly-replaced -> partial (1/13 moved) |
| 17 Nov 12:04 | fixer | claim | fixer claimed the slot |
| 17 Nov 12:04 | fixer | build-engine | started |
| 17 Nov 12:06 | fixer | build-engine | engine built in 90s |
| 17 Nov 12:30 | fixer | attempt | content-missing-partly-replaced -> reverted (0/16 moved) |
| 17 Nov 12:51 | fixer | claim | fixer claimed the slot |
| 17 Nov 12:51 | fixer | build-engine | started |
| 17 Nov 12:53 | fixer | build-engine | engine built in 85s |
| 17 Nov 13:13 | fixer | attempt | content-missing-partly-replaced -> error |
| 17 Nov 13:46 | fixer | build-engine | started |
| 17 Nov 13:47 | fixer | build-engine | engine built in 51s |
| 17 Nov 13:50 | fixer | build-engine | started |
| 17 Nov 13:50 | fixer | build-engine | started |
| 17 Nov 13:51 | fixer | build-engine | started |
| 17 Nov 13:52 | fixer | build-engine | engine built in 73s |
| 17 Nov 13:57 | fixer | build-engine | started |
| 17 Nov 13:58 | fixer | build-engine | engine built in 94s |
| 17 Nov 14:02 | fixer | build-engine | started |
| 17 Nov 14:03 | fixer | build-engine | started |
| 17 Nov 14:04 | fixer | build-engine | started |
| 17 Nov 14:05 | fixer | build-engine | engine built in 66s |
| 17 Nov 14:09 | fixer | build-engine | started |
| 17 Nov 14:11 | fixer | build-engine | engine built in 101s |
| 17 Nov 14:34 | fixer | hypothesis | content-missing-partly-replaced -> ruled-out |
| 17 Nov 14:34 | fixer | hypothesis | content-missing-partly-replaced -> ruled-out |
| 17 Nov 14:34 | fixer | hypothesis | content-missing-partly-replaced -> confirmed |
| 17 Nov 14:34 | fixer | attempt | content-missing-partly-replaced -> partial (2/16 moved) |
| 17 Nov 14:39 | fixer | claim | fixer claimed the slot |
| 17 Nov 14:39 | fixer | build-engine | started |
| 17 Nov 14:40 | fixer | build-engine | engine built in 58s |
| 17 Nov 14:58 | fixer | build-engine | started |
| 17 Nov 14:59 | fixer | build-engine | engine built in 56s |
| 17 Nov 15:36 | fixer | attempt | content-missing-partly-replaced -> partial (1/30 moved) |
| 17 Nov 16:35 | fixer | claim | fixer claimed the slot |
| 17 Nov 16:35 | fixer | build-engine | started |
| 17 Nov 16:38 | fixer | build-engine | engine built in 95s |
| 17 Nov 16:44 | fixer | build-engine | started |
| 17 Nov 16:46 | fixer | build-engine | engine built in 130s |
| 17 Nov 17:21 | fixer | build-engine | started |
| 17 Nov 17:22 | fixer | build-engine | engine built in 90s |
| 17 Nov 17:34 | fixer | attempt | content-missing-partly-replaced -> reverted (0/213 moved) |
| 17 Nov 17:46 | fixer | claim | fixer claimed the slot |
| 17 Nov 17:47 | fixer | build-engine | started |
| 17 Nov 17:47 | fixer | build-engine | engine built in 37s |
| 17 Nov 17:52 | fixer | build-engine | started |
| 17 Nov 17:52 | fixer | build-engine | engine built in 36s |
| 17 Nov 17:54 | fixer | build-engine | started |
| 17 Nov 17:55 | fixer | build-engine | engine built in 37s |
| 17 Nov 18:16 | fixer | build-engine | started |
| 17 Nov 18:17 | fixer | build-engine | engine built in 41s |
| 17 Nov 18:18 | fixer | build-engine | started |
| 17 Nov 18:19 | fixer | build-engine | engine built in 36s |
| 17 Nov 18:21 | fixer | build-engine | started |
| 17 Nov 18:22 | fixer | build-engine | engine built in 43s |
| 17 Nov 18:22 | fixer | attempt | content-missing-partly-replaced -> reverted (0/16 moved) |
| 17 Nov 18:24 | fixer | build-engine | started |
| 17 Nov 18:24 | fixer | build-engine | engine built in 42s |
| 17 Nov 18:33 | fixer | build-engine | started |
| 17 Nov 18:34 | fixer | build-engine | engine built in 40s |
| 17 Nov 18:34 | fixer | attempt | content-missing-partly-replaced -> reverted (0/16 moved) |
| 17 Nov 18:34 | fixer | build-engine | started |
| 17 Nov 18:35 | fixer | build-engine | engine built in 43s |
| 17 Nov 18:44 | fixer | build-engine | started |
| 17 Nov 18:44 | fixer | build-engine | engine built in 41s |
| 17 Nov 18:45 | fixer | attempt | content-missing-partly-replaced -> reverted (0/16 moved) |
| 17 Nov 18:56 | fixer | claim | fixer claimed the slot |
| 17 Nov 18:56 | fixer | build-engine | started |
| 17 Nov 18:57 | fixer | build-engine | engine built in 36s |
| 17 Nov 19:24 | fixer | build-engine | started |
| 17 Nov 19:24 | fixer | build-engine | engine built in 40s |
| 17 Nov 19:31 | fixer | attempt | content-missing-partly-replaced -> partial (1/3 moved) |
| 17 Nov 19:35 | fixer | attempt | content-missing-partly-replaced -> kept (3/3 moved) |
| 17 Nov 23:02 | baseline | claim | baseline claimed the slot |
| 17 Nov 23:43 | classifier | claim | classifier claimed the slot |
| 18 Nov 09:54 | fixer | claim | fixer claimed the slot |
| 18 Nov 09:55 | fixer | build-engine | started |
| 18 Nov 09:55 | fixer | build-engine | engine built in 35s |
| 18 Nov 09:56 | fixer | build-engine | started |
| 18 Nov 09:56 | fixer | build-engine | engine unchanged, compile skipped |
| 18 Nov 10:51 | fixer | build-engine | started |
| 18 Nov 10:52 | fixer | build-engine | started |
| 18 Nov 10:53 | fixer | build-engine | engine built in 46s |
| 18 Nov 11:49 | fixer | attempt | content-missing-nothing-in-its-place -> kept (1/30 moved) |
| 18 Nov 11:50 | fixer | hypothesis | content-missing-nothing-in-its-place -> confirmed |
| 18 Nov 11:50 | fixer | hypothesis | content-missing-nothing-in-its-place -> untested |
| 18 Nov 11:52 | fixer | build-engine | started |
| 18 Nov 11:53 | fixer | build-engine | engine built in 39s |
| 18 Nov 11:54 | fixer | build-engine | started |
| 18 Nov 11:55 | fixer | build-engine | engine built in 37s |
| 18 Nov 11:55 | fixer | attempt | content-missing-nothing-in-its-place -> reverted (0/30 moved) |
| 18 Nov 11:55 | fixer | hypothesis | content-missing-nothing-in-its-place -> ruled-out |
| 18 Nov 12:58 | fixer | claim | fixer claimed the slot |
| 18 Nov 12:58 | fixer | build-engine | started |
| 18 Nov 12:58 | fixer | build-engine | engine built in 36s |
| 18 Nov 13:04 | fixer | build-engine | started |
| 18 Nov 13:05 | fixer | build-engine | engine built in 39s |
| 18 Nov 13:44 | fixer | attempt | single-element-far-out -> partial (1/1 moved) |
| 18 Nov 14:50 | classifier | build-engine | started |
| 18 Nov 14:50 | classifier | build-engine | engine built in 38s |
| 18 Nov 14:50 | fixer | claim | fixer claimed the slot |
| 18 Nov 14:50 | fixer | build-engine | started |
| 18 Nov 14:50 | fixer | build-engine | engine unchanged, compile skipped |
| 18 Nov 14:51 | fixer | attempt | content-partly-lost-and-displaced -> partial (1/7 moved) |
| 18 Nov 15:28 | fixer | attempt | content-partly-lost-and-displaced -> kept (1/210 moved) |
| 18 Nov 15:58 | fixer | claim | fixer claimed the slot |
| 18 Nov 15:58 | fixer | build-engine | started |
| 18 Nov 16:00 | fixer | build-engine | engine built in 60s |
| 18 Nov 16:02 | fixer | build-engine | started |
| 18 Nov 16:03 | fixer | build-engine | engine built in 57s |
| 18 Nov 16:07 | fixer | build-engine | started |
| 18 Nov 16:08 | fixer | build-engine | engine built in 45s |
| 18 Nov 16:10 | fixer | build-engine | started |
| 18 Nov 16:11 | fixer | build-engine | engine built in 68s |
| 18 Nov 16:11 | fixer | attempt | content-partly-lost-and-displaced -> reverted (0/7 moved) |
