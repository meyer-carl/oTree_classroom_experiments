from __future__ import annotations

from decimal import Decimal

import pytest

from grading_benchmarks import SessionContext, collect_opportunities, missing_supported_apps
from scripts.build_grading_summary import (
    assign_session_percentiles,
    build_quarter_records,
    build_session_records,
)


def base_row(
    *,
    session_name: str,
    session_code: str = "S1",
    participant_label: str = "ECON101_001",
    participant_code: str = "P1",
    source_file: str = "all_apps_wide.csv",
    **extra: str,
) -> dict[str, str]:
    row = {
        "participant.label": participant_label,
        "participant.code": participant_code,
        "session.code": session_code,
        "session.config.name": session_name,
        "__source_file": source_file,
    }
    row.update(extra)
    return row


def test_grading_benchmarks_cover_all_configured_apps():
    assert missing_supported_apps() == []


def test_role_balanced_dictator_summary_uses_raw_max_and_sitout_counts():
    row = base_row(
        session_name="dictator_role_balanced_classroom",
        **{
            "session.config.role_balanced_classroom": "1",
            "aa_dictator.1.player.id_in_group": "1",
            "aa_dictator.1.player.active_this_round": "0",
            "aa_dictator.1.player.assigned_role": "",
            "aa_dictator.1.player.raw_round_payoff": "0",
            "aa_dictator.1.player.payoff": "0",
            "aa_dictator.2.player.id_in_group": "2",
            "aa_dictator.2.player.active_this_round": "1",
            "aa_dictator.2.player.assigned_role": "Recipient",
            "aa_dictator.2.player.raw_round_payoff": "100",
            "aa_dictator.2.player.payoff": "50",
            "aa_dictator.3.player.id_in_group": "1",
            "aa_dictator.3.player.active_this_round": "1",
            "aa_dictator.3.player.assigned_role": "Dictator",
            "aa_dictator.3.player.raw_round_payoff": "100",
            "aa_dictator.3.player.payoff": "50",
            "aa_dictator.4.player.id_in_group": "1",
            "aa_dictator.4.player.active_this_round": "0",
            "aa_dictator.4.player.assigned_role": "",
            "aa_dictator.4.player.raw_round_payoff": "0",
            "aa_dictator.4.player.payoff": "0",
        },
    )

    records = build_session_records([row], allow_anonymous=False)
    record = records[0]
    assert record["raw_earnings_points"] == Decimal("200")
    assert record["app_payoff_points"] == Decimal("100")
    assert record["max_attainable_points"] == Decimal("200")
    assert record["attainment_fraction"] == Decimal("1")
    assert record["active_opportunity_count"] == 2
    assert record["sit_out_count"] == 2


def test_representative_benchmarks_cover_trust_centipede_public_goods_auction_and_market():
    trust_row = base_row(
        session_name="trust_role_balanced_classroom",
        **{
            "session.config.role_balanced_classroom": "1",
            "session.config.trust_multiplier": "3",
            "ac_trust.1.player.id_in_group": "1",
            "ac_trust.1.player.active_this_round": "1",
            "ac_trust.1.player.assigned_role": "First mover",
            "ac_trust.1.player.raw_round_payoff": "300",
            "ac_trust.1.player.payoff": "75",
        },
    )
    trust_context = SessionContext.from_rows([trust_row])
    trust_opportunity = collect_opportunities(trust_row, trust_context)[0]
    assert trust_opportunity.max_attainable == Decimal("300")

    centipede_row = base_row(
        session_name="centipede_role_balanced_classroom",
        **{
            "session.config.role_balanced_classroom": "1",
            "af_centipede.1.player.id_in_group": "1",
            "af_centipede.1.player.active_this_round": "1",
            "af_centipede.1.player.assigned_role": "Player 1",
            "af_centipede.1.player.raw_round_payoff": "60",
            "af_centipede.1.player.payoff": "30",
            "af_centipede.2.player.id_in_group": "1",
            "af_centipede.2.player.active_this_round": "1",
            "af_centipede.2.player.assigned_role": "Player 1",
            "af_centipede.2.player.raw_round_payoff": "0",
            "af_centipede.2.player.payoff": "0",
            "af_centipede.3.player.id_in_group": "1",
            "af_centipede.3.player.active_this_round": "1",
            "af_centipede.3.player.assigned_role": "Player 1",
            "af_centipede.3.player.raw_round_payoff": "0",
            "af_centipede.3.player.payoff": "0",
            "af_centipede.4.player.id_in_group": "1",
            "af_centipede.4.player.active_this_round": "1",
            "af_centipede.4.player.assigned_role": "Player 1",
            "af_centipede.4.player.raw_round_payoff": "0",
            "af_centipede.4.player.payoff": "0",
            "af_centipede.5.player.id_in_group": "1",
            "af_centipede.5.player.active_this_round": "1",
            "af_centipede.5.player.assigned_role": "Player 1",
            "af_centipede.5.player.raw_round_payoff": "0",
            "af_centipede.5.player.payoff": "0",
            "af_centipede.6.player.id_in_group": "1",
            "af_centipede.6.player.active_this_round": "1",
            "af_centipede.6.player.assigned_role": "Player 1",
            "af_centipede.6.player.raw_round_payoff": "0",
            "af_centipede.6.player.payoff": "0",
        },
    )
    centipede_context = SessionContext.from_rows([centipede_row])
    centipede_opportunity = collect_opportunities(centipede_row, centipede_context)[0]
    assert centipede_opportunity.max_attainable == Decimal("180")

    public_goods_row = base_row(
        session_name="public_goods_flexible",
        **{
            "aj_public_goods.1.player.id_in_group": "1",
            "aj_public_goods.1.player.payoff": "108",
            "aj_public_goods.1.player.contribution": "10",
            "aj_public_goods.1.group.id_in_subsession": "1",
            "aj_public_goods.1.group.effective_group_size": "3",
            "aj_public_goods.1.group.effective_multiplier": "1.8",
        },
    )
    public_goods_context = SessionContext.from_rows([public_goods_row])
    public_goods_opportunity = collect_opportunities(public_goods_row, public_goods_context)[0]
    assert public_goods_opportunity.max_attainable == Decimal("220")

    auction_row = base_row(
        session_name="sealed_bid_first_price",
        **{
            "ao_sealed_bid_first_price.1.player.id_in_group": "1",
            "ao_sealed_bid_first_price.1.player.private_value": "120",
            "ao_sealed_bid_first_price.1.player.payoff": "20",
        },
    )
    auction_context = SessionContext.from_rows([auction_row])
    auction_opportunity = collect_opportunities(auction_row, auction_context)[0]
    assert auction_opportunity.max_attainable == Decimal("120")

    market_row = base_row(
        session_name="market_supply_demand_classroom_market",
        **{
            "ak_market_supply_demand.1.player.id_in_group": "5",
            "ak_market_supply_demand.1.player.is_buyer": "0",
            "ak_market_supply_demand.1.player.private_cost": "20",
            "ak_market_supply_demand.1.player.private_value": "0",
            "ak_market_supply_demand.1.player.payoff": "65",
            "ak_market_supply_demand.1.group.id_in_subsession": "1",
            "ak_market_supply_demand.1.group.buyer_schedule_csv": "100, 90, 80, 70, 60",
            "ak_market_supply_demand.1.group.seller_schedule_csv": "20, 30, 40, 50",
        },
    )
    market_context = SessionContext.from_rows([market_row])
    market_opportunity = collect_opportunities(market_row, market_context)[0]
    assert market_opportunity.max_attainable == Decimal("80")


