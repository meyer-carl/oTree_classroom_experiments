from otree.api import *

from classroom_utils import next_app, session_config_value


doc = """
Keynesian beauty contest / guess 2/3 of the average. Players guess a number and
the closest guess to 2/3 of the average wins.
"""


class C(BaseConstants):
    PLAYERS_PER_GROUP = 1
    HEADCOUNT_GROUP_SIZE = 2
    NUM_ROUNDS = 3
    NAME_IN_URL = "guess_two_thirds"
    JACKPOT = cu(100)
    GUESS_MAX = 100


def group_mode(subsession: "Subsession") -> str:
    return session_config_value(subsession, "guess_two_thirds_group_mode", "pairs")


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    if subsession.round_number > 1:
        subsession.group_like_round(1)
        return

    players = subsession.get_players()
    if group_mode(subsession) == "whole_class":
        subsession.set_group_matrix([players])
        return

    groups = [
        players[index:index + C.HEADCOUNT_GROUP_SIZE]
        for index in range(0, len(players), C.HEADCOUNT_GROUP_SIZE)
    ]
    subsession.set_group_matrix(groups)


class Group(BaseGroup):
    two_thirds_avg = models.FloatField()
    best_guess = models.IntegerField()
    num_winners = models.IntegerField()


class Player(BasePlayer):
    guess = models.IntegerField(
        min=0,
        max=C.GUESS_MAX,
        label="Please pick a number from 0 to 100:",
    )
    is_winner = models.BooleanField(initial=False)


def active_group_size(player: Player) -> int:
    return len(player.group.get_players())


def is_unmatched(player: Player) -> bool:
    if group_mode(player.subsession) == "whole_class":
        return active_group_size(player) < 2
    return active_group_size(player) < C.HEADCOUNT_GROUP_SIZE


class Unmatched(Page):
    template_name = "global/Unmatched.html"

    @staticmethod
    def is_displayed(player: Player):
        return is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        required_size = 2 if group_mode(player.subsession) == "whole_class" else C.HEADCOUNT_GROUP_SIZE
        return dict(required_size=required_size)

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return next_app(upcoming_apps)


def set_payoffs(group: Group):
    players = group.get_players()
    guesses = [player.guess for player in players]
    group.two_thirds_avg = round((2 / 3) * sum(guesses) / len(players), 2)
    group.best_guess = min(guesses, key=lambda guess: abs(guess - group.two_thirds_avg))
    winners = [player for player in players if player.guess == group.best_guess]
    group.num_winners = len(winners)
    for player in players:
        player.is_winner = player in winners
        player.payoff = C.JACKPOT / group.num_winners if player.is_winner else cu(0)


def two_thirds_avg_history(group: Group):
    return [prior_group.two_thirds_avg for prior_group in group.in_previous_rounds()]


def group_vars(player: Player) -> dict:
    return dict(
        whole_class_mode=group_mode(player.subsession) == "whole_class",
        active_group_size=active_group_size(player),
    )


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return group_vars(player)


class Guess(Page):
    form_model = "player"
    form_fields = ["guess"]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            two_thirds_avg_history=two_thirds_avg_history(player.group),
            **group_vars(player),
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            sorted_guesses=sorted(participant.guess for participant in player.group.get_players()),
            **group_vars(player),
        )


page_sequence = [Unmatched, Introduction, Guess, ResultsWaitPage, Results]
