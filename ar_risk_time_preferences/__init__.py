from otree.api import *
import random

from classroom_utils import bool_config_value


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
    INCLUDE_LOSS = True
    INCLUDE_AMBIGUITY = False

    LOSS_REFERENCE = cu(50)

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

    LOSS_ROWS = [
        dict(p_high=0.5, sure=cu(45), gamble_high=cu(55), gamble_low=cu(35)),
        dict(p_high=0.5, sure=cu(44), gamble_high=cu(58), gamble_low=cu(30)),
        dict(p_high=0.5, sure=cu(43), gamble_high=cu(60), gamble_low=cu(28)),
        dict(p_high=0.5, sure=cu(42), gamble_high=cu(62), gamble_low=cu(25)),
        dict(p_high=0.5, sure=cu(41), gamble_high=cu(65), gamble_low=cu(20)),
    ]

    AMBIGUITY_PROB_MENU = [0.1, 0.3, 0.5, 0.7, 0.9]
    AMBIGUITY_ROWS = [
        dict(known_p_high=0.1, known_high=cu(40), known_low=cu(2), ambiguous_high=cu(40), ambiguous_low=cu(2)),
        dict(known_p_high=0.3, known_high=cu(40), known_low=cu(2), ambiguous_high=cu(40), ambiguous_low=cu(2)),
        dict(known_p_high=0.5, known_high=cu(40), known_low=cu(2), ambiguous_high=cu(40), ambiguous_low=cu(2)),
        dict(known_p_high=0.7, known_high=cu(40), known_low=cu(2), ambiguous_high=cu(40), ambiguous_low=cu(2)),
        dict(known_p_high=0.9, known_high=cu(40), known_low=cu(2), ambiguous_high=cu(40), ambiguous_low=cu(2)),
    ]

    NUM_RISK_ROWS = len(RISK_ROWS)
    NUM_TIME_ROWS = len(TIME_ROWS)
    NUM_LOSS_ROWS = len(LOSS_ROWS)
    NUM_AMBIGUITY_ROWS = len(AMBIGUITY_ROWS)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pay_task = models.StringField(initial='')
    pay_row = models.IntegerField(initial=0)
    pay_amount = models.CurrencyField(initial=cu(0))
    risk_draw = models.FloatField(initial=0)
    ambiguity_realized_p_high = models.FloatField(initial=0)


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

for i in range(1, C.NUM_LOSS_ROWS + 1):
    row = C.LOSS_ROWS[i - 1]
    label = (
        f"Row {i}: A={row['sure']} for sure; "
        f"B=({row['gamble_high']} with probability {row['p_high']}, "
        f"{row['gamble_low']} otherwise)"
    )
    setattr(
        Player,
        f"loss_choice_{i}",
        models.StringField(
            choices=[['A', 'Option A'], ['B', 'Option B']],
            widget=widgets.RadioSelect,
            label=label,
        ),
    )

for i in range(1, C.NUM_AMBIGUITY_ROWS + 1):
    row = C.AMBIGUITY_ROWS[i - 1]
    known_high = int(row['known_p_high'] * 100)
    known_low = 100 - known_high
    label = (
        f"Row {i}: A=({known_high}% {row['known_high']}, {known_low}% {row['known_low']}); "
        f"B=(unknown chance of {row['ambiguous_high']}, {row['ambiguous_low']} otherwise)"
    )
    setattr(
        Player,
        f"ambiguity_choice_{i}",
        models.StringField(
            choices=[['A', 'Option A'], ['B', 'Option B']],
            widget=widgets.RadioSelect,
            label=label,
        ),
    )


# FUNCTIONS
def include_risk(player: Player):
    return bool_config_value(player, 'include_risk', C.INCLUDE_RISK)


def include_time(player: Player):
    return bool_config_value(player, 'include_time', C.INCLUDE_TIME)


def include_loss(player: Player):
    return bool_config_value(player, 'include_loss', C.INCLUDE_LOSS)


def include_ambiguity(player: Player):
    return bool_config_value(player, 'include_ambiguity', C.INCLUDE_AMBIGUITY)


def enabled_tasks(player: Player):
    tasks = []
    if include_risk(player):
        tasks += [('risk', i) for i in range(1, C.NUM_RISK_ROWS + 1)]
    if include_time(player):
        tasks += [('time', i) for i in range(1, C.NUM_TIME_ROWS + 1)]
    if include_loss(player):
        tasks += [('loss', i) for i in range(1, C.NUM_LOSS_ROWS + 1)]
    if include_ambiguity(player):
        tasks += [('ambiguity', i) for i in range(1, C.NUM_AMBIGUITY_ROWS + 1)]
    return tasks


