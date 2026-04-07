# Headcount And Fallbacks

Use this guide to decide whether a class can run cleanly with the headcount you actually have in the room.

## Best Options When Headcount Is Uncertain

Use these first if you expect absences, late arrivals, or uneven numbers.

- `ar_risk_time_preferences`: works with any number of participants, including one.
- `survey` and `payment_info`: work with any number of participants.
- `ab_ultimatum`, `ac_trust`, `af_centipede`: resilient to one spare participant because they include strategy fallback.

## New Flexible Classroom Presets

These are the first opt-in flexible presets. They preserve the legacy presets instead of silently changing them.

### `guess_two_thirds_classroom`

- pools the active room into one beauty-contest calculation
- works better for a true classroom discussion than the legacy paired version
- still needs at least two active participants

### `public_goods_flexible`

- allows a smaller final group instead of requiring perfect trios
- keeps the public-goods lesson interpretable by scaling the per-person share to actual group size
- is the right choice when the room is one or two students off a clean multiple of 3

### Auction family flexible presets

- `english_auction_classroom_flexible`
- `dutch_auction_classroom_flexible`
- `sealed_bid_first_price_classroom_flexible`
- `sealed_bid_second_price_classroom_flexible`
- `ebay_auction_classroom_flexible`
- `common_value_auction_classroom_flexible`

What changes:

- the apps use the real number of bidders in each balanced classroom group
- private-value auctions allow groups as small as 2
- `common_value_auction_classroom_flexible` requires at least 3 bidders
- bidder count is shown in the instructions and results because competition intensity changes with group size

### `volunteer_dilemma_flexible`

- allows balanced 2-to-5 person groups
- keeps per-person benefit and volunteer cost explicit in the results
- is the right choice when the room is slightly off a clean multiple of 3

### `competitiveness_classroom_flexible`

- allows balanced 3-to-5 person groups
- keeps exactly 1 tournament winner by default, even if the group has 5 participants
- is the right choice when the room is slightly off a clean multiple of 4

### `common_pool_resource_flexible`

- allows balanced 3-to-5 person groups
- scales starting stock and extraction limits to the actual group size
- is the right choice when the room is slightly off a clean multiple of 4

### `*_classroom_pair_cycle` presets for short 2-player games

- `nash_demand_classroom_pair_cycle`
- `matching_pennies_classroom_pair_cycle`
- `coordination_game_classroom_pair_cycle`
- `prisoner_one_rd_classroom_pair_cycle`
- `bertrand_classroom_pair_cycle`
- `cournot_classroom_pair_cycle`
- `traveler_dilemma_classroom_pair_cycle`

What changes:

- the apps run for 4 rounds
- one spare participant rotates out each round when attendance is odd
- active players are rematched in real pairs rather than matched with fake opponents
- classroom earnings are averaged across the rounds in which a participant actually played

### `*_role_balanced_classroom` presets for asymmetric 2-player games

- `dictator_role_balanced_classroom`
- `two_sided_auction_role_balanced_classroom`
- `endowment_effect_role_balanced_classroom`
- `gift_exchange_role_balanced_classroom`

What changes:

- the apps run for 4 rounds
- one spare participant rotates out each round when attendance is odd
- active players rotate across both roles instead of keeping one fixed role for the whole app
- classroom earnings are averaged across the rounds in which a participant actually played

### `market_supply_demand_classroom_market`

- places the whole active room into one market
- allows odd classroom sizes as long as at least 4 participants are present
- splits the room into real buyers and sellers using the actual attendance
- generates the buyer-value and seller-cost schedules from configured high/low endpoints

## Legacy Exact-Multiple Apps

These apps still require clean group counts in their default presets.

### Exact Multiple Of 2 In Legacy Presets

- `aa_dictator`
- `ad_nash_demand`
- `ag_matching_pennies`
- `ah_coordination`
- `ai_prisoner_one_rd`
- `ai_prisoner_mult_rd`
- `al_two_sided_auction`
- `at_bertrand`
- `au_cournot`
- `aw_traveler_dilemma`
- `az_endowment_effect`
- `ba_gift_exchange`

Instructor fallback:

- use the matching `*_classroom_pair_cycle` or `*_role_balanced_classroom` preset when it fits the lesson
- keep `ai_prisoner_mult_rd` fixed-size because stable repeated pairs are the treatment
- use a reserve browser
- move one student to observer/debrief duty
- switch to `ar_risk_time_preferences` if the room cannot be repaired cleanly

### Exact Multiple Of 3

- `aj_public_goods` in the legacy preset
- `ay_volunteer_dilemma`

Instructor fallback:

- use the `public_goods_flexible` preset if that fits the lesson
- use `volunteer_dilemma_flexible` if you want to keep everyone in the room
- otherwise wait for a clean multiple or switch apps

### Exact Multiple Of 4

- `as_competitiveness`
- `bb_common_pool_resource`
- `bc_asset_market_bubble`
- `am_english_auction`
- `an_dutch_auction`
- `ao_sealed_bid_first_price`
- `ap_sealed_bid_second_price`
- `aq_ebay_auction`
- `av_common_value_auction`

Instructor fallback:

- use the matching flexible preset for auctions, competitiveness, or common-pool resource when it fits the lesson
- do not launch `bc_asset_market_bubble` with a broken final group
- keep one or two reserve browsers available
- move one student into observer/debrief duty if the lesson still works without them

### Exact Multiple Of 8 In The Legacy Market Preset

- `ak_market_supply_demand`

Instructor fallback:

- use `market_supply_demand_classroom_market` if you want one whole-class market with dynamic schedules
- otherwise treat a missing trader as a hard stop
- use reserve browsers or switch to a different app

## Late Arrivals

Safest:

- `ar_risk_time_preferences`
- `survey`
- `payment_info`

Sometimes workable:

- `ab_ultimatum`
- `ac_trust`
- `af_centipede`

Usually unsafe once play starts:

- the remaining multiplayer apps

## Practical Rules

- Do not rely on a default exact-multiple app to “mostly work” with a short room.
- If one student is missing, use a reserve browser before redesigning the lesson.
- If the room is badly off the required multiple, switch to a solo app or a flexible preset.
- Keep one backup activity ready for the days when the room count changes at the last minute.
- If you want the classroom-flexible version of an auction or tournament app, choose the preset with `_classroom_flexible`, `_classroom_pair_cycle`, `_role_balanced_classroom`, or `_classroom_market` in its session name.
