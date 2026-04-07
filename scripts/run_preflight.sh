#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

PROJECT_PYTHON="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PROJECT_PYTHON" ]]; then
  echo "Project virtualenv not found at $PROJECT_PYTHON. Run ./scripts/bootstrap.sh first."
  exit 1
fi

"$PROJECT_PYTHON" scripts/check_environment.py
"$PROJECT_PYTHON" scripts/verify_audit_tests.py
"$PROJECT_PYTHON" scripts/verify_test_coverage.py
"$PROJECT_PYTHON" scripts/audit_instructor_docs.py
"$PROJECT_PYTHON" scripts/audit_headcount_matrix.py
"$PROJECT_PYTHON" -m pytest tests/test_classroom_tools.py tests/test_instructor_docs.py -q
"$PROJECT_PYTHON" -m compileall classroom_utils.py settings.py \
  scripts tests \
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
