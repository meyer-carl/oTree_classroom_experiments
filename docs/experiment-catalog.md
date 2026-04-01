# Experiment Catalog

## Social Preferences and Bargaining

| App | Topic | Compatibility | Operational notes |
| --- | --- | --- | --- |
| `aa_dictator` | Dictator game | Exact multiple of 2 | Baseline generosity and allocation choice. Unmatched players skip. |
| `ab_ultimatum` | Ultimatum game | Odd-count resilient | Supports direct and strategy-method variants. Best current spare-student option in bargaining. |
| `ac_trust` | Trust game | Odd-count resilient | Includes strategy-method handling for incomplete groups. |
| `aj_public_goods` | Public goods | Exact multiple of 3 | Do not start with a short final trio. |
| `az_endowment_effect` | Endowment effect / WTA-WTP | Exact multiple of 2 | Seller/buyer valuations for reference dependence and ownership effects. |
| `ba_gift_exchange` | Gift exchange | Exact multiple of 2 | Reciprocity and principal-agent teaching case. |
| `ay_volunteer_dilemma` | Volunteer dilemma | Exact multiple of 3 | Best with a clean trio and no late replacements. |

## Strategic Interaction

| App | Topic | Compatibility | Operational notes |
| --- | --- | --- | --- |
| `ad_nash_demand` | Nash demand | Exact multiple of 2 | Useful for bargaining and conflict over a fixed surplus. |
| `ae_guess_two_thirds` | Beauty contest | Exact multiple of 2 | Current implementation is paired, not a single whole-class average. |
| `af_centipede` | Centipede game | Odd-count resilient | Highest operational complexity in the strategy-method family. |
| `ag_matching_pennies` | Zero-sum matching pennies | Exact multiple of 2 | Good for mixed-strategy intuition. |
| `ah_coordination` | Coordination game | Exact multiple of 2 | Clean coordination and payoff comparison. |
| `ai_prisoner_one_rd` | One-shot prisoner’s dilemma | Exact multiple of 2 | Simple benchmark PD. |
| `ai_prisoner_mult_rd` | Repeated prisoner’s dilemma | Exact multiple of 2 | Fixed matching across rounds. Avoid mid-session headcount changes. |
| `aw_traveler_dilemma` | Traveler’s dilemma | Exact multiple of 2 | Useful for bounded rationality and undercutting. |

## Markets and Industrial Organization

| App | Topic | Compatibility | Operational notes |
| --- | --- | --- | --- |
| `ak_market_supply_demand` | Supply and demand market | Exact multiple of 8 | Largest standard classroom market. Treat missing traders as a hard stop. |
| `bb_common_pool_resource` | Common-pool resource | Exact multiple of 4 | Repeated commons game with stock regeneration. |
| `bc_asset_market_bubble` | Asset market bubble | Exact multiple of 4 | Repeated asset market with declining fundamentals and uniform-price clearing. |
| `al_two_sided_auction` | Two-sided auction | Exact multiple of 2 | Simple trade/no-trade benchmark. |
| `am_english_auction` | English auction | Exact multiple of 4 | Ascending-price auction. |
| `an_dutch_auction` | Dutch auction | Exact multiple of 4 | Descending-price auction. |
| `ao_sealed_bid_first_price` | First-price sealed bid | Exact multiple of 4 | Core auction-bidding exercise. |
| `ap_sealed_bid_second_price` | Second-price sealed bid | Exact multiple of 4 | Dominant-strategy teaching example. |
| `aq_ebay_auction` | eBay-style proxy bidding | Exact multiple of 4 | Incremental proxy-bid logic. |
| `av_common_value_auction` | Common value auction | Exact multiple of 4 | Winner’s curse and noisy signals. |
| `at_bertrand` | Bertrand competition | Exact multiple of 2 | Price competition. |
| `au_cournot` | Cournot competition | Exact multiple of 2 | Quantity competition. |

## Individual Measurement

| App | Topic | Compatibility | Operational notes |
| --- | --- | --- | --- |
| `ar_risk_time_preferences` | Risk, time, loss, and ambiguity preferences | Any count | Solo multiple-price-list app and strongest fallback when a multiplayer session cannot form cleanly. |
| `as_competitiveness` | Competitiveness | Exact multiple of 4 | Timed task plus incentive choice. Needs a full peer group. |

## Support Apps

| App | Topic | Compatibility | Operational notes |
| --- | --- | --- | --- |
| `survey` | Survey and cognitive reflection | Any count | Safe bundled follow-up or fallback app. |
| `payment_info` | Redemption and payout instructions | Any count | Shows participant label when present, otherwise the anonymous participant code. |

## Planning Notes

- Use `docs/headcount-and-fallbacks.md` as the operational matrix before launching a live class.
- The catalog is broad on bargaining, auctions, and strategic interaction.
- The first-wave behavioral gaps are now covered by endowment effect, gift exchange, commons, and asset-market bubble apps.
- The next gaps to prioritize remain self-control, overconfidence, discrimination, and voting.
