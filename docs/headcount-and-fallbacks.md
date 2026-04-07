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

## Legacy Exact-Multiple Apps

These apps still require clean group counts in their default presets.

### Exact Multiple Of 2

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

- use a reserve browser
- move one student to observer/debrief duty
- switch to `ar_risk_time_preferences` if the room cannot be repaired cleanly

### Exact Multiple Of 3

- `aj_public_goods` in the legacy preset
- `ay_volunteer_dilemma`

Instructor fallback:

- use the `public_goods_flexible` preset if that fits the lesson
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

- do not launch with a broken final group
- keep one or two reserve browsers available
- move one student into observer/debrief duty if the lesson still works without them

### Exact Multiple Of 8

- `ak_market_supply_demand`

Instructor fallback:

- treat a missing trader as a hard stop
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
