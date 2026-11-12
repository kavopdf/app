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
