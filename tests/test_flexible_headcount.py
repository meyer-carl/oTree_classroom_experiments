from __future__ import annotations

from types import SimpleNamespace

from otree.api import cu

import am_english_auction as english
import an_dutch_auction as dutch
import ao_sealed_bid_first_price as first_price
import ap_sealed_bid_second_price as second_price
import aq_ebay_auction as ebay
import av_common_value_auction as common_value
import ay_volunteer_dilemma as volunteer
import as_competitiveness as competitiveness
import bb_common_pool_resource as common_pool
import ak_market_supply_demand as market
from classroom_utils import bounded_group_sizes, role_assignment_schedule, round_robin_pair_schedule, schedule_active_counts


class FakeGroup:
    def __init__(self, players, config=None, **attrs):
        self._players = players
        self.session = SimpleNamespace(config=config or {})
        for key, value in attrs.items():
            setattr(self, key, value)
        for player in players:
            player.group = self

    def get_players(self):
        return self._players


def _players(field_name, values, private_value=cu(120)):
    players = []
    for index, value in enumerate(values, start=1):
        player = SimpleNamespace(
            id_in_group=index,
            private_value=private_value,
            is_winner=False,
            payoff=cu(0),
        )
        setattr(player, field_name, cu(value))
        players.append(player)
    return players


def test_private_auction_bounded_group_sizes():
    expected = {
        2: [2],
        3: [3],
        4: [4],
        5: [5],
        7: [4, 3],
        9: [5, 4],
        11: [4, 4, 3],
    }
    for total_players, expected_sizes in expected.items():
        assert bounded_group_sizes(total_players, 4, min_group_size=2, max_group_size=6) == expected_sizes


def test_common_value_bounded_group_sizes():
    expected = {
        2: [2],
        3: [3],
        4: [4],
        5: [5],
        7: [4, 3],
        9: [5, 4],
        11: [4, 4, 3],
    }
    for total_players, expected_sizes in expected.items():
        assert bounded_group_sizes(total_players, 4, min_group_size=3, max_group_size=6) == expected_sizes


def test_variable_group_size_candidates_have_no_singletons_when_feasible():
    assert bounded_group_sizes(7, 3, min_group_size=2, max_group_size=5) == [4, 3]
    assert bounded_group_sizes(9, 4, min_group_size=3, max_group_size=5) == [5, 4]


def test_round_robin_pair_schedule_rotates_the_spare():
    schedule = round_robin_pair_schedule(["p1", "p2", "p3", "p4", "p5"], 4)
    spares = []
    for round_groups in schedule:
        paired = {code for group in round_groups if len(group) == 2 for code in group}
        spare = ({"p1", "p2", "p3", "p4", "p5"} - paired).pop()
        spares.append(spare)
    assert len(set(spares)) == 4


def test_role_assignment_schedule_balances_roles_across_rounds():
    schedule = round_robin_pair_schedule(["p1", "p2", "p3", "p4", "p5"], 4)
    assignments = role_assignment_schedule(schedule, "A", "B")
    counts = {}
    for round_assignment in assignments:
        for participant_code, role in round_assignment.items():
            counts.setdefault(participant_code, []).append(role)
    for roles in counts.values():
        assert "A" in roles
        assert "B" in roles


def test_pair_schedule_active_counts_only_include_played_rounds():
    schedule = round_robin_pair_schedule(["p1", "p2", "p3"], 4)
    counts = schedule_active_counts(schedule)
    assert sum(counts.values()) == 8
    assert min(counts.values()) >= 2


def test_english_auction_outcomes_scale_to_actual_bidder_count():
    for bidder_count in [3, 4, 5, 6]:
        players = _players('exit_price', [100, 90, 80, 70, 60, 50][:bidder_count])
        group = FakeGroup(players)
        english.set_payoffs(group)
        assert group.actual_bidder_count == bidder_count
        assert group.winning_price == cu(90)
        assert players[0].is_winner is True
        assert players[0].payoff == cu(30)
        assert all(player.payoff == cu(0) for player in players[1:])


def test_dutch_auction_outcomes_scale_to_actual_bidder_count():
    for bidder_count in [3, 4, 5, 6]:
        players = _players('stop_price', [100, 90, 80, 70, 60, 50][:bidder_count])
        group = FakeGroup(players)
        dutch.set_payoffs(group)
        assert group.actual_bidder_count == bidder_count
        assert group.winning_price == cu(100)
        assert players[0].is_winner is True
        assert players[0].payoff == cu(20)


