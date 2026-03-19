from otree.api import *

doc = """
Common-pool resource game with a shared stock that replenishes between rounds.
Players extract from a common resource, and the remaining stock carries forward.
"""


class C(BaseConstants):
    NAME_IN_URL = "common_pool_resource"
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 4

    INITIAL_STOCK = 120
    REGEN_RATE = 0.9
    MAX_EXTRACTION_PER_ROUND = 40


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    start_stock = models.IntegerField(initial=C.INITIAL_STOCK)
    remaining_stock = models.IntegerField(initial=C.INITIAL_STOCK)
    total_extracted = models.IntegerField(initial=0)


class Player(BasePlayer):
    extraction = models.IntegerField(
        min=0,
        max=C.MAX_EXTRACTION_PER_ROUND,
        label="How many units will you extract this round?",
    )
    round_payoff = models.CurrencyField(initial=cu(0))


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        subsession.group_randomly()
        for group in subsession.get_groups():
            group.start_stock = C.INITIAL_STOCK
            group.remaining_stock = C.INITIAL_STOCK
    else:
        subsession.group_like_round(1)
        previous_subsession = subsession.in_previous_rounds()[-1]
        for group in subsession.get_groups():
            previous_group = previous_subsession.get_groups()[group.id_in_subsession - 1]
            group.start_stock = int(round(previous_group.remaining_stock * C.REGEN_RATE))
            group.remaining_stock = group.start_stock


def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.PLAYERS_PER_GROUP


class Unmatched(Page):
    template_name = "global/Unmatched.html"

    @staticmethod
    def is_displayed(player: Player):
        return is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(required_size=C.PLAYERS_PER_GROUP)

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return upcoming_apps[0] if upcoming_apps else None


def max_extraction(group: Group):
    return min(C.MAX_EXTRACTION_PER_ROUND, group.start_stock // C.PLAYERS_PER_GROUP)


def set_payoffs(group: Group):
    players = group.get_players()
    total_requested = sum(p.extraction for p in players)
    group.total_extracted = total_requested
    group.remaining_stock = max(0, group.start_stock - total_requested)

    for p in players:
        p.round_payoff = cu(p.extraction)
        p.payoff = p.round_payoff


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Extract(Page):
    form_model = "player"
    form_fields = ["extraction"]

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(
            round_number=player.round_number,
            start_stock=group.start_stock,
            max_extraction=max_extraction(group),
            regen_rate=C.REGEN_RATE,
        )

    @staticmethod
    def error_message(player: Player, values):
        limit = max_extraction(player.group)
        if values["extraction"] > limit:
            return f"Choose at most {limit} units this round."


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        total_payoff = sum(p.payoff for p in player.in_all_rounds())
        next_round_stock = int(round(group.remaining_stock * C.REGEN_RATE))
        return dict(
            round_number=player.round_number,
            start_stock=group.start_stock,
            total_extracted=group.total_extracted,
            remaining_stock=group.remaining_stock,
            next_round_stock=next_round_stock,
            round_payoff=player.payoff,
            total_payoff=total_payoff,
        )


page_sequence = [Unmatched, Introduction, Extract, ResultsWaitPage, Results]
