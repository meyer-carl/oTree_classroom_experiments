from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable

import settings

import aa_dictator
import ab_ultimatum
import ac_trust
import ad_nash_demand
import ae_guess_two_thirds
import af_centipede
import ag_matching_pennies
import ah_coordination
import ai_prisoner_mult_rd
import ai_prisoner_one_rd
import aj_public_goods
import ak_market_supply_demand
import al_two_sided_auction
import am_english_auction
import an_dutch_auction
import ao_sealed_bid_first_price
import ap_sealed_bid_second_price
import aq_ebay_auction
import ar_risk_time_preferences
import as_competitiveness
import at_bertrand
import au_cournot
import av_common_value_auction
import aw_traveler_dilemma
import ay_volunteer_dilemma
import az_endowment_effect
import ba_gift_exchange
import bb_common_pool_resource
import bc_asset_market_bubble


ZERO = Decimal("0")
ONE = Decimal("1")

SESSION_CONFIG_MAP = {config["name"]: config for config in settings.SESSION_CONFIGS}
ZERO_OPPORTUNITY_APPS = {"survey", "payment_info"}


@dataclass(frozen=True)
class Opportunity:
    app_name: str
    raw_earnings: Decimal
    app_payoff: Decimal
    max_attainable: Decimal
    active_opportunity: int
    sit_out: int


@dataclass
class SessionContext:
    session_code: str
    session_name: str
    rows: list[dict[str, str]]
    app_sequence: list[str]
    source_files: set[str]
    rounds_by_app: dict[str, list[int]]
    groups_by_app_round: dict[tuple[str, int, str], list[dict[str, str]]]

    @classmethod
    def from_rows(cls, rows: list[dict[str, str]]) -> "SessionContext":
        if not rows:
            raise ValueError("SessionContext requires at least one row.")
        session_code = text_value(rows[0], "session.code")
        session_name = text_value(rows[0], "session.config.name")
        config = SESSION_CONFIG_MAP.get(session_name)
        if not config:
            raise ValueError(f"Unknown session config in export: {session_name}")
        app_sequence = list(config.get("app_sequence", []))
        rounds_by_app: dict[str, set[int]] = {app_name: set() for app_name in app_sequence}
        groups_by_app_round: dict[tuple[str, int, str], list[dict[str, str]]] = {}
        source_files = {row.get("__source_file", "") for row in rows if row.get("__source_file")}

        for row in rows:
            for app_name in app_sequence:
                for round_number in round_numbers_for_app(row, app_name):
                    rounds_by_app.setdefault(app_name, set()).add(round_number)
                    group_id = text_value(row, app_field_name(app_name, round_number, "group.id_in_subsession"))
                    if group_id:
                        groups_by_app_round.setdefault((app_name, round_number, group_id), []).append(row)

        return cls(
            session_code=session_code,
            session_name=session_name,
            rows=rows,
            app_sequence=app_sequence,
            source_files=source_files,
            rounds_by_app={app_name: sorted(rounds) for app_name, rounds in rounds_by_app.items()},
            groups_by_app_round=groups_by_app_round,
        )

    def group_members(self, row: dict[str, str], app_name: str, round_number: int) -> list[dict[str, str]]:
        group_id = text_value(row, app_field_name(app_name, round_number, "group.id_in_subsession"))
        if not group_id:
            return []
        return self.groups_by_app_round.get((app_name, round_number, group_id), [])


def supported_apps() -> set[str]:
    return set(APP_EXTRACTORS) | ZERO_OPPORTUNITY_APPS


def missing_supported_apps() -> list[str]:
    configured_apps = {
        app_name
        for config in settings.SESSION_CONFIGS
        for app_name in config.get("app_sequence", [])
    }
    return sorted(configured_apps - supported_apps())


def collect_opportunities(row: dict[str, str], context: SessionContext) -> list[Opportunity]:
    opportunities: list[Opportunity] = []
    for app_name in context.app_sequence:
        if app_name in ZERO_OPPORTUNITY_APPS:
            continue
        extractor = APP_EXTRACTORS.get(app_name)
        if extractor is None:
            raise ValueError(f"No grading benchmark extractor implemented for {app_name}.")
        opportunities.extend(extractor(row, context))
    return opportunities


def round_numbers_for_app(row: dict[str, str], app_name: str) -> list[int]:
    prefix = f"{app_name}."
    round_numbers = set()
    for key, value in row.items():
        if not value or not key.startswith(prefix):
            continue
        remainder = key[len(prefix):]
        parts = remainder.split(".", 1)
        if parts and parts[0].isdigit():
            round_numbers.add(int(parts[0]))
    return sorted(round_numbers)


