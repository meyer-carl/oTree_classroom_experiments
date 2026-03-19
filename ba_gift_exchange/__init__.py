from otree.api import *

doc = """
Gift exchange game with one employer and one worker.
The employer offers a wage and the worker responds with effort.
Higher effort raises the employer's output but also costs the worker more.
"""


class C(BaseConstants):
    NAME_IN_URL = "gift_exchange"
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    BASE_PAYOFF = cu(40)
    WAGE_INCREMENT = cu(10)
    MAX_WAGE = cu(100)
    PRODUCTIVITY_PER_EFFORT = cu(20)
    EFFORT_COSTS = {
        0: cu(0),
        1: cu(2),
        2: cu(5),
        3: cu(9),
        4: cu(14),
        5: cu(20),
    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    wage = models.CurrencyField(
        min=cu(0),
        max=C.MAX_WAGE,
        label="Wage offer",
    )
    effort = models.IntegerField(
        min=0,
        max=max(C.EFFORT_COSTS),
        choices=[[i, str(i)] for i in range(0, max(C.EFFORT_COSTS) + 1)],
        widget=widgets.RadioSelect,
        label="Effort choice",
    )
    employer_payoff = models.CurrencyField(initial=cu(0))
    worker_payoff = models.CurrencyField(initial=cu(0))


class Player(BasePlayer):
    pass


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        subsession.group_randomly()


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


def role_name(player: Player):
    return "Employer" if player.id_in_group == 1 else "Worker"


def set_payoffs(group: Group):
    employer = group.get_player_by_id(1)
    worker = group.get_player_by_id(2)
    effort_cost = C.EFFORT_COSTS[group.effort]

    group.employer_payoff = C.BASE_PAYOFF + C.PRODUCTIVITY_PER_EFFORT * group.effort - group.wage
    group.worker_payoff = C.BASE_PAYOFF + group.wage - effort_cost

    employer.payoff = group.employer_payoff
    worker.payoff = group.worker_payoff


class Introduction(Page):
    pass


class OfferWage(Page):
    form_model = "group"
    form_fields = ["wage"]

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            role=role_name(player),
            page_title="Employer offer",
            prompt="Choose a wage offer for the worker.",
            wage_increment=C.WAGE_INCREMENT,
            productivity=C.PRODUCTIVITY_PER_EFFORT,
        )

    @staticmethod
    def error_message(player: Player, values):
        wage = values["wage"]
        if int(wage) % int(C.WAGE_INCREMENT) != 0:
            return f"Use wage increments of {C.WAGE_INCREMENT}."


class WaitForWage(WaitPage):
    pass


class ChooseEffort(Page):
    form_model = "group"
    form_fields = ["effort"]

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            role=role_name(player),
            page_title="Worker effort",
            prompt="Choose the effort level after seeing the wage offer.",
            effort_costs=C.EFFORT_COSTS,
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(
            role=role_name(player),
            wage=group.wage,
            effort=group.effort,
            effort_cost=C.EFFORT_COSTS[group.effort],
            employer_payoff=group.employer_payoff,
            worker_payoff=group.worker_payoff,
        )


page_sequence = [
    Unmatched,
    Introduction,
    OfferWage,
    WaitForWage,
    ChooseEffort,
    ResultsWaitPage,
    Results,
]
