# Experiment Catalog

Use this catalog to choose the classroom exercise. Use `01_instructor_pdfs/06_headcount_and_fallbacks.pdf` right after this if your class size may be messy.

## Social Preferences And Bargaining

- `aa_dictator`: baseline dictator game. Legacy preset needs clean pairs; `dictator_role_balanced_classroom` rotates dictator/recipient roles across 4 rounds.
- `ab_ultimatum`: ultimatum game with direct play and strategy-method fallback. Best current bargaining app when the headcount may be odd.
- `ac_trust`: trust game with strategy-method fallback and configurable multiplier. Also resilient to one spare participant.
- `aj_public_goods`: legacy preset uses trios. The new `public_goods_flexible` preset allows a smaller final group with scaled payoffs.
- `az_endowment_effect`: buyer/seller WTA-WTP comparison. Legacy paired format; `endowment_effect_role_balanced_classroom` rotates buyer/seller roles across 4 rounds.
- `ba_gift_exchange`: employer-worker reciprocity exercise. Legacy paired format; `gift_exchange_role_balanced_classroom` rotates employer/worker roles across 4 rounds.
- `ay_volunteer_dilemma`: volunteer dilemma in trios. The new `volunteer_dilemma_flexible` preset allows balanced 2-to-5 person groups.

## Strategic Interaction

- `ad_nash_demand`: two-player bargaining over a fixed surplus. `nash_demand_classroom_pair_cycle` rotates a spare participant and averages earnings over active rounds.
- `ae_guess_two_thirds`: beauty contest. The legacy preset runs in pairs; the new `guess_two_thirds_classroom` preset pools the active room into one classroom contest.
- `af_centipede`: centipede game with strategy fallback for odd headcounts.
- `ag_matching_pennies`: two-player mixed-strategy benchmark. `matching_pennies_classroom_pair_cycle` rotates pairs and any spare participant across 4 rounds.
- `ah_coordination`: coordination game in pairs. `coordination_game_classroom_pair_cycle` rotates pairs and any spare participant across 4 rounds.
- `ai_prisoner_one_rd`: one-shot prisoner’s dilemma in pairs. `prisoner_one_rd_classroom_pair_cycle` rotates pairs and any spare participant across 4 rounds.
- `ai_prisoner_mult_rd`: repeated prisoner’s dilemma with stable pairs across rounds.
- `aw_traveler_dilemma`: traveler’s dilemma in pairs. `traveler_dilemma_classroom_pair_cycle` rotates pairs and any spare participant across 4 rounds.

## Markets And Industrial Organization

- `ak_market_supply_demand`: legacy preset is an eight-trader market. `market_supply_demand_classroom_market` instead puts the whole room into one market with dynamic buyer/seller schedules.
- `bb_common_pool_resource`: repeated common-pool extraction game. The new `common_pool_resource_flexible` preset allows balanced 3-to-5 person groups with scaled stock and extraction limits.
- `bc_asset_market_bubble`: repeated asset market with declining fundamentals. Intentionally still fixed at groups of 4 because inventories and cash carry forward across rounds.
- `al_two_sided_auction`: simple buyer-seller trade benchmark. `two_sided_auction_role_balanced_classroom` rotates buyer/seller roles across 4 rounds.
- `am_english_auction`: ascending-price auction. The `english_auction_classroom_flexible` preset uses real 2-to-6 bidder groups.
- `an_dutch_auction`: descending-price auction. The `dutch_auction_classroom_flexible` preset uses real 2-to-6 bidder groups.
- `ao_sealed_bid_first_price`: first-price sealed-bid auction. The `sealed_bid_first_price_classroom_flexible` preset uses real 2-to-6 bidder groups.
- `ap_sealed_bid_second_price`: second-price sealed-bid auction. The `sealed_bid_second_price_classroom_flexible` preset uses real 2-to-6 bidder groups.
- `aq_ebay_auction`: eBay-style proxy bidding. The `ebay_auction_classroom_flexible` preset uses real 2-to-6 bidder groups.
- `av_common_value_auction`: common-value auction. The `common_value_auction_classroom_flexible` preset uses real 3-to-6 bidder groups.
- `at_bertrand`: Bertrand competition in pairs. `bertrand_classroom_pair_cycle` rotates pairs and any spare participant across 4 rounds.
- `au_cournot`: Cournot competition in pairs. `cournot_classroom_pair_cycle` rotates pairs and any spare participant across 4 rounds.

## Individual Measurement

- `ar_risk_time_preferences`: risk, time, loss, and ambiguity preferences. Best fallback when a multiplayer activity cannot form cleanly.
- `as_competitiveness`: timed competitiveness task. The new `competitiveness_classroom_flexible` preset allows balanced 3-to-5 person groups while keeping one tournament winner by default.

## Support Apps

- `survey`: safe follow-up or fallback app for any headcount.
- `payment_info`: redemption and payout instructions for any headcount.

## How To Use This Catalog

1. choose the teaching goal
2. check whether the app’s headcount rule matches the class size you actually expect
3. run one `live_demo` before the real class
4. use `01_instructor_pdfs/09_data_and_export.pdf` afterward if you want to preserve debrief-relevant fields
