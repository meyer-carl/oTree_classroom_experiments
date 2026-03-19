from otree.api import *
import json
import random

from classroom_utils import (
    currency_config_value,
    int_config_value,
    is_incomplete_group,
    next_app,
    unmatched_template_vars,
)


doc = """
Simple competitiveness experiment inspired by Niederle and Vesterlund.
Participants solve math problems under piece-rate and tournament incentives,
then choose their preferred compensation scheme.
"""


class C(BaseConstants):
    NAME_IN_URL = 'competitiveness'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 3

    NUM_TASKS = 6
    TASK_MIN = 10
    TASK_MAX = 99
    TIME_LIMIT_SECONDS = 0

    PIECE_RATE = cu(10)
    TOURNAMENT_RATE = cu(20)
    TOURNAMENT_WINNERS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    max_score = models.IntegerField(initial=0)
    winner_count = models.IntegerField(initial=0)


class Player(BasePlayer):
    task_data = models.LongStringField(initial='')
    num_correct = models.IntegerField(initial=0)
    comp_choice = models.StringField(
        choices=[['piece', 'Piece-rate'], ['tournament', 'Tournament']],
        blank=True,
    )
    is_tournament_winner = models.BooleanField(initial=False)


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


# Dynamic answer fields
for i in range(1, C.NUM_TASKS + 1):
    setattr(
        Player,
        f"answer_{i}",
        models.IntegerField(min=0, blank=True, label=f"Answer {i}"),
    )


def competitiveness_num_tasks(context):
    return max(1, min(C.NUM_TASKS, int_config_value(context, 'competitiveness_num_tasks', C.NUM_TASKS)))


def competitiveness_task_min(context):
    return int_config_value(context, 'competitiveness_task_min', C.TASK_MIN)


def competitiveness_task_max(context):
    configured_max = int_config_value(context, 'competitiveness_task_max', C.TASK_MAX)
    return max(competitiveness_task_min(context), configured_max)


def competitiveness_time_limit(context):
    return int_config_value(context, 'competitiveness_time_limit_seconds', C.TIME_LIMIT_SECONDS)


def competitiveness_piece_rate(context):
    return currency_config_value(context, 'competitiveness_piece_rate', C.PIECE_RATE)


def competitiveness_tournament_rate(context):
    return currency_config_value(context, 'competitiveness_tournament_rate', C.TOURNAMENT_RATE)


def competitiveness_tournament_winners(context):
    return max(1, int_config_value(context, 'competitiveness_tournament_winners', C.TOURNAMENT_WINNERS))


# FUNCTIONS
def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        tasks = []
        for _ in range(competitiveness_num_tasks(p)):
            a = random.randint(competitiveness_task_min(p), competitiveness_task_max(p))
            b = random.randint(competitiveness_task_min(p), competitiveness_task_max(p))
            tasks.append({'a': a, 'b': b})
        p.task_data = json.dumps(tasks)


def _get_tasks(player: Player):
    tasks = json.loads(player.task_data)
    task_list = []
    for i, task in enumerate(tasks, start=1):
        task_list.append(
            dict(index=i, a=task['a'], b=task['b'], field=f'answer_{i}')
        )
    return task_list


def _count_correct(player: Player):
    tasks = json.loads(player.task_data)
    total = 0
    for i, task in enumerate(tasks, start=1):
        answer = getattr(player, f'answer_{i}')
        if answer is not None and answer == task['a'] + task['b']:
            total += 1
    return total


def _tournament_winners(players, top_n):
    if not players:
        return []
    scores = sorted([p.num_correct for p in players], reverse=True)
    cutoff_index = min(top_n, len(scores)) - 1
    cutoff_score = scores[cutoff_index]
    return [p for p in players if p.num_correct >= cutoff_score]


def set_round_results(group: Group):
    players = group.get_players()

    for p in players:
        p.num_correct = _count_correct(p)
        p.is_tournament_winner = False

    group.max_score = max([p.num_correct for p in players]) if players else 0

    round_number = group.subsession.round_number
    if round_number == 1:
        for p in players:
            p.payoff = p.num_correct * competitiveness_piece_rate(group)
        group.winner_count = 0
        return

    if round_number == 2:
        winners = _tournament_winners(players, competitiveness_tournament_winners(group))
        group.winner_count = len(winners)
        for p in players:
            if p in winners:
                p.is_tournament_winner = True
                p.payoff = p.num_correct * competitiveness_tournament_rate(group)
            else:
                p.payoff = cu(0)
        return

    tournament_players = [p for p in players if p.comp_choice == 'tournament']
    winners = _tournament_winners(tournament_players, competitiveness_tournament_winners(group))
    group.winner_count = len(winners)

    for p in players:
        if p.comp_choice == 'piece':
            p.payoff = p.num_correct * competitiveness_piece_rate(group)
        elif p in winners:
            p.is_tournament_winner = True
            p.payoff = p.num_correct * competitiveness_tournament_rate(group)
        else:
            p.payoff = cu(0)


# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            piece_rate=competitiveness_piece_rate(player),
            tournament_rate=competitiveness_tournament_rate(player),
            tournament_winners=competitiveness_tournament_winners(player),
            task_count=competitiveness_num_tasks(player),
            time_limit_seconds=competitiveness_time_limit(player),
        )


class Choice(Page):
    form_model = 'player'
    form_fields = ['comp_choice']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 3


class Task(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        return [f'answer_{i}' for i in range(1, competitiveness_num_tasks(player) + 1)]

    @staticmethod
    def get_timeout_seconds(player: Player):
        limit = competitiveness_time_limit(player)
        return limit if limit else None

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            tasks=_get_tasks(player),
            time_limit_seconds=competitiveness_time_limit(player),
        )


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_round_results


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            round_number=player.round_number,
            max_score=player.group.max_score,
            winner_count=player.group.winner_count,
            piece_rate=competitiveness_piece_rate(player),
            tournament_rate=competitiveness_tournament_rate(player),
            tournament_winners=competitiveness_tournament_winners(player),
            task_count=competitiveness_num_tasks(player),
            time_limit_seconds=competitiveness_time_limit(player),
        )


page_sequence = [Unmatched, Introduction, Choice, Task, ResultsWaitPage, Results]
