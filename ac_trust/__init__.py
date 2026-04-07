from otree.api import *
import random

from classroom_utils import (
    apply_pair_schedule,
    bool_config_value,
    group_matrix_for_sizes,
    int_config_value,
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
Trust Game: This is a standard 2-player trust game where the amount sent by player 1 gets
tripled. The trust game was first proposed by
<a href="http://econweb.ucsd.edu/~jandreon/Econ264/papers/Berg%20et%20al%20GEB%201995.pdf" target="_blank">
    Berg, Dickhaut, and McCabe (1995)
</a>.
The code is slightly modified from the original oTree code, found
<a href="https://github.com/oTree-org/oTree/tree/lite" target="_blank">
    here
</a>.
"""


class C(BaseConstants):
    NAME_IN_URL = 'trust'
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 4
    LEGACY_ACTIVE_ROUNDS = 1
    ENDOWMENT = cu(100)
    MULTIPLIER = 3
    USE_STRATEGY_METHOD = False
    SEND_INCREMENT = 10
    STRATEGY_SEND_AMOUNTS = list(range(0, int(ENDOWMENT) + 1, SEND_INCREMENT))
    FIRST_ROLE = 'First mover'
    SECOND_ROLE = 'Second mover'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    sent_amount = models.CurrencyField(
        min=cu(0),
        max=C.ENDOWMENT,
        doc="""Amount sent by the first mover""",
        label="How much do you want to send to the other player?",
    )
    sent_back_amount = models.CurrencyField(
        min=cu(0),
        doc="""Amount sent back by the second mover""",
        label="How much do you want to send back to the other player?",
    )


class Player(BasePlayer):
    assigned_role = models.StringField(blank=True)
    active_this_round = models.BooleanField(initial=True)
    raw_round_payoff = models.CurrencyField(initial=cu(0))


for amount in C.STRATEGY_SEND_AMOUNTS:
    max_back = amount * C.MULTIPLIER
    setattr(
        Player,
        f'strategy_send_back_{amount}',
        models.CurrencyField(
            min=cu(0),
            max=cu(max_back),
            label=f"If the first mover sends {cu(amount)} (tripled to {cu(max_back)}), how much do you send back?",
            blank=True,
        ),
    )


SCHEDULE_KEY = schedule_var_key(C.NAME_IN_URL, 'role_cycle_schedule')
ROLE_KEY = schedule_var_key(C.NAME_IN_URL, 'role_cycle_roles')
ACTIVE_COUNT_KEY = schedule_var_key(C.NAME_IN_URL, 'role_cycle_active_counts')


def role_balanced_classroom(context):
    return bool_config_value(context, 'role_balanced_classroom', False)


def active_rounds(context):
    if role_balanced_classroom(context):
        return int(session_config_value(context, 'role_cycle_rounds', C.NUM_ROUNDS))
    return C.LEGACY_ACTIVE_ROUNDS


def role_cycle_payoff_rule(context):
    return session_config_value(context, 'role_cycle_payoff_rule', 'average_active')


def trust_endowment(context):
    return C.ENDOWMENT


def trust_multiplier(context):
    return int_config_value(context, 'trust_multiplier', C.MULTIPLIER)


def trust_send_increment(context):
    configured = int_config_value(context, 'trust_send_increment', C.SEND_INCREMENT)
    if configured <= 0 or configured % C.SEND_INCREMENT != 0:
        return C.SEND_INCREMENT
    return configured


def trust_strategy_send_amounts(context):
    endowment = int(trust_endowment(context))
    increment = trust_send_increment(context)
    if endowment > int(C.ENDOWMENT) or endowment % C.SEND_INCREMENT != 0:
        endowment = int(C.ENDOWMENT)
    return list(range(0, endowment + 1, increment))


def role_name(player: Player):
    if role_balanced_classroom(player):
        return player.assigned_role
    return C.FIRST_ROLE if player.id_in_group == 1 else C.SECOND_ROLE


def is_active_round(player: Player):
    return player.round_number <= active_rounds(player)


def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.HEADCOUNT_GROUP_SIZE


def strategy_fields(player: Player):
    return [f'strategy_send_back_{amount}' for amount in trust_strategy_send_amounts(player)]


def creating_session(subsession: Subsession):
    role_map = {}
    if role_balanced_classroom(subsession):
        if subsession.round_number == 1:
            schedule = round_robin_pair_schedule(
                [player.participant.code for player in subsession.get_players()],
                active_rounds(subsession),
            )
            subsession.session.vars[SCHEDULE_KEY] = schedule
            subsession.session.vars[ROLE_KEY] = role_assignment_schedule(
                schedule,
                C.FIRST_ROLE,
                C.SECOND_ROLE,
            )
            subsession.session.vars[ACTIVE_COUNT_KEY] = schedule_active_counts(schedule)

        role_map = subsession.session.vars[ROLE_KEY][subsession.round_number - 1]
        apply_pair_schedule(
            subsession,
            subsession.session.vars[SCHEDULE_KEY][subsession.round_number - 1],
            role_assignments=role_map,
            primary_role=C.FIRST_ROLE,
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
        subsession.session.vars['trust_force_strategy'] = any(
            len(group.get_players()) < C.HEADCOUNT_GROUP_SIZE for group in subsession.get_groups()
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
        'trust_force_strategy', False
    )


def random_second_mover(player: Player):
    candidates = [p for p in player.subsession.get_players() if p.id_in_group == 2 and p != player]
    return random.choice(candidates) if candidates else None


def random_first_mover(player: Player):
    candidates = [p for p in player.subsession.get_players() if p.id_in_group == 1 and p != player]
    return random.choice(candidates) if candidates else None


def sent_back_amount_max(group: Group):
    return group.sent_amount * trust_multiplier(group)


def assign_payoff(player: Player, raw_payoff):
    player.raw_round_payoff = raw_payoff
    if role_balanced_classroom(player) and role_cycle_payoff_rule(player) == 'average_active':
        active_count = player.session.vars[ACTIVE_COUNT_KEY].get(player.participant.code, 1)
        player.payoff = normalized_average_payoff(player, raw_payoff, active_count)
    else:
        player.payoff = raw_payoff


def set_payoffs(group: Group):
    endowment = trust_endowment(group)
    multiplier = trust_multiplier(group)
    players = group.get_players()
    if len(players) < C.HEADCOUNT_GROUP_SIZE:
        lone_player = players[0]
        if lone_player.id_in_group == 1:
            group.sent_amount = group.sent_amount or cu(0)
            second_mover = random_second_mover(lone_player)
            if second_mover and use_strategy_method(second_mover):
                field = f'strategy_send_back_{int(group.sent_amount)}'
                group.sent_back_amount = getattr(second_mover, field, cu(0)) or cu(0)
            elif second_mover:
                group.sent_back_amount = second_mover.group.sent_back_amount or cu(0)
            else:
                group.sent_back_amount = cu(0)
            assign_payoff(lone_player, endowment - group.sent_amount + group.sent_back_amount)
        else:
            first_mover = random_first_mover(lone_player)
            group.sent_amount = first_mover.group.sent_amount if first_mover and first_mover.group.sent_amount is not None else cu(0)
            if use_strategy_method(lone_player):
                field = f'strategy_send_back_{int(group.sent_amount)}'
                group.sent_back_amount = getattr(lone_player, field, cu(0)) or cu(0)
            else:
                group.sent_back_amount = group.sent_back_amount or cu(0)
            assign_payoff(lone_player, group.sent_amount * multiplier - group.sent_back_amount)
        return

    first_mover = next(player for player in players if role_name(player) == C.FIRST_ROLE)
    second_mover = next(player for player in players if role_name(player) == C.SECOND_ROLE)
    if use_strategy_method(second_mover):
        field = f'strategy_send_back_{int(group.sent_amount)}'
        group.sent_back_amount = getattr(second_mover, field)

    assign_payoff(first_mover, endowment - group.sent_amount + group.sent_back_amount)
    assign_payoff(second_mover, group.sent_amount * multiplier - group.sent_back_amount)


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
        return role_balanced_classroom(player) and is_active_round(player) and is_unmatched(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(current_round=player.round_number, total_rounds=active_rounds(player))


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.active_this_round

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            endowment=trust_endowment(player),
            multiplier=trust_multiplier(player),
        )


class Send(Page):
    form_model = 'group'
    form_fields = ['sent_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and role_name(player) == C.FIRST_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            endowment=trust_endowment(player),
            multiplier=trust_multiplier(player),
            role_label=role_name(player),
            counterpart_role=C.SECOND_ROLE,
            counterpart_label='second mover',
        )

    @staticmethod
    def error_message(player: Player, values):
        if values['sent_amount'] > trust_endowment(player):
            return f"You cannot send more than the session endowment of {trust_endowment(player)}."
        if use_strategy_method(player):
            amount = int(values['sent_amount'])
            if amount % trust_send_increment(player) != 0:
                return f"Please enter a multiple of {trust_send_increment(player)}."


class SendBackWaitPage(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and not use_strategy_method(player)


class SendBack(Page):
    form_model = 'group'
    form_fields = ['sent_back_amount']

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and role_name(player) == C.SECOND_ROLE and not use_strategy_method(player)

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        tripled_amount = group.sent_amount * trust_multiplier(player)
        return dict(
            tripled_amount=tripled_amount,
            endowment=trust_endowment(player),
            multiplier=trust_multiplier(player),
            role_label=role_name(player),
            counterpart_role=C.FIRST_ROLE,
            counterpart_label='first mover',
        )

    @staticmethod
    def error_message(player: Player, values):
        if values['sent_back_amount'] > sent_back_amount_max(player.group):
            return f"You cannot return more than {sent_back_amount_max(player.group)}."


class StrategySendBack(Page):
    form_model = 'player'
    form_fields = []

    @staticmethod
    def get_form_fields(player: Player):
        return strategy_fields(player)

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and role_name(player) == C.SECOND_ROLE and use_strategy_method(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            endowment=trust_endowment(player),
            multiplier=trust_multiplier(player),
            send_increment=trust_send_increment(player),
        )

    @staticmethod
    def error_message(player: Player, values):
        missing = [name for name in strategy_fields(player) if values.get(name) is None]
        if missing:
            return "Please fill in a response for each possible amount."


class StrategySyncWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and use_strategy_method(player)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        is_first_mover = role_name(player) == C.FIRST_ROLE
        return dict(
            tripled_amount=group.sent_amount * trust_multiplier(player),
            endowment=trust_endowment(player),
            multiplier=trust_multiplier(player),
            send_increment=trust_send_increment(player),
            role_label=role_name(player),
            counterpart_role=C.SECOND_ROLE if is_first_mover else C.FIRST_ROLE,
            counterpart_label='second mover' if is_first_mover else 'first mover',
            is_first_mover=is_first_mover,
            raw_round_payoff=player.raw_round_payoff,
        )


page_sequence = [
    Unmatched,
    SitOutRound,
    Introduction,
    StrategySendBack,
    Send,
    SendBackWaitPage,
    SendBack,
    StrategySyncWaitPage,
    ResultsWaitPage,
    Results,
]
