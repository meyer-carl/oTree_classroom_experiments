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
Ultimatum Game: One player decides how to divide a certain amount between themself and the other
player.
The code is adapted from the Dictator game, found
<a href="https://github.com/oTree-org/oTree/tree/lite" target="_blank">
    here
</a>.
"""


class C(BaseConstants):
    NAME_IN_URL = 'ultimatum'
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 4
    LEGACY_ACTIVE_ROUNDS = 1
    ENDOWMENT = cu(100)
    USE_STRATEGY_METHOD = False
    PROPOSER_ROLE = 'Proposer'
    RESPONDER_ROLE = 'Responder'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    offer = models.CurrencyField(
        doc="""Amount the proposer offers to the responder""",
        min=0,
        max=C.ENDOWMENT,
        label="I will offer",
    )
    accepted = models.BooleanField(
        doc="""Whether the offer was accepted by the responder""",
        choices=[
            [True, 'Yes'],
            [False, 'No'],
        ],
        label="Do you accept the offer?",
        widget=widgets.RadioSelect,
    )


class Player(BasePlayer):
    min_accept = models.CurrencyField(
        min=cu(0),
        max=C.ENDOWMENT,
        doc="""Minimum acceptable offer (strategy method)""",
        label="Minimum acceptable offer",
        blank=True,
    )
    assigned_role = models.StringField(blank=True)
    active_this_round = models.BooleanField(initial=True)
    raw_round_payoff = models.CurrencyField(initial=cu(0))


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


def ultimatum_endowment(context):
    return C.ENDOWMENT


def role_name(player: Player):
    if role_balanced_classroom(player):
        return player.assigned_role
    return C.PROPOSER_ROLE if player.id_in_group == 1 else C.RESPONDER_ROLE


def is_active_round(player: Player):
    return player.round_number <= active_rounds(player)


def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.HEADCOUNT_GROUP_SIZE


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
                C.PROPOSER_ROLE,
                C.RESPONDER_ROLE,
            )
            subsession.session.vars[ACTIVE_COUNT_KEY] = schedule_active_counts(schedule)

        role_map = subsession.session.vars[ROLE_KEY][subsession.round_number - 1]
        apply_pair_schedule(
            subsession,
            subsession.session.vars[SCHEDULE_KEY][subsession.round_number - 1],
            role_assignments=role_map,
            primary_role=C.PROPOSER_ROLE,
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
        subsession.session.vars['ultimatum_force_strategy'] = any(
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
        'ultimatum_force_strategy', False
    )


def random_responder(player: Player):
    candidates = [p for p in player.subsession.get_players() if p.id_in_group == 2 and p != player]
    return random.choice(candidates) if candidates else None


def random_proposer(player: Player):
    candidates = [p for p in player.subsession.get_players() if p.id_in_group == 1 and p != player]
    return random.choice(candidates) if candidates else None


def responder_accepts_offer(responder: Player | None, offer):
    if responder is None:
        return False
    if use_strategy_method(responder) and responder.min_accept is not None:
        return offer >= responder.min_accept
    return responder.group.accepted


def assign_payoff(player: Player, raw_payoff):
    player.raw_round_payoff = raw_payoff
    if role_balanced_classroom(player) and role_cycle_payoff_rule(player) == 'average_active':
        active_count = player.session.vars[ACTIVE_COUNT_KEY].get(player.participant.code, 1)
        player.payoff = normalized_average_payoff(player, raw_payoff, active_count)
    else:
        player.payoff = raw_payoff


def set_payoffs(group: Group):
    endowment = ultimatum_endowment(group)
    players = group.get_players()
    if len(players) < C.HEADCOUNT_GROUP_SIZE:
        lone_player = players[0]
        if lone_player.id_in_group == 1:
            offer = group.offer or cu(0)
            responder = random_responder(lone_player)
        else:
            proposer = random_proposer(lone_player)
            offer = proposer.group.offer if proposer and proposer.group.offer is not None else cu(0)
            group.offer = offer
            responder = lone_player if proposer else None
        accepted = responder_accepts_offer(responder, offer)
        group.accepted = accepted
        if lone_player.id_in_group == 1:
            assign_payoff(lone_player, endowment - offer if accepted else cu(0))
        else:
            assign_payoff(lone_player, offer if accepted else cu(0))
        return

    proposer = next(player for player in players if role_name(player) == C.PROPOSER_ROLE)
    responder = next(player for player in players if role_name(player) == C.RESPONDER_ROLE)

    if use_strategy_method(responder):
        group.accepted = group.offer >= (responder.min_accept or cu(0))

    if group.accepted:
        assign_payoff(proposer, endowment - group.offer)
        assign_payoff(responder, group.offer)
    else:
        assign_payoff(proposer, cu(0))
        assign_payoff(responder, cu(0))


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
        return dict(endowment=ultimatum_endowment(player))


class Offer(Page):
    form_model = 'group'
    form_fields = ['offer']

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and role_name(player) == C.PROPOSER_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            endowment=ultimatum_endowment(player),
            role_label=role_name(player),
            counterpart_role=C.RESPONDER_ROLE,
            counterpart_label='responder',
        )

    @staticmethod
    def error_message(player: Player, values):
        if values['offer'] > ultimatum_endowment(player):
            return f"The offer cannot exceed the session endowment of {ultimatum_endowment(player)}."


class WaitForOtherPlayers(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and not use_strategy_method(player)


class Response(Page):
    form_model = 'group'
    form_fields = ['accepted']

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and role_name(player) == C.RESPONDER_ROLE and not use_strategy_method(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            offer=player.group.offer,
            endowment=ultimatum_endowment(player),
            role_label=role_name(player),
            counterpart_role=C.PROPOSER_ROLE,
            counterpart_label='proposer',
        )


class StrategyResponse(Page):
    form_model = 'player'
    form_fields = ['min_accept']

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round and role_name(player) == C.RESPONDER_ROLE and use_strategy_method(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endowment=ultimatum_endowment(player))


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
        endowment = ultimatum_endowment(player)
        is_proposer = role_name(player) == C.PROPOSER_ROLE
        return dict(
            offer=player.group.offer,
            accepted=player.group.accepted,
            kept=endowment - player.group.offer,
            endowment=endowment,
            is_proposer=is_proposer,
            role_label=role_name(player),
            counterpart_role=C.RESPONDER_ROLE if is_proposer else C.PROPOSER_ROLE,
            counterpart_label='responder' if is_proposer else 'proposer',
            raw_round_payoff=player.raw_round_payoff,
        )


page_sequence = [
    Unmatched,
    SitOutRound,
    Introduction,
    StrategyResponse,
    Offer,
    WaitForOtherPlayers,
    Response,
    StrategySyncWaitPage,
    ResultsWaitPage,
    Results,
]