def app_field_name(app_name: str, round_number: int, suffix: str) -> str:
    return f"{app_name}.{round_number}.{suffix}"


def text_value(row: dict[str, str], key: str, default: str = "") -> str:
    return (row.get(key, "") or default).strip()


def parse_decimal(value: object, default: Decimal = ZERO) -> Decimal:
    if value is None:
        return default
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    text = str(value).strip()
    if not text:
        return default
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"Could not parse decimal value: {value!r}") from exc


def money_value(row: dict[str, str], key: str, default: Decimal = ZERO) -> Decimal:
    return parse_decimal(row.get(key, ""), default=default)


def int_value(row: dict[str, str], key: str, default: int = 0) -> int:
    text = text_value(row, key)
    if not text:
        return default
    return int(Decimal(text))


def bool_value(row: dict[str, str], key: str) -> bool | None:
    text = text_value(row, key)
    if text == "":
        return None
    if text in {"1", "True", "true"}:
        return True
    if text in {"0", "False", "false"}:
        return False
    raise ValueError(f"Could not parse boolean field {key}={text!r}")


def config_decimal(row: dict[str, str], key: str, default: object) -> Decimal:
    return parse_decimal(row.get(f"session.config.{key}", default), default=parse_decimal(default))


def config_int(row: dict[str, str], key: str, default: int) -> int:
    text = text_value(row, f"session.config.{key}")
    return int(Decimal(text)) if text else int(default)


def parse_schedule_csv(text: str) -> list[Decimal]:
    return [parse_decimal(part.strip()) for part in text.split(",") if part.strip()]


def active_flag(row: dict[str, str], app_name: str, round_number: int) -> bool | None:
    return bool_value(row, app_field_name(app_name, round_number, "player.active_this_round"))


def assigned_role(row: dict[str, str], app_name: str, round_number: int) -> str:
    return text_value(row, app_field_name(app_name, round_number, "player.assigned_role")) or text_value(
        row, app_field_name(app_name, round_number, "player.role")
    )


def raw_round_payoff(row: dict[str, str], app_name: str, round_number: int) -> Decimal:
    raw_key = app_field_name(app_name, round_number, "player.raw_round_payoff")
    if raw_key in row:
        return money_value(row, raw_key)
    round_key = app_field_name(app_name, round_number, "player.round_payoff")
    if round_key in row:
        return money_value(row, round_key)
    return money_value(row, app_field_name(app_name, round_number, "player.payoff"))


def player_payoff(row: dict[str, str], app_name: str, round_number: int) -> Decimal:
    return money_value(row, app_field_name(app_name, round_number, "player.payoff"))


def player_present(row: dict[str, str], app_name: str, round_number: int) -> bool:
    return text_value(row, app_field_name(app_name, round_number, "player.id_in_group")) != ""


def repeated_round_opportunities(
    row: dict[str, str],
    context: SessionContext,
    app_name: str,
    benchmark_fn: Callable[[dict[str, str], SessionContext, str, int], Decimal],
) -> list[Opportunity]:
    opportunities: list[Opportunity] = []
    for round_number in context.rounds_by_app.get(app_name, []):
        if not player_present(row, app_name, round_number):
            continue
        active = active_flag(row, app_name, round_number)
        if active is False:
            opportunities.append(
                Opportunity(
                    app_name=app_name,
                    raw_earnings=ZERO,
                    app_payoff=ZERO,
                    max_attainable=ZERO,
                    active_opportunity=0,
                    sit_out=1,
                )
            )
            continue
        opportunities.append(
            Opportunity(
                app_name=app_name,
                raw_earnings=raw_round_payoff(row, app_name, round_number),
                app_payoff=player_payoff(row, app_name, round_number),
                max_attainable=benchmark_fn(row, context, app_name, round_number),
                active_opportunity=1,
                sit_out=0,
            )
        )
    return opportunities


