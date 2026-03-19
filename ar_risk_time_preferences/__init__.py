from otree.api import *
import random


doc = """
Lottery choices for risk and time preferences using simple multiple price lists.
One row is randomly selected for payment.
"""


class C(BaseConstants):
    NAME_IN_URL = 'risk_time_preferences'
    PLAYERS_PER_GROUP = 1
    NUM_ROUNDS = 1

    INCLUDE_RISK = True
    INCLUDE_TIME = True

    RISK_ROWS = [
        dict(p_high=0.1, a_high=cu(20), a_low=cu(16), b_high=cu(40), b_low=cu(2)),
        dict(p_high=0.3, a_high=cu(20), a_low=cu(16), b_high=cu(40), b_low=cu(2)),
        dict(p_high=0.5, a_high=cu(20), a_low=cu(16), b_high=cu(40), b_low=cu(2)),
        dict(p_high=0.7, a_high=cu(20), a_low=cu(16), b_high=cu(40), b_low=cu(2)),
        dict(p_high=0.9, a_high=cu(20), a_low=cu(16), b_high=cu(40), b_low=cu(2)),
    ]

    TIME_ROWS = [
        dict(sooner=cu(10), later=cu(11), delay='1 week'),
        dict(sooner=cu(10), later=cu(12), delay='1 week'),
        dict(sooner=cu(10), later=cu(14), delay='1 month'),
        dict(sooner=cu(10), later=cu(16), delay='1 month'),
        dict(sooner=cu(10), later=cu(20), delay='3 months'),
    ]

    NUM_RISK_ROWS = len(RISK_ROWS)
    NUM_TIME_ROWS = len(TIME_ROWS)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pay_task = models.StringField(initial='')
    pay_row = models.IntegerField(initial=0)
    pay_amount = models.CurrencyField(initial=cu(0))
    risk_draw = models.FloatField(initial=0)


# Dynamic fields for multiple price lists
for i in range(1, C.NUM_RISK_ROWS + 1):
    row = C.RISK_ROWS[i - 1]
    p_high = int(row['p_high'] * 100)
    p_low = 100 - p_high
    label = (
        f"Row {i}: A=({p_high}% {row['a_high']}, {p_low}% {row['a_low']}); "
        f"B=({p_high}% {row['b_high']}, {p_low}% {row['b_low']})"
    )
    setattr(
        Player,
        f"risk_choice_{i}",
        models.StringField(
            choices=[['A', 'Option A'], ['B', 'Option B']],
            widget=widgets.RadioSelect,
            label=label,
        ),
    )

for i in range(1, C.NUM_TIME_ROWS + 1):
    row = C.TIME_ROWS[i - 1]
    label = (
        f"Row {i}: A={row['sooner']} now; "
        f"B={row['later']} in {row['delay']}"
    )
    setattr(
        Player,
        f"time_choice_{i}",
        models.StringField(
            choices=[['A', 'Option A'], ['B', 'Option B']],
            widget=widgets.RadioSelect,
            label=label,
        ),
    )


# FUNCTIONS
def set_payoffs(group: Group):
    for p in group.get_players():
        tasks = []
        if C.INCLUDE_RISK:
            tasks += [('risk', i) for i in range(1, C.NUM_RISK_ROWS + 1)]
        if C.INCLUDE_TIME:
            tasks += [('time', i) for i in range(1, C.NUM_TIME_ROWS + 1)]

        pay_task, pay_row = random.choice(tasks)
        p.pay_task = pay_task
        p.pay_row = pay_row

        if pay_task == 'risk':
            row = C.RISK_ROWS[pay_row - 1]
            choice = getattr(p, f'risk_choice_{pay_row}')
            draw = random.random()
            p.risk_draw = draw
            if choice == 'A':
                payoff = row['a_high'] if draw < row['p_high'] else row['a_low']
            else:
                payoff = row['b_high'] if draw < row['p_high'] else row['b_low']
        else:
            row = C.TIME_ROWS[pay_row - 1]
            choice = getattr(p, f'time_choice_{pay_row}')
            payoff = row['sooner'] if choice == 'A' else row['later']

        p.pay_amount = payoff
        p.payoff = payoff


# PAGES
class Introduction(Page):
    pass


class RiskChoices(Page):
    form_model = 'player'
    form_fields = [f'risk_choice_{i}' for i in range(1, C.NUM_RISK_ROWS + 1)]

    @staticmethod
    def is_displayed(player: Player):
        return C.INCLUDE_RISK


class TimeChoices(Page):
    form_model = 'player'
    form_fields = [f'time_choice_{i}' for i in range(1, C.NUM_TIME_ROWS + 1)]

    @staticmethod
    def is_displayed(player: Player):
        return C.INCLUDE_TIME


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        pay_task = player.pay_task
        pay_row = player.pay_row
        if pay_task == 'risk':
            row = C.RISK_ROWS[pay_row - 1]
            choice = getattr(player, f'risk_choice_{pay_row}')
            return dict(
                pay_task=pay_task,
                pay_row=pay_row,
                choice=choice,
                row=row,
            )
        row = C.TIME_ROWS[pay_row - 1]
        choice = getattr(player, f'time_choice_{pay_row}')
        return dict(
            pay_task=pay_task,
            pay_row=pay_row,
            choice=choice,
            row=row,
        )


page_sequence = [Introduction, RiskChoices, TimeChoices, ResultsWaitPage, Results]
