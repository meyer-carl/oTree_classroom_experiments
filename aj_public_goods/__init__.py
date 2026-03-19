from otree.api import *



class C(BaseConstants):
    NAME_IN_URL = 'public_goods_simple'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 2
    ENDOWMENT = cu(100)
    MULTIPLIER = 1.8


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()


class Player(BasePlayer):
    contribution = models.CurrencyField(
        min=0, max=C.ENDOWMENT, label="How much will you contribute?"
    )

# Helper to detect incomplete groups
def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.PLAYERS_PER_GROUP

# Page to notify unmatched participants and skip the app
class Unmatched(Page):
    template_name = 'global/Unmatched.html'

    @staticmethod
    def is_displayed(player: Player):
        return is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(required_size=C.PLAYERS_PER_GROUP)

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return upcoming_apps[0] if upcoming_apps else None


# FUNCTIONS
def set_payoffs(group: Group):
    players = group.get_players()
    contributions = [p.contribution for p in players]
    group.total_contribution = sum(contributions)
    group.individual_share = (
        group.total_contribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
    )
    for p in players:
        p.payoff = C.ENDOWMENT - p.contribution + group.individual_share


# PAGES
class Introduction(Page):
    """Instructions page; show only in round 1."""
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Contribute(Page):
    form_model = 'player'
    form_fields = ['contribution']


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
        all_rounds = player.in_all_rounds()
        total = sum([r.payoff for r in all_rounds])

        return dict(
            total_payoff=total,
        )

page_sequence = [Unmatched, Introduction, Contribute, ResultsWaitPage, Results]