def one_round_opportunity(
    row: dict[str, str],
    context: SessionContext,
    app_name: str,
    benchmark_fn: Callable[[dict[str, str], SessionContext, str, int], Decimal],
) -> list[Opportunity]:
    rounds = context.rounds_by_app.get(app_name, [])
    if not rounds:
        return []
    round_number = rounds[0]
    if not player_present(row, app_name, round_number):
        return []
    active = active_flag(row, app_name, round_number)
    if active is False:
        return [Opportunity(app_name, ZERO, ZERO, ZERO, 0, 1)]
    return [
        Opportunity(
            app_name=app_name,
            raw_earnings=raw_round_payoff(row, app_name, round_number),
            app_payoff=player_payoff(row, app_name, round_number),
            max_attainable=benchmark_fn(row, context, app_name, round_number),
            active_opportunity=1,
            sit_out=0,
        )
    ]


def repeated_total_opportunity(
    row: dict[str, str],
    context: SessionContext,
    app_name: str,
    benchmark_fn: Callable[[dict[str, str], SessionContext, str, int], Decimal],
) -> list[Opportunity]:
    rounds = [round_number for round_number in context.rounds_by_app.get(app_name, []) if player_present(row, app_name, round_number)]
    if not rounds:
        return []
    raw_total = sum(raw_round_payoff(row, app_name, round_number) for round_number in rounds)
    app_total = sum(player_payoff(row, app_name, round_number) for round_number in rounds)
    max_total = sum(benchmark_fn(row, context, app_name, round_number) for round_number in rounds)
    return [Opportunity(app_name, raw_total, app_total, max_total, 1, 0)]


def centipede_opportunities(row: dict[str, str], context: SessionContext) -> list[Opportunity]:
    rounds = [round_number for round_number in context.rounds_by_app.get("af_centipede", []) if player_present(row, "af_centipede", round_number)]
    if not rounds:
        return []

    if text_value(row, "session.config.role_balanced_classroom") == "1":
        opportunities: list[Opportunity] = []
        for start_round in range(1, max(rounds) + 1, af_centipede.C.NODES_PER_GAME):
            active = active_flag(row, "af_centipede", start_round)
            if active is False:
                opportunities.append(Opportunity("af_centipede", ZERO, ZERO, ZERO, 0, 1))
                continue
            block_rounds = [
                round_number
                for round_number in rounds
                if start_round <= round_number < start_round + af_centipede.C.NODES_PER_GAME
            ]
            if not block_rounds:
                continue
            starting_role = assigned_role(row, "af_centipede", start_round)
            opportunities.append(
                Opportunity(
                    app_name="af_centipede",
                    raw_earnings=sum(raw_round_payoff(row, "af_centipede", round_number) for round_number in block_rounds),
                    app_payoff=sum(player_payoff(row, "af_centipede", round_number) for round_number in block_rounds),
                    max_attainable=centipede_max_for_role(starting_role),
                    active_opportunity=1,
                    sit_out=0,
                )
            )
        return opportunities

    round_number = rounds[0]
    starting_role = assigned_role(row, "af_centipede", round_number) or (
        af_centipede.C.PLAYER_ONE_ROLE
        if int_value(row, app_field_name("af_centipede", round_number, "player.id_in_group"), 1) == 1
        else af_centipede.C.PLAYER_TWO_ROLE
    )
    return [
        Opportunity(
            app_name="af_centipede",
            raw_earnings=sum(player_payoff(row, "af_centipede", candidate) for candidate in rounds),
            app_payoff=sum(player_payoff(row, "af_centipede", candidate) for candidate in rounds),
            max_attainable=centipede_max_for_role(starting_role),
            active_opportunity=1,
            sit_out=0,
        )
    ]


def risk_time_opportunities(row: dict[str, str], context: SessionContext) -> list[Opportunity]:
    round_number = 1
    if not player_present(row, "ar_risk_time_preferences", round_number):
        return []
    pay_task = text_value(row, app_field_name("ar_risk_time_preferences", round_number, "player.pay_task"))
    if not pay_task:
        return []
    pay_row = int_value(row, app_field_name("ar_risk_time_preferences", round_number, "player.pay_row"), 0)
    payoff = player_payoff(row, "ar_risk_time_preferences", round_number)
    return [
        Opportunity(
            app_name="ar_risk_time_preferences",
            raw_earnings=payoff,
            app_payoff=payoff,
            max_attainable=risk_time_max(pay_task, pay_row),
            active_opportunity=1,
            sit_out=0,
        )
    ]


def asset_market_opportunities(row: dict[str, str], context: SessionContext) -> list[Opportunity]:
    rounds = [round_number for round_number in context.rounds_by_app.get("bc_asset_market_bubble", []) if player_present(row, "bc_asset_market_bubble", round_number)]
    if not rounds:
        return []
    total = sum(player_payoff(row, "bc_asset_market_bubble", round_number) for round_number in rounds)
    # This app's wealth path depends on endogenous inventories and counterpart states across rounds.
    # We keep it in the grading export, but use realized final wealth as the v1 benchmark rather than a
    # misleading path counterfactual.
    return [Opportunity("bc_asset_market_bubble", total, total, total, 1, 0)]