def test_first_price_auction_outcomes_scale_to_actual_bidder_count():
    for bidder_count in [3, 4, 5, 6]:
        players = _players('bid', [100, 90, 80, 70, 60, 50][:bidder_count])
        group = FakeGroup(players)
        first_price.set_payoffs(group)
        assert group.actual_bidder_count == bidder_count
        assert group.winning_bid == cu(100)
        assert players[0].is_winner is True
        assert players[0].payoff == cu(20)


def test_second_price_auction_outcomes_scale_to_actual_bidder_count():
    for bidder_count in [3, 4, 5, 6]:
        players = _players('bid', [100, 90, 80, 70, 60, 50][:bidder_count])
        group = FakeGroup(players)
        second_price.set_payoffs(group)
        assert group.actual_bidder_count == bidder_count
        assert group.winning_price == cu(90)
        assert players[0].is_winner is True
        assert players[0].payoff == cu(30)


def test_ebay_auction_outcomes_scale_to_actual_bidder_count():
    for bidder_count in [3, 4, 5, 6]:
        players = _players('proxy_bid', [100, 80, 60, 40, 20, 10][:bidder_count])
        group = FakeGroup(players)
        ebay.set_payoffs(group)
        assert group.actual_bidder_count == bidder_count
        assert group.winning_price == cu(81)
        assert players[0].is_winner is True
        assert players[0].payoff == cu(39)


def test_common_value_auction_outcomes_scale_to_actual_bidder_count():
    for bidder_count in [3, 4, 5, 6]:
        players = _players('bid_amount', [5, 4, 3, 2, 1, 0][:bidder_count], private_value=cu(0))
        group = FakeGroup(players, item_value=cu(8))
        common_value.set_winner(group)
        assert group.actual_bidder_count == bidder_count
        assert group.highest_bid == cu(5)
        assert players[0].is_winner is True
        assert players[0].payoff == cu(3)


def test_volunteer_flexible_payoffs_match_target_group_defaults():
    config = {
        'volunteer_flexible_grouping': True,
        'volunteer_scale_payoffs': True,
        'volunteer_benefit_per_person': 100,
        'volunteer_cost_per_person': 40,
    }
    for group_size in [2, 3, 4, 5]:
        players = [
            SimpleNamespace(id_in_group=index + 1, volunteer=index == 0, payoff=cu(0))
            for index in range(group_size)
        ]
        group = FakeGroup(players, config=config)
        volunteer.set_payoffs(group)
        assert group.effective_group_size == group_size
        assert group.success_benefit == cu(100)
        assert group.volunteer_cost == cu(40)
        assert group.total_group_benefit == cu(100 * group_size)
        assert players[0].payoff == cu(60)
        for player in players[1:]:
            assert player.payoff == cu(100)


def test_competitiveness_keeps_one_default_winner_in_flexible_groups():
    config = {'competitiveness_flexible_grouping': True}
    for group_size in [3, 4, 5]:
        players = [SimpleNamespace(id_in_group=index + 1) for index in range(group_size)]
        group = FakeGroup(players, config=config)
        assert competitiveness.effective_tournament_winners(group) == 1


def test_common_pool_scaling_uses_actual_group_size():
    config = {
        'common_pool_flexible_grouping': True,
        'common_pool_initial_stock_per_person': 30,
        'common_pool_max_extraction_per_person': 30,
        'common_pool_regen_rate': 0.9,
    }
    for group_size in [3, 4, 5]:
        players = [SimpleNamespace(id_in_group=index + 1) for index in range(group_size)]
        group = FakeGroup(players, config=config, start_stock=30 * group_size, effective_group_size=group_size)
        assert common_pool.starting_stock_for_group(group_size, group.session) == 30 * group_size
        assert common_pool.effective_max_extraction(group) == 30


def test_whole_class_market_generates_balanced_schedules():
    config = {
        'classroom_whole_market': True,
        'market_min_headcount': 4,
        'buyer_value_high': 100,
        'buyer_value_low': 70,
        'seller_cost_low': 20,
        'seller_cost_high': 50,
    }
    group = FakeGroup([], config=config, actual_num_buyers=3, actual_num_sellers=2)
    assert market.generated_buyer_values(group, 3) == [cu(100), cu(85), cu(70)]
    assert market.generated_seller_costs(group, 2) == [cu(20), cu(50)]
