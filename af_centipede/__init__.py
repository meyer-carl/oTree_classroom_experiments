from otree.api import *
import random

from classroom_utils import (
    apply_pair_schedule,
    bool_config_value,
    group_matrix_for_sizes,
    next_app,
    normalized_average_payoff,
    partition_group_sizes,
    role_assignment_schedule,
    round_robin_pair_schedule,
    schedule_active_counts,
    schedule_var_key,
    session_config_value,
    unmatched_template_vars,
)

doc = """
Centipede Game:
Players alternate deciding whether to take a larger share of a growing pot or pass it on.
If no one takes by the final node, the pot is split equally.
"""


class C(BaseConstants):
    NAME_IN_URL = 'centipede'
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 2
    NODES_PER_GAME = 6
    CLASSROOM_GAME_BLOCKS = 2
    NUM_ROUNDS = NODES_PER_GAME * CLASSROOM_GAME_BLOCKS
    LEGACY_ACTIVE_ROUNDS = NODES_PER_GAME
    INITIAL_POT = cu(100)
    POT_INCREMENT = cu(50)
    SHARE_TAKER = 0.6
    SHARE_OTHER = 0.4
    PCT_TAKER = SHARE_TAKER * 100
    PCT_OTHER = SHARE_OTHER * 100
    USE_STRATEGY_METHOD = False
    PLAYER_ONE_ROLE = 'Player 1'
    PLAYER_TWO_ROLE = 'Player 2'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    taken = models.BooleanField(initial=False)
    taker = models.IntegerField(null=True)
    take_round = models.IntegerField(null=True)
    take = models.BooleanField(
        choices=[
            [True, 'Stop'],
            [False, 'Pass to your opponent'],
        ],
        widget=widgets.RadioSelect,
        label='',
    )

    def current_pot(self):
        return pot_for_round(local_round_number(self.subsession.round_number))


class Player(BasePlayer):
    assigned_role = models.StringField(blank=True)
    active_this_round = models.BooleanField(initial=True)
    raw_round_payoff = models.CurrencyField(initial=cu(0))


for r in range(1, C.LEGACY_ACTIVE_ROUNDS + 1):
    pot = C.INITIAL_POT + (r - 1) * C.POT_INCREMENT
    setattr(
        Player,
        f'strategy_take_{r}',
        models.BooleanField(
            choices=[
                [True, 'Stop'],
                [False, 'Pass to your opponent'],
            ],
            widget=widgets.RadioSelect,
            label=f"Round {r}: pot = {pot}",
            blank=True,
        ),
    )


BLOCK_SCHEDULE_KEY = schedule_var_key(C.NAME_IN_URL, 'role_cycle_game_schedule')
BLOCK_ROLE_KEY = schedule_var_key(C.NAME_IN_URL, 'role_cycle_game_roles')
BLOCK_ACTIVE_COUNT_KEY = schedule_var_key(C.NAME_IN_URL, 'role_cycle_game_active_counts')


def role_balanced_classroom(context):
    return bool_config_value(context, 'role_balanced_classroom', False)


def active_rounds(context):
    if role_balanced_classroom(context):
        return int(session_config_value(context, 'role_cycle_rounds', C.NUM_ROUNDS))
    return C.LEGACY_ACTIVE_ROUNDS


def role_cycle_payoff_rule(context):
    return session_config_value(context, 'role_cycle_payoff_rule', 'average_active')