def dictator_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    role = assigned_role(row, app_name, round_number)
    if role == aa_dictator.C.RECIPIENT_ROLE:
        return parse_decimal(aa_dictator.C.ENDOWMENT)
    return parse_decimal(aa_dictator.C.ENDOWMENT)


def ultimatum_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    return parse_decimal(ab_ultimatum.C.ENDOWMENT)


def trust_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    endowment = config_decimal(row, "trust_endowment", ac_trust.C.ENDOWMENT)
    multiplier = config_decimal(row, "trust_multiplier", ac_trust.C.MULTIPLIER)
    return endowment * multiplier


def nash_demand_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    return parse_decimal(ad_nash_demand.C.AMOUNT_SHARED)


def guess_two_thirds_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    return parse_decimal(ae_guess_two_thirds.C.JACKPOT)


def centipede_max_for_role(role: str) -> Decimal:
    best = parse_decimal(af_centipede.pot_for_round(af_centipede.C.NODES_PER_GAME)) / 2
    for local_round in range(1, af_centipede.C.NODES_PER_GAME + 1):
        pot = parse_decimal(af_centipede.pot_for_round(local_round))
        if role == af_centipede.C.PLAYER_ONE_ROLE:
            payoff = pot * parse_decimal(af_centipede.C.SHARE_TAKER if local_round % 2 == 1 else af_centipede.C.SHARE_OTHER)
        else:
            payoff = pot * parse_decimal(af_centipede.C.SHARE_TAKER if local_round % 2 == 0 else af_centipede.C.SHARE_OTHER)
        best = max(best, payoff)
    return best


