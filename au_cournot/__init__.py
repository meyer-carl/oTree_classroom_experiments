from otree.api import *

from classroom_utils import (
    apply_pair_schedule,
    bool_config_value,
    group_matrix_for_sizes,
    int_config_value,
    next_app,
    normalized_average_payoff,
    partition_group_sizes,
    round_robin_pair_schedule,
    schedule_active_counts,
    schedule_var_key,
    session_config_value,
    unmatched_template_vars,
)


doc = """
Cournot competition: firms choose quantities. The unit price falls as total
output rises. Payoff equals unit price times own quantity.
"""


class C(BaseConstants):
    NAME_IN_URL = 'cournot'
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 4

    TOTAL_CAPACITY = 60
    MAX_UNITS_PER_PLAYER = int(TOTAL_CAPACITY / HEADCOUNT_GROUP_SIZE)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    unit_price = models.CurrencyField()
    total_units = models.IntegerField(doc="""Total units produced by all players""")


class Player(BasePlayer):
    units = models.IntegerField(
        min=0,
        max=C.MAX_UNITS_PER_PLAYER,
        doc="""Quantity of units to produce""",
        label="How many units will you produce?",
    )
    active_this_round = models.BooleanField(initial=True)
    raw_round_payoff = models.CurrencyField(initial=cu(0))


SCHEDULE_KEY = schedule_var_key(C.NAME_IN_URL, 'pair_cycle_schedule')
ACTIVE_COUNT_KEY = schedule_var_key(C.NAME_IN_URL, 'pair_cycle_active_counts')


def pair_cycle_enabled(context):
    return bool_config_value(context, 'pair_cycle_enabled', False)


def pair_cycle_rounds(context):
    return int_config_value(context, 'pair_cycle_rounds', 4) if pair_cycle_enabled(context) else 1


def pair_cycle_payoff_rule(context):
    return session_config_value(context, 'pair_cycle_payoff_rule', 'average_active')


def is_active_round(player: Player):
    return player.round_number <= pair_cycle_rounds(player)

# Helper to detect incomplete groups
def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.HEADCOUNT_GROUP_SIZE

# Page to notify unmatched participants and skip the app
class Unmatched(Page):
    template_name = 'global/Unmatched.html'

    @staticmethod
    def is_displayed(player: Player):
        return not pair_cycle_enabled(player) and is_unmatched(player) and player.round_number == 1

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
        return pair_cycle_enabled(player) and is_active_round(player) and is_unmatched(player)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(current_round=player.round_number, total_rounds=pair_cycle_rounds(player))


def creating_session(subsession: Subsession):
    if pair_cycle_enabled(subsession):
        if subsession.round_number == 1:
            schedule = round_robin_pair_schedule(
                [player.participant.code for player in subsession.get_players()],
                pair_cycle_rounds(subsession),
            )
            subsession.session.vars[SCHEDULE_KEY] = schedule
            subsession.session.vars[ACTIVE_COUNT_KEY] = schedule_active_counts(schedule)

        apply_pair_schedule(
            subsession,
            subsession.session.vars[SCHEDULE_KEY][subsession.round_number - 1],
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
    else:
        subsession.group_like_round(1)

    for player in subsession.get_players():
        player.active_this_round = is_active_round(player) and not is_unmatched(player)
        player.raw_round_payoff = cu(0)


def assign_payoff(player: Player, raw_payoff):
    player.raw_round_payoff = raw_payoff
    if pair_cycle_enabled(player) and pair_cycle_payoff_rule(player) == 'average_active':
        active_rounds = player.session.vars[ACTIVE_COUNT_KEY].get(player.participant.code, 1)
        player.payoff = normalized_average_payoff(player, raw_payoff, active_rounds)
    else:
        player.payoff = raw_payoff


# FUNCTIONS
def set_payoffs(group: Group):
    players = group.get_players()
    group.total_units = sum([p.units for p in players])
    group.unit_price = C.TOTAL_CAPACITY - group.total_units
    for p in players:
        assign_payoff(p, group.unit_price * p.units)


def other_player(player: Player):
    return player.get_others_in_group()[0]


# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.active_this_round


class Decide(Page):
    form_model = 'player'
    form_fields = ['units']

    @staticmethod
    def is_displayed(player: Player):
        return player.active_this_round


class ResultsWaitPage(WaitPage):
    body_text = "Waiting for the other participant to decide."
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
        return dict(other_player_units=other_player(player).units, raw_round_payoff=player.raw_round_payoff)


page_sequence = [Unmatched, SitOutRound, Introduction, Decide, ResultsWaitPage, Results]