def game_block_count(context):
    if not role_balanced_classroom(context):
        return 1
    return max(1, active_rounds(context) // C.NODES_PER_GAME)


def block_index(round_number):
    return (round_number - 1) // C.NODES_PER_GAME


def local_round_number(round_number):
    return ((round_number - 1) % C.NODES_PER_GAME) + 1


def block_start_round(round_number):
    return block_index(round_number) * C.NODES_PER_GAME + 1


def is_block_start_round(context):
    round_number = getattr(context, 'round_number', context)
    return local_round_number(round_number) == 1


def role_name(player: Player):
    if role_balanced_classroom(player):
        return player.assigned_role
    return C.PLAYER_ONE_ROLE if player.id_in_group == 1 else C.PLAYER_TWO_ROLE


def is_active_round(player: Player):
    return player.round_number <= active_rounds(player)


def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.HEADCOUNT_GROUP_SIZE


def creating_session(subsession: Subsession):
    role_map = {}
    if role_balanced_classroom(subsession):
        if subsession.round_number == 1:
            block_schedule = round_robin_pair_schedule(
                [player.participant.code for player in subsession.get_players()],
                game_block_count(subsession),
            )
            subsession.session.vars[BLOCK_SCHEDULE_KEY] = block_schedule
            subsession.session.vars[BLOCK_ROLE_KEY] = role_assignment_schedule(
                block_schedule,
                C.PLAYER_ONE_ROLE,
                C.PLAYER_TWO_ROLE,
            )
            subsession.session.vars[BLOCK_ACTIVE_COUNT_KEY] = schedule_active_counts(block_schedule)

        current_block = block_index(subsession.round_number)
        role_map = subsession.session.vars[BLOCK_ROLE_KEY][current_block]
        apply_pair_schedule(
            subsession,
            subsession.session.vars[BLOCK_SCHEDULE_KEY][current_block],
            role_assignments=role_map,
            primary_role=C.PLAYER_ONE_ROLE,
        )
    elif subsession.round_number == 1:
        players = list(subsession.get_players())
        subsession.set_group_matrix(
            group_matrix_for_sizes(
                players,
                partition_group_sizes(
                    len(players),
                    C.HEADCOUNT_GROUP_SIZE,
                    allow_variable_group_sizes=False,
                    minimum_group_size=1,
                ),
            )
        )
        subsession.session.vars['centipede_force_strategy'] = any(
            len(group.get_players()) < C.HEADCOUNT_GROUP_SIZE for group in subsession.get_groups()
        )
    else:
        if role_balanced_classroom(subsession):
            current_block = block_index(subsession.round_number)
            role_map = subsession.session.vars[BLOCK_ROLE_KEY][current_block]
            apply_pair_schedule(
                subsession,
                subsession.session.vars[BLOCK_SCHEDULE_KEY][current_block],
                role_assignments=role_map,
                primary_role=C.PLAYER_ONE_ROLE,
            )
        else:
            subsession.group_like_round(1)

    for player in subsession.get_players():
        player.active_this_round = is_active_round(player) and not is_unmatched(player)
        player.raw_round_payoff = cu(0)
        player.assigned_role = (
            role_map.get(player.participant.code, '')
            if role_balanced_classroom(subsession)
            else (role_name(player) if player.active_this_round else '')
        )


def use_strategy_method(player: Player):
    return bool_config_value(player, 'use_strategy_method', C.USE_STRATEGY_METHOD) or player.session.vars.get(
        'centipede_force_strategy', False
    )


def strategy_fields_for_player(player: Player):
    fields = []
    for r in range(1, C.NODES_PER_GAME + 1):
        if (r % 2 == 1 and player.id_in_group == 1) or (r % 2 == 0 and player.id_in_group == 2):
            fields.append(f'strategy_take_{r}')
    return fields


def strategy_choice(player: Player, round_number: int):
    return getattr(player, f'strategy_take_{round_number}')


def previous_round_players_in_same_block(player: Player):
    if not role_balanced_classroom(player):
        return list(player.in_previous_rounds())
    start = block_start_round(player.round_number)
    return [player.in_round(r) for r in range(start, player.round_number)]


def game_finished_before_round(player: Player):
    return any(previous.group.taken for previous in previous_round_players_in_same_block(player))


def random_opponent(player: Player):
    target_id = 2 if player.id_in_group == 1 else 1
    candidates = [p for p in player.subsession.get_players() if p.id_in_group == target_id and p != player]
    return random.choice(candidates) if candidates else None


def compute_strategy_outcome(p1: Player, p2: Player):
    for r in range(1, C.NODES_PER_GAME + 1):
        if r % 2 == 1:
            if strategy_choice(p1, r):
                return True, 1, r
        else:
            if strategy_choice(p2, r):
                return True, 2, r
    return False, None, None


def pot_for_round(round_number: int):
    return C.INITIAL_POT + (round_number - 1) * C.POT_INCREMENT


def assign_payoff(player: Player, raw_payoff):
    player.raw_round_payoff = raw_payoff
    if role_balanced_classroom(player) and role_cycle_payoff_rule(player) == 'average_active':
        active_count = player.session.vars[BLOCK_ACTIVE_COUNT_KEY].get(player.participant.code, 1)
        player.payoff = normalized_average_payoff(player, raw_payoff, active_count)
    else:
        player.payoff = raw_payoff


def set_payoffs(group: Group):
    players = group.get_players()
    if not players:
        return

    use_strategy = use_strategy_method(players[0])
    if use_strategy:
        if len(players) < C.HEADCOUNT_GROUP_SIZE:
            lone_player = players[0]
            opponent = random_opponent(lone_player)
            if opponent:
                taken, taker, take_round = compute_strategy_outcome(
                    lone_player if lone_player.id_in_group == 1 else opponent,
                    opponent if lone_player.id_in_group == 1 else lone_player,
                )
            else:
                taken, taker, take_round = False, None, None
            group.taken = taken
            group.taker = taker
            group.take_round = take_round
            r = take_round or C.NODES_PER_GAME
            pot = pot_for_round(r)
            if taken and taker == lone_player.id_in_group:
                assign_payoff(lone_player, pot * C.SHARE_TAKER)
            elif taken:
                assign_payoff(lone_player, pot * C.SHARE_OTHER)
            else:
                assign_payoff(lone_player, pot / 2)
            return

        p1 = group.get_player_by_id(1)
        p2 = group.get_player_by_id(2)
        taken, taker, take_round = compute_strategy_outcome(p1, p2)
        group.taken = taken
        group.taker = taker
        group.take_round = take_round

    take_round = group.field_maybe_none('take_round')
    r = take_round or C.NODES_PER_GAME
    pot = pot_for_round(r)

    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    if group.taken:
        if group.taker == 1:
            assign_payoff(p1, pot * C.SHARE_TAKER)
            assign_payoff(p2, pot * C.SHARE_OTHER)
        else:
            assign_payoff(p2, pot * C.SHARE_TAKER)
            assign_payoff(p1, pot * C.SHARE_OTHER)
    else:
        assign_payoff(p1, pot / 2)
        assign_payoff(p2, pot / 2)


class Unmatched(Page):
    template_name = 'global/Unmatched.html'

    @staticmethod
    def is_displayed(player: Player):
        return not role_balanced_classroom(player) and is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return unmatched_template_vars(C.HEADCOUNT_GROUP_SIZE)

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return next_app(upcoming_apps)


class SitOutRound(Page):
    template_name = 'global/SitOutRound.html'

    @staticmethod
    def is_displayed(player: Player):
        return (
            role_balanced_classroom(player)
            and is_active_round(player)
            and is_unmatched(player)
            and is_block_start_round(player)
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            current_round=block_index(player.round_number) + 1,
            total_rounds=game_block_count(player),
        )


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.active_this_round


class StrategyDecision(Page):
    form_model = 'player'
    form_fields = []

    @staticmethod
    def get_form_fields(player: Player):
        return strategy_fields_for_player(player)

    @staticmethod
    def is_displayed(player: Player):
        if not use_strategy_method(player) or not player.active_this_round:
            return False
        if role_balanced_classroom(player):
            return is_block_start_round(player)
        return player.round_number == 1


class Decision(Page):
    form_model = 'group'
    form_fields = ['take']

    @staticmethod
    def is_displayed(player: Player):
        if not player.active_this_round or use_strategy_method(player):
            return False
        if game_finished_before_round(player):
            return False
        if player.group.taken:
            return False

        local_round = local_round_number(player.round_number)
        return (player.id_in_group == 1 and local_round % 2 == 1) or (
            player.id_in_group == 2 and local_round % 2 == 0
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            pot=pot_for_round(local_round_number(player.round_number)),
            node_round=local_round_number(player.round_number),
            game_number=block_index(player.round_number) + 1,
            starting_role=role_name(player),
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group
        if group.take:
            group.taken = True
            group.taker = player.id_in_group
            group.take_round = local_round_number(player.round_number)


class DecisionWaitPage(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        if not player.active_this_round or use_strategy_method(player):
            return False
        if game_finished_before_round(player):
            return False
        return not player.group.taken and local_round_number(player.round_number) < C.NODES_PER_GAME


class StrategySyncWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player):
        if not player.active_this_round or not use_strategy_method(player):
            return False
        if role_balanced_classroom(player):
            return is_block_start_round(player)
        return player.round_number == 1


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        if not player.active_this_round:
            return False
        if use_strategy_method(player):
            if role_balanced_classroom(player):
                return is_block_start_round(player)
            return player.round_number == 1
        if game_finished_before_round(player):
            return False
        local_round = local_round_number(player.round_number)
        take_round = group.field_maybe_none('take_round')
        return (group.taken and local_round == take_round) or (not group.taken and local_round == C.NODES_PER_GAME)


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        if not player.active_this_round:
            return False
        if use_strategy_method(player):
            if role_balanced_classroom(player):
                return is_block_start_round(player)
            return player.round_number == 1
        if game_finished_before_round(player):
            return False
        local_round = local_round_number(player.round_number)
        take_round = group.field_maybe_none('take_round')
        return (group.taken and local_round == take_round) or (not group.taken and local_round == C.NODES_PER_GAME)

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        take_round = group.field_maybe_none('take_round')
        final_round = take_round or C.NODES_PER_GAME
        taker = group.field_maybe_none('taker')
        return dict(
            final_round=final_round,
            final_pot=pot_for_round(final_round),
            taker=taker,
            share_taker=C.SHARE_TAKER,
            share_other=C.SHARE_OTHER,
            player_stopped=taker == player.id_in_group,
            starting_role=role_name(player),
            game_number=block_index(player.round_number) + 1,
            raw_round_payoff=player.raw_round_payoff,
        )


page_sequence = [
    Unmatched,
    SitOutRound,
    Introduction,
    StrategyDecision,
    Decision,
    DecisionWaitPage,
    StrategySyncWaitPage,
    ResultsWaitPage,
    Results,
]