def test_session_percentiles_skip_zero_opportunity_rows():
    records = [
        {
            "participant_label": "A",
            "session_code": "S1",
            "session_name": "dictator_role_balanced_classroom",
            "raw_earnings_points": Decimal("100"),
            "app_payoff_points": Decimal("50"),
            "max_attainable_points": Decimal("100"),
            "attainment_fraction": Decimal("1"),
            "active_opportunity_count": 1,
            "sit_out_count": 0,
            "source_file": "one.csv",
        },
        {
            "participant_label": "B",
            "session_code": "S1",
            "session_name": "dictator_role_balanced_classroom",
            "raw_earnings_points": Decimal("50"),
            "app_payoff_points": Decimal("50"),
            "max_attainable_points": Decimal("100"),
            "attainment_fraction": Decimal("0.5"),
            "active_opportunity_count": 1,
            "sit_out_count": 0,
            "source_file": "one.csv",
        },
        {
            "participant_label": "C",
            "session_code": "S1",
            "session_name": "dictator_role_balanced_classroom",
            "raw_earnings_points": Decimal("0"),
            "app_payoff_points": Decimal("0"),
            "max_attainable_points": Decimal("0"),
            "attainment_fraction": Decimal("0"),
            "active_opportunity_count": 0,
            "sit_out_count": 1,
            "source_file": "one.csv",
        },
    ]
    assign_session_percentiles(records)
    by_label = {record["participant_label"]: record for record in records}
    assert by_label["A"]["raw_earnings_percentile"] == 100.0
    assert by_label["B"]["raw_earnings_percentile"] == 0.0
    assert by_label["C"].get("raw_earnings_percentile") is None
    assert by_label["C"].get("attainment_fraction_percentile") is None


def test_quarter_aggregation_sums_session_records():
    session_records = [
        {
            "participant_label": "ECON101_001",
            "session_code": "S1",
            "session_name": "dictator",
            "raw_earnings_points": Decimal("10"),
            "app_payoff_points": Decimal("10"),
            "max_attainable_points": Decimal("20"),
            "attainment_fraction": Decimal("0.5"),
            "active_opportunity_count": 1,
            "sit_out_count": 0,
            "source_file": "week1.csv",
        },
        {
            "participant_label": "ECON101_001",
            "session_code": "S2",
            "session_name": "trust",
            "raw_earnings_points": Decimal("15"),
            "app_payoff_points": Decimal("15"),
            "max_attainable_points": Decimal("30"),
            "attainment_fraction": Decimal("0.5"),
            "active_opportunity_count": 1,
            "sit_out_count": 0,
            "source_file": "week2.csv",
        },
    ]
    quarter_records = build_quarter_records(session_records)
    assert quarter_records == [
        {
            "participant_label": "ECON101_001",
            "total_raw_earnings_points": Decimal("25"),
            "total_app_payoff_points": Decimal("25"),
            "total_max_attainable_points": Decimal("50"),
            "overall_attainment_fraction": Decimal("0.5"),
            "raw_earnings_percentile": 100.0,
            "attainment_fraction_percentile": 100.0,
            "session_count": 2,
            "active_opportunity_count": 2,
            "sit_out_count": 0,
            "sessions": "dictator;trust",
        }
    ]


def test_build_session_records_rejects_anonymous_without_flag_and_allows_it_with_flag():
    anonymous_row = base_row(
        session_name="dictator",
        participant_label="",
        participant_code="anon1",
        **{
            "aa_dictator.1.player.id_in_group": "1",
            "aa_dictator.1.player.payoff": "99",
        },
    )

    with pytest.raises(ValueError):
        build_session_records([anonymous_row], allow_anonymous=False)

    records = build_session_records([anonymous_row], allow_anonymous=True)
    assert records[0]["participant_label"] == "ANON_anon1"
