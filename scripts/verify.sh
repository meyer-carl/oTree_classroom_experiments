#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -d ".venv" ]]; then
  source ".venv/bin/activate"
fi

python scripts/check_environment.py
python scripts/verify_audit_tests.py
python -m compileall classroom_utils.py settings.py \
  aa_dictator ab_ultimatum ac_trust ad_nash_demand ae_guess_two_thirds \
  af_centipede ag_matching_pennies ah_coordination ai_prisoner_mult_rd \
  ai_prisoner_one_rd aj_public_goods ak_market_supply_demand \
  al_two_sided_auction am_english_auction an_dutch_auction \
  ao_sealed_bid_first_price ap_sealed_bid_second_price aq_ebay_auction \
  ar_risk_time_preferences as_competitiveness at_bertrand au_cournot \
  av_common_value_auction aw_traveler_dilemma ay_volunteer_dilemma \
  az_endowment_effect ba_gift_exchange bb_common_pool_resource \
  bc_asset_market_bubble \
  payment_info survey

if command -v otree >/dev/null 2>&1; then
  sessions=(
    dictator
    ultimatum
    trust
    centipede
    market_supply_demand
    prisoner_mult_rd
    risk_time_preferences
    risk_time_preferences_ambiguity
    competitiveness
    endowment_effect
    gift_exchange
    common_pool_resource
    asset_market_bubble
    survey_payment
  )
  for session_name in "${sessions[@]}"; do
    echo "Running otree test ${session_name}"
    otree test "${session_name}"
  done
else
  echo "otree CLI not found in PATH; skipping bot execution."
fi
