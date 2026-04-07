from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import settings  # noqa: E402


SUITE_ORDER = ("smoke", "high", "full")

SMOKE_SESSIONS = {
    "dictator",
    "ultimatum",
    "trust",
    "centipede",
    "market_supply_demand",
    "prisoner_mult_rd",
    "risk_time_preferences",
    "risk_time_preferences_ambiguity",
    "competitiveness",
    "endowment_effect",
    "gift_exchange",
    "common_pool_resource",
    "asset_market_bubble",
    "survey_payment",
}

HIGH_ONLY_SESSIONS = {
    "nash_demand",
    "nash_demand_classroom_pair_cycle",
    "guess_two_thirds",
    "guess_two_thirds_classroom",
    "ultimatum_role_balanced_classroom",
    "trust_role_balanced_classroom",
    "centipede_role_balanced_classroom",
    "matching_pennies",
    "matching_pennies_classroom_pair_cycle",
    "coordination_game",
    "coordination_game_classroom_pair_cycle",
    "prisoner_one_rd",
    "prisoner_one_rd_classroom_pair_cycle",
    "public_goods",
    "public_goods_flexible",
    "two_sided_auction",
    "two_sided_auction_role_balanced_classroom",
    "english_auction",
    "english_auction_classroom_flexible",
    "dutch_auction",
    "dutch_auction_classroom_flexible",
    "sealed_bid_first_price",
    "sealed_bid_first_price_classroom_flexible",
    "sealed_bid_second_price",
    "sealed_bid_second_price_classroom_flexible",
    "ebay_auction",
    "ebay_auction_classroom_flexible",
    "bertrand",
    "bertrand_classroom_pair_cycle",
    "cournot",
    "cournot_classroom_pair_cycle",
    "common_value_auction",
    "common_value_auction_classroom_flexible",
    "traveler_dilemma",
    "traveler_dilemma_classroom_pair_cycle",
    "volunteer_dilemma",
    "volunteer_dilemma_flexible",
    "competitiveness_classroom_flexible",
    "common_pool_resource_flexible",
    "dictator_role_balanced_classroom",
    "endowment_effect_role_balanced_classroom",
    "gift_exchange_role_balanced_classroom",
    "market_supply_demand_classroom_market",
}

FULL_ONLY_SESSIONS = {
    "trust_with_survey",
    "public_goods_with_survey",
    "market_with_survey",
    "competitiveness_with_survey",
}


def load_session_configs():
    return settings.SESSION_CONFIGS


def session_names():
    return [config["name"] for config in load_session_configs()]


def bundled_session_names():
    return [
        config["name"]
        for config in load_session_configs()
        if len(config.get("app_sequence", [])) > 1
    ]


def tier_assignments():
    assignments = {}
    for name in SMOKE_SESSIONS:
        assignments[name] = "smoke"
    for name in HIGH_ONLY_SESSIONS:
        assignments[name] = "high"
    for name in FULL_ONLY_SESSIONS:
        assignments[name] = "full"
    return assignments


def suite_sessions(suite_name: str):
    tier_index = SUITE_ORDER.index(suite_name)
    assignments = tier_assignments()
    return [
        name
        for name in session_names()
        if SUITE_ORDER.index(assignments[name]) <= tier_index
    ]


def validate_suite_assignments():
    problems = []
    assignments = tier_assignments()
    config_names = session_names()

    unknown_sessions = sorted(name for name in assignments if name not in config_names)
    if unknown_sessions:
        problems.append(
            "Unknown assigned sessions: " + ", ".join(unknown_sessions)
        )

    missing_assignments = sorted(name for name in config_names if name not in assignments)
    if missing_assignments:
        problems.append(
            "Missing suite assignments: " + ", ".join(missing_assignments)
        )

    duplicate_assignments = sorted(
        SMOKE_SESSIONS & HIGH_ONLY_SESSIONS
        | SMOKE_SESSIONS & FULL_ONLY_SESSIONS
        | HIGH_ONLY_SESSIONS & FULL_ONLY_SESSIONS
    )
    if duplicate_assignments:
        problems.append(
            "Sessions assigned to multiple tiers: " + ", ".join(duplicate_assignments)
        )

    covered_sessions = set()
    for suite_name in SUITE_ORDER:
        covered_sessions.update(suite_sessions(suite_name))

    missing_bundles = sorted(
        name for name in bundled_session_names() if name not in covered_sessions
    )
    if missing_bundles:
        problems.append(
            "Bundled session configs missing from all suites: "
            + ", ".join(missing_bundles)
        )

    return problems
