from otree.api import *
import random

from classroom_utils import (
    bool_config_value,
    currency_config_value,
    ensure_random_paying_round,
    is_incomplete_group,
    next_app,
    total_payoff,
    unmatched_template_vars,
)

doc = """
Repeated Prisoner's Dilemma with fixed matchings.
Players are randomly matched in round 1 and keep the same partner
for all rounds (fixed matching). The session can optionally pick a
single random paying round, or you can pay every round and sum payoffs.
"""

class C(BaseConstants):
    NAME_IN_URL = 'prisoner_mult_rd'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10          # <- set the number of repeated rounds here
    # Payoff matrix constants (adjust to your payoff structure)
    PAYOFF_A = cu(300)  # If I defect & other cooperates
    PAYOFF_B = cu(200)  # If both cooperate
    PAYOFF_C = cu(100)  # If both defect
    PAYOFF_D = cu(0)    # If I cooperate & other defects

    # If you prefer a single paying round, set PAY_SINGLE_ROUND = True
    PAY_SINGLE_ROUND = False

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    cooperate = models.BooleanField(
        choices=[[True, 'Cooperate'], [False, 'Defect']],
        doc="""Player's decision in this round""",
        widget=widgets.RadioSelect,
    )

# Helper to detect incomplete groups
def is_unmatched(player: Player):
    return is_incomplete_group(player, C.PLAYERS_PER_GROUP)

# Page to notify unmatched participants and skip the app
class Unmatched(Page):
    template_name = 'global/Unmatched.html'

    @staticmethod
    def is_displayed(player: Player):
        return is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return unmatched_template_vars(C.PLAYERS_PER_GROUP)

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return next_app(upcoming_apps)


def pd_payoff_a(context):
    return currency_config_value(context, 'pd_payoff_a', C.PAYOFF_A)


def pd_payoff_b(context):
    return currency_config_value(context, 'pd_payoff_b', C.PAYOFF_B)


def pd_payoff_c(context):
    return currency_config_value(context, 'pd_payoff_c', C.PAYOFF_C)


def pd_payoff_d(context):
    return currency_config_value(context, 'pd_payoff_d', C.PAYOFF_D)


def pd_pay_single_round(context):
    return bool_config_value(context, 'pd_pay_single_round', C.PAY_SINGLE_ROUND)

# ---------------- session setup ----------------
def creating_session(subsession: Subsession):
    """
    Round 1: form random groups.
    Rounds 2..NUM_ROUNDS: copy grouping from round 1 (fixed matching).
    Also optionally choose a random paying round and store it in session.vars.
    """
    session = subsession.session

    if subsession.round_number == 1:
        # randomly form pairs for the repeated game
        subsession.group_randomly()

        # optional: choose one random paying round and store it
        ensure_random_paying_round(
            session,
            'paying_round',
            C.NUM_ROUNDS,
            enabled=pd_pay_single_round(session),
        )

    else:
        # copy the groups from round 1 -> fixed matching
        subsession.group_like_round(1)

# ---------------- helper functions ----------------
def other_player(player: Player):
    """Return the single other player in the same group."""
    return player.get_others_in_group()[0]


def set_payoffs(group: Group):
    """
    Called each round by ResultsWaitPage (or equivalent). Computes
    the payoff for this round and stores it in player.payoff.
    If you pay only one random round, use session.vars['paying_round'].
    """
    session = group.subsession.session
    subsession = group.subsession
    p1, p2 = group.get_players()

    # payoff matrix keyed by (my_cooperate, other_cooperate)
    payoff_matrix = {
        (False, True): pd_payoff_a(group),   # I defect, other cooperates
        (True, True): pd_payoff_b(group),    # both cooperate
        (False, False): pd_payoff_c(group),  # both defect
        (True, False): pd_payoff_d(group),   # I cooperate, other defects
    }

    # compute "this round" payoff for each player:
    for p in (p1, p2):
        other = other_player(p)
        # This round's payoff according to the matrix
        round_payoff = payoff_matrix[(p.cooperate, other.cooperate)]

        # If you only pay one random round:
        if pd_pay_single_round(group) and session.vars.get('paying_round') is not None:
            if subsession.round_number == session.vars['paying_round']:
                p.payoff = round_payoff
            else:
                p.payoff = cu(0)
        else:
            # If you pay every round, assign the round payoff (will be summed in final CSV)
            p.payoff = round_payoff

# ---------------- PAGES ----------------
class Introduction(Page):
    """Instructions page; show only in round 1."""
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            total_rounds=C.NUM_ROUNDS,
            payoff_a=pd_payoff_a(player),
            payoff_b=pd_payoff_b(player),
            payoff_c=pd_payoff_c(player),
            payoff_d=pd_payoff_d(player),
            pay_single_round=pd_pay_single_round(player),
        )


class Decision(Page):
    form_model = 'player'
    form_fields = ['cooperate']

    @staticmethod
    def vars_for_template(player: Player):
        # Show opponent's past choices (if any) to help subjects learn
        history = player.in_previous_rounds()
        return dict(history=history)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    def vars_for_template(player: Player):
        """
        Provide current-round and cumulative information to the template:
        - current_round: number of the current round
        - total_rounds: total number of rounds in the session
        - my_decision: this player's decision this round (display string)
        - opponent_decision: other player's decision this round (display string)
        - round_payoff: payoff for this player in the current round
        - total_payoff: sum of payoffs across all rounds
        - all_rounds: list of Player objects for all rounds (for history tables)
        - paying_round: session.vars['paying_round'] if present (may be None)
        """
        session = player.session
        all_rounds = player.in_all_rounds()
        total = total_payoff(player)

        # current-round info
        current_round_number = player.round_number
        total_rounds = C.NUM_ROUNDS
        my_decision = player.field_display('cooperate')
        opponent = other_player(player)
        opponent_decision = opponent.field_display('cooperate')
        round_payoff = player.payoff

        return dict(
            my_decision=my_decision,
            opponent_decision=opponent_decision,
            round_payoff=round_payoff,
            total_payoff=total,
            current_round=current_round_number,
            total_rounds=total_rounds,
            all_rounds=all_rounds,
            paying_round=session.vars.get('paying_round'),
            payoff_a=pd_payoff_a(player),
            payoff_b=pd_payoff_b(player),
            payoff_c=pd_payoff_c(player),
            payoff_d=pd_payoff_d(player),
            pay_single_round=pd_pay_single_round(player),
        )


page_sequence = [Unmatched, Introduction, Decision, ResultsWaitPage, Results]