def pick_paid_task(player: Player, tasks):
    forced_task = player.session.vars.get('risk_time_forced_pay_task')
    forced_row = player.session.vars.get('risk_time_forced_pay_row', 1)
    valid_rows = {
        task_row
        for task_name, task_row in tasks
        if task_name == forced_task
    }
    if forced_task and forced_row in valid_rows:
        return forced_task, forced_row
    return random.choice(tasks)


def set_payoffs(group: Group):
    for p in group.get_players():
        tasks = enabled_tasks(p)
        pay_task, pay_row = pick_paid_task(p, tasks)
        p.pay_task = pay_task
        p.pay_row = pay_row
        p.risk_draw = 0
        p.ambiguity_realized_p_high = 0

        if pay_task == 'risk':
            row = C.RISK_ROWS[pay_row - 1]
            choice = getattr(p, f'risk_choice_{pay_row}')
            draw = random.random()
            p.risk_draw = draw
            if choice == 'A':
                payoff = row['a_high'] if draw < row['p_high'] else row['a_low']
            else:
                payoff = row['b_high'] if draw < row['p_high'] else row['b_low']
        elif pay_task == 'time':
            row = C.TIME_ROWS[pay_row - 1]
            choice = getattr(p, f'time_choice_{pay_row}')
            payoff = row['sooner'] if choice == 'A' else row['later']
        elif pay_task == 'loss':
            row = C.LOSS_ROWS[pay_row - 1]
            choice = getattr(p, f'loss_choice_{pay_row}')
            draw = random.random()
            p.risk_draw = draw
            if choice == 'A':
                payoff = row['sure']
            else:
                payoff = row['gamble_high'] if draw < row['p_high'] else row['gamble_low']
        else:
            row = C.AMBIGUITY_ROWS[pay_row - 1]
            choice = getattr(p, f'ambiguity_choice_{pay_row}')
            draw = random.random()
            p.risk_draw = draw
            if choice == 'A':
                resolved_p_high = row['known_p_high']
                payoff = row['known_high'] if draw < resolved_p_high else row['known_low']
            else:
                resolved_p_high = random.choice(C.AMBIGUITY_PROB_MENU)
                p.ambiguity_realized_p_high = resolved_p_high
                payoff = row['ambiguous_high'] if draw < resolved_p_high else row['ambiguous_low']

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
        return include_risk(player)


class TimeChoices(Page):
    form_model = 'player'
    form_fields = [f'time_choice_{i}' for i in range(1, C.NUM_TIME_ROWS + 1)]

    @staticmethod
    def is_displayed(player: Player):
        return include_time(player)


class LossChoices(Page):
    form_model = 'player'
    form_fields = [f'loss_choice_{i}' for i in range(1, C.NUM_LOSS_ROWS + 1)]

    @staticmethod
    def is_displayed(player: Player):
        return include_loss(player)


class AmbiguityChoices(Page):
    form_model = 'player'
    form_fields = [f'ambiguity_choice_{i}' for i in range(1, C.NUM_AMBIGUITY_ROWS + 1)]

    @staticmethod
    def is_displayed(player: Player):
        return include_ambiguity(player)


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
        if pay_task == 'time':
            row = C.TIME_ROWS[pay_row - 1]
            choice = getattr(player, f'time_choice_{pay_row}')
            return dict(
                pay_task=pay_task,
                pay_row=pay_row,
                choice=choice,
                row=row,
            )
        if pay_task == 'loss':
            row = C.LOSS_ROWS[pay_row - 1]
            choice = getattr(player, f'loss_choice_{pay_row}')
            return dict(
                pay_task=pay_task,
                pay_row=pay_row,
                choice=choice,
                row=row,
                loss_reference=C.LOSS_REFERENCE,
            )
        row = C.AMBIGUITY_ROWS[pay_row - 1]
        choice = getattr(player, f'ambiguity_choice_{pay_row}')
        return dict(
            pay_task=pay_task,
            pay_row=pay_row,
            choice=choice,
            row=row,
            ambiguity_realized_p_high=player.ambiguity_realized_p_high,
        )


page_sequence = [Introduction, RiskChoices, TimeChoices, LossChoices, AmbiguityChoices, ResultsWaitPage, Results]