def constant_max(value: object) -> Callable[[dict[str, str], SessionContext, str, int], Decimal]:
    decimal_value = parse_decimal(value)

    def _inner(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
        return decimal_value

    return _inner


def prisoner_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    return max(
        config_decimal(row, "pd_payoff_a", ai_prisoner_mult_rd.C.PAYOFF_A),
        config_decimal(row, "pd_payoff_b", ai_prisoner_mult_rd.C.PAYOFF_B),
        config_decimal(row, "pd_payoff_c", ai_prisoner_mult_rd.C.PAYOFF_C),
        config_decimal(row, "pd_payoff_d", ai_prisoner_mult_rd.C.PAYOFF_D),
    )


def public_goods_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    endowment = parse_decimal(aj_public_goods.C.ENDOWMENT)
    group_size = max(1, int_value(row, app_field_name(app_name, round_number, "group.effective_group_size"), aj_public_goods.C.HEADCOUNT_GROUP_SIZE))
    effective_multiplier = money_value(
        row,
        app_field_name(app_name, round_number, "group.effective_multiplier"),
        default=parse_decimal(aj_public_goods.C.MULTIPLIER),
    )
    others_total = endowment * (group_size - 1)
    own_coefficient = (effective_multiplier / Decimal(group_size)) - ONE
    own_contribution = endowment if own_coefficient > ZERO else ZERO
    total_contribution = others_total + own_contribution
    share = total_contribution * effective_multiplier / Decimal(group_size)
    return endowment - own_contribution + share


def market_schedule_values(row: dict[str, str], app_name: str, round_number: int, field: str) -> list[Decimal]:
    return parse_schedule_csv(text_value(row, app_field_name(app_name, round_number, f"group.{field}")))


def market_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    is_buyer = bool_value(row, app_field_name(app_name, round_number, "player.is_buyer"))
    buyer_values = market_schedule_values(row, app_name, round_number, "buyer_schedule_csv")
    seller_costs = market_schedule_values(row, app_name, round_number, "seller_schedule_csv")
    private_value = money_value(row, app_field_name(app_name, round_number, "player.private_value"))
    private_cost = money_value(row, app_field_name(app_name, round_number, "player.private_cost"))
    if is_buyer:
        if not seller_costs:
            return ZERO
        return max(ZERO, private_value - min(seller_costs))
    if not buyer_values:
        return ZERO
    return max(ZERO, max(buyer_values) - private_cost)


def role_peers(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> list[dict[str, str]]:
    participant_code = text_value(row, "participant.code")
    return [peer for peer in context.group_members(row, app_name, round_number) if text_value(peer, "participant.code") != participant_code]


def two_sided_auction_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    peers = role_peers(row, context, app_name, round_number)
    own_role = assigned_role(row, app_name, round_number) or text_value(row, app_field_name(app_name, round_number, "player.role"))
    private_value = money_value(row, app_field_name(app_name, round_number, "player.private_value"))
    private_cost = money_value(row, app_field_name(app_name, round_number, "player.private_cost"))
    if not peers:
        return ZERO
    peer = peers[0]
    peer_value = money_value(peer, app_field_name(app_name, round_number, "player.private_value"))
    peer_cost = money_value(peer, app_field_name(app_name, round_number, "player.private_cost"))
    if own_role == al_two_sided_auction.C.BUYER_ROLE:
        return max(ZERO, private_value - peer_cost)
    return max(ZERO, peer_value - private_cost)


def auction_private_value_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    return money_value(row, app_field_name(app_name, round_number, "player.private_value"))


def common_value_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    return money_value(row, app_field_name(app_name, round_number, "group.item_value"))


def risk_time_max(pay_task: str, pay_row: int) -> Decimal:
    if pay_task == "risk":
        row = ar_risk_time_preferences.C.RISK_ROWS[pay_row - 1]
        return max(parse_decimal(row["a_high"]), parse_decimal(row["a_low"]), parse_decimal(row["b_high"]), parse_decimal(row["b_low"]))
    if pay_task == "time":
        row = ar_risk_time_preferences.C.TIME_ROWS[pay_row - 1]
        return max(parse_decimal(row["sooner"]), parse_decimal(row["later"]))
    if pay_task == "loss":
        row = ar_risk_time_preferences.C.LOSS_ROWS[pay_row - 1]
        return max(parse_decimal(row["sure"]), parse_decimal(row["gamble_high"]), parse_decimal(row["gamble_low"]))
    row = ar_risk_time_preferences.C.AMBIGUITY_ROWS[pay_row - 1]
    return max(
        parse_decimal(row["known_high"]),
        parse_decimal(row["known_low"]),
        parse_decimal(row["ambiguous_high"]),
        parse_decimal(row["ambiguous_low"]),
    )


def competitiveness_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    task_count = config_int(row, "competitiveness_num_tasks", as_competitiveness.C.NUM_TASKS)
    piece_rate = config_decimal(row, "competitiveness_piece_rate", as_competitiveness.C.PIECE_RATE)
    tournament_rate = config_decimal(row, "competitiveness_tournament_rate", as_competitiveness.C.TOURNAMENT_RATE)
    if round_number == 1:
        return Decimal(task_count) * piece_rate
    if round_number == 2:
        return Decimal(task_count) * tournament_rate
    return Decimal(task_count) * max(piece_rate, tournament_rate)


def bertrand_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    return parse_decimal(at_bertrand.C.MAXIMUM_PRICE)


def cournot_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    max_units = au_cournot.C.MAX_UNITS_PER_PLAYER
    total_capacity = Decimal(au_cournot.C.TOTAL_CAPACITY)
    best = ZERO
    for units in range(0, max_units + 1):
        payoff = Decimal(units) * (total_capacity - Decimal(units))
        best = max(best, payoff)
    return best


def traveler_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    return max(
        parse_decimal(aw_traveler_dilemma.C.MAX_AMOUNT),
        parse_decimal(aw_traveler_dilemma.C.MAX_AMOUNT) - ONE + parse_decimal(aw_traveler_dilemma.C.ADJUSTMENT_ABS),
    )


def volunteer_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    return money_value(row, app_field_name(app_name, round_number, "group.success_benefit"))


def endowment_effect_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    role = assigned_role(row, app_name, round_number)
    if role == az_endowment_effect.C.SELLER_ROLE:
        return parse_decimal(az_endowment_effect.C.CASH_ENDOWMENT + az_endowment_effect.C.PRICE_MAX)
    return parse_decimal(az_endowment_effect.C.CASH_ENDOWMENT + az_endowment_effect.C.MUG_VALUE_TO_BUYER)


def gift_exchange_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    role = assigned_role(row, app_name, round_number)
    if role == ba_gift_exchange.C.EMPLOYER_ROLE:
        max_effort = max(ba_gift_exchange.C.EFFORT_COSTS)
        return parse_decimal(
            ba_gift_exchange.C.BASE_PAYOFF
            + ba_gift_exchange.C.PRODUCTIVITY_PER_EFFORT * max_effort
        )
    min_effort_cost = min(ba_gift_exchange.C.EFFORT_COSTS.values())
    return parse_decimal(ba_gift_exchange.C.BASE_PAYOFF + ba_gift_exchange.C.MAX_WAGE - min_effort_cost)


def common_pool_max(row: dict[str, str], context: SessionContext, app_name: str, round_number: int) -> Decimal:
    return parse_decimal(
        int_value(
            row,
            app_field_name(app_name, round_number, "group.effective_max_extraction"),
            bb_common_pool_resource.C.MAX_EXTRACTION_PER_ROUND,
        )
    )


APP_EXTRACTORS: dict[str, Callable[[dict[str, str], SessionContext], list[Opportunity]]] = {
    "aa_dictator": lambda row, context: repeated_round_opportunities(row, context, "aa_dictator", dictator_max),
    "ab_ultimatum": lambda row, context: repeated_round_opportunities(row, context, "ab_ultimatum", ultimatum_max),
    "ac_trust": lambda row, context: repeated_round_opportunities(row, context, "ac_trust", trust_max),
    "ad_nash_demand": lambda row, context: repeated_round_opportunities(row, context, "ad_nash_demand", nash_demand_max),
    "ae_guess_two_thirds": lambda row, context: repeated_round_opportunities(row, context, "ae_guess_two_thirds", guess_two_thirds_max),
    "af_centipede": centipede_opportunities,
    "ag_matching_pennies": lambda row, context: repeated_round_opportunities(
        row, context, "ag_matching_pennies", constant_max(ag_matching_pennies.C.STAKES)
    ),
    "ah_coordination": lambda row, context: repeated_round_opportunities(
        row, context, "ah_coordination", constant_max(ah_coordination.C.STAKES)
    ),
    "ai_prisoner_mult_rd": lambda row, context: repeated_round_opportunities(row, context, "ai_prisoner_mult_rd", prisoner_max),
    "ai_prisoner_one_rd": lambda row, context: repeated_round_opportunities(row, context, "ai_prisoner_one_rd", prisoner_max),
    "aj_public_goods": lambda row, context: repeated_round_opportunities(row, context, "aj_public_goods", public_goods_max),
    "ak_market_supply_demand": lambda row, context: one_round_opportunity(row, context, "ak_market_supply_demand", market_max),
    "al_two_sided_auction": lambda row, context: repeated_round_opportunities(row, context, "al_two_sided_auction", two_sided_auction_max),
    "am_english_auction": lambda row, context: one_round_opportunity(row, context, "am_english_auction", auction_private_value_max),
    "an_dutch_auction": lambda row, context: one_round_opportunity(row, context, "an_dutch_auction", auction_private_value_max),
    "ao_sealed_bid_first_price": lambda row, context: one_round_opportunity(row, context, "ao_sealed_bid_first_price", auction_private_value_max),
    "ap_sealed_bid_second_price": lambda row, context: one_round_opportunity(row, context, "ap_sealed_bid_second_price", auction_private_value_max),
    "aq_ebay_auction": lambda row, context: one_round_opportunity(row, context, "aq_ebay_auction", auction_private_value_max),
    "ar_risk_time_preferences": risk_time_opportunities,
    "as_competitiveness": lambda row, context: repeated_round_opportunities(row, context, "as_competitiveness", competitiveness_max),
    "at_bertrand": lambda row, context: repeated_round_opportunities(row, context, "at_bertrand", bertrand_max),
    "au_cournot": lambda row, context: repeated_round_opportunities(row, context, "au_cournot", cournot_max),
    "av_common_value_auction": lambda row, context: one_round_opportunity(row, context, "av_common_value_auction", common_value_max),
    "aw_traveler_dilemma": lambda row, context: repeated_round_opportunities(row, context, "aw_traveler_dilemma", traveler_max),
    "ay_volunteer_dilemma": lambda row, context: one_round_opportunity(row, context, "ay_volunteer_dilemma", volunteer_max),
    "az_endowment_effect": lambda row, context: repeated_round_opportunities(row, context, "az_endowment_effect", endowment_effect_max),
    "ba_gift_exchange": lambda row, context: repeated_round_opportunities(row, context, "ba_gift_exchange", gift_exchange_max),
    "bb_common_pool_resource": lambda row, context: repeated_round_opportunities(row, context, "bb_common_pool_resource", common_pool_max),
    "bc_asset_market_bubble": asset_market_opportunities,
}
