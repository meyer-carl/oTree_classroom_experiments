# Headcount and Fallbacks

## Matrix

This table is the operational source of truth for classroom headcount handling. If code changes, update this file and rerun `python scripts/audit_headcount_matrix.py`.

| App | Group size | Minimum workable headcount | Compatibility | Odd-count behavior | Late arrival after start? | Instructor response | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `aa_dictator` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Use a reserve browser or move one student to observer/debrief duty. | Unmatched players skip ahead. |
| `ab_ultimatum` | 2 | 2 | odd-count resilient | strategy fallback | Limited | Use the built-in strategy fallback for one spare student; if the room collapses below two active participants, switch apps. | Best used with at least one full pair plus any spare student. |
| `ac_trust` | 2 | 2 | odd-count resilient | strategy fallback | Limited | Use the built-in strategy fallback for one spare student; if the room collapses below two active participants, switch apps. | Best used with at least one full pair plus any spare student. |
| `ad_nash_demand` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Keep a reserve browser or reassign one student as observer. | Unmatched players skip ahead. |
| `ae_guess_two_thirds` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Run it only when you can form clean pairs, or switch to a different whole-class reasoning exercise. | Current implementation is paired, not a single class-wide average. |
| `af_centipede` | 2 | 2 | odd-count resilient | strategy fallback | Limited | Use the built-in strategy fallback for one spare student; if the room collapses below two active participants, switch apps. | Highest operator complexity in the strategy-fallback family. |
| `ag_matching_pennies` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Use a reserve browser or move one student to observer/debrief duty. | Random paying round remains well-defined only with full pairs. |
| `ah_coordination` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Use a reserve browser or move one student to observer/debrief duty. | Random paying round remains well-defined only with full pairs. |
| `ai_prisoner_mult_rd` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Do not start with an incomplete final pair; repeated matching depends on stable pairs. | Late replacement is risky once rounds begin. |
| `ai_prisoner_one_rd` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Use a reserve browser or move one student to observer/debrief duty. | One-shot pair structure only. |
| `aj_public_goods` | 3 | 3 | exact multiple of 3 | skip unmatched | No | Do not launch until headcount is a multiple of three; otherwise switch or reassign students. | Contributions are only interpretable with full groups. |
| `ak_market_supply_demand` | 8 | 8 | exact multiple of 8 | skip unmatched | No | Treat missing traders as a release-blocking headcount problem; use reserve browsers or switch apps. | Needs a full buyer/seller structure. |
| `al_two_sided_auction` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Use a reserve browser or move one student to observer/debrief duty. | One buyer and one seller only. |
| `am_english_auction` | 4 | 4 | exact multiple of 4 | skip unmatched | No | Do not start without a full four-player auction group. | Fewer bidders changes the auction logic materially. |
| `an_dutch_auction` | 4 | 4 | exact multiple of 4 | skip unmatched | No | Do not start without a full four-player auction group. | Fewer bidders changes the auction logic materially. |
| `ao_sealed_bid_first_price` | 4 | 4 | exact multiple of 4 | skip unmatched | No | Do not start without a full four-player auction group. | Private-value bidding exercise assumes a full bidder set. |
| `ap_sealed_bid_second_price` | 4 | 4 | exact multiple of 4 | skip unmatched | No | Do not start without a full four-player auction group. | Private-value bidding exercise assumes a full bidder set. |
| `aq_ebay_auction` | 4 | 4 | exact multiple of 4 | skip unmatched | No | Do not start without a full four-player auction group. | Proxy-bid competition is easiest to explain with a full bidder set. |
| `ar_risk_time_preferences` | 1 | 1 | any count | not applicable | Yes | Safe fallback when a multiplayer session cannot be formed cleanly. | Solo multiple-price-list app. |
| `as_competitiveness` | 4 | 4 | exact multiple of 4 | skip unmatched | No | Keep one reserve browser or shift a student to observer/debrief duty. | Tournament incentives depend on the full peer group. |
| `at_bertrand` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Use a reserve browser or move one student to observer/debrief duty. | Two-firm pricing only. |
| `au_cournot` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Use a reserve browser or move one student to observer/debrief duty. | Two-firm quantity game only. |
| `av_common_value_auction` | 4 | 4 | exact multiple of 4 | skip unmatched | No | Do not start without a full four-player auction group. | Winner’s-curse discussion depends on a real bidder pool. |
| `aw_traveler_dilemma` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Use a reserve browser or move one student to observer/debrief duty. | Two-player claim comparison only. |
| `ay_volunteer_dilemma` | 3 | 3 | exact multiple of 3 | skip unmatched | No | Do not start until headcount is a multiple of three. | Public-provision logic depends on the full trio. |
| `az_endowment_effect` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Use a reserve browser or move one student to observer/debrief duty. | Buyer/seller pairing only. |
| `ba_gift_exchange` | 2 | 2 | exact multiple of 2 | skip unmatched | No | Use a reserve browser or move one student to observer/debrief duty. | Employer-worker pairing only. |
| `bb_common_pool_resource` | 4 | 4 | exact multiple of 4 | skip unmatched | No | Do not start without a full four-player extraction group. | Regeneration and scarcity depend on the full group. |
| `bc_asset_market_bubble` | 4 | 4 | exact multiple of 4 | skip unmatched | No | Do not start without a full four-player market group. | Cash and asset dynamics are calibrated to the full group. |
| `payment_info` | ungrouped | 1 | any count | not applicable | Yes | Safe standalone follow-up app. | Displays participant label when present, otherwise participant code. |
| `survey` | ungrouped | 1 | any count | not applicable | Yes | Safe standalone follow-up app. | Useful as a fallback or bundled post-experiment app. |

## Fallback Rules

- If an app says `exact multiple`, do not rely on the app to “mostly work” with a short room. The app will skip unmatched players, and the debrief will be harder to defend.
- If you are one participant short, first use a reserve browser.
- If you still cannot form clean groups, move one student into observer/debrief duty instead of launching a broken final group.
- If the room is badly off the required multiple, switch to `risk_time_preferences`, `survey_payment`, or one of the odd-count-resilient bargaining apps.

## Late Arrival Policy

- Safe late arrivals: `risk_time_preferences`, `survey`, `payment_info`
- Limited late arrivals: `ultimatum`, `trust`, `centipede` only if the session has not progressed far enough that the spare student would distort the debrief
- Unsafe late arrivals: all remaining multiplayer apps

## Practical Warnings

- `guess_two_thirds` is not yet a single pooled classroom beauty contest. It currently runs in pairs.
- `market_supply_demand` should be treated as a full-room app. If the eighth trader is missing, switch or fill the seat.
- Repeated-round apps are less tolerant of mid-session browser loss than one-shot apps because state carries forward.
