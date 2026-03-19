from otree.api import *
import json
import random


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


# Dynamic answer fields
for i in range(1, C.NUM_TASKS + 1):
    setattr(
        Player,
        f"answer_{i}",
        models.IntegerField(min=0, blank=True, label=f"Answer {i}"),
    )


# FUNCTIONS
def creating_session(subsession: Subsession):
    for p in subsession.get_players():
        tasks = []
        for _ in range(C.NUM_TASKS):
            a = random.randint(C.TASK_MIN, C.TASK_MAX)
            b = random.randint(C.TASK_MIN, C.TASK_MAX)
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
            p.payoff = p.num_correct * C.PIECE_RATE
        group.winner_count = 0
        return

    if round_number == 2:
        winners = _tournament_winners(players, C.TOURNAMENT_WINNERS)
        group.winner_count = len(winners)
        for p in players:
            if p in winners:
                p.is_tournament_winner = True
                p.payoff = p.num_correct * C.TOURNAMENT_RATE
            else:
                p.payoff = cu(0)
        return

    piece_players = [p for p in players if p.comp_choice == 'piece']
    tournament_players = [p for p in players if p.comp_choice == 'tournament']
    winners = _tournament_winners(tournament_players, C.TOURNAMENT_WINNERS)
    group.winner_count = len(winners)

    for p in players:
        if p.comp_choice == 'piece':
            p.payoff = p.num_correct * C.PIECE_RATE
        elif p in winners:
            p.is_tournament_winner = True
            p.payoff = p.num_correct * C.TOURNAMENT_RATE
        else:
            p.payoff = cu(0)


# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Choice(Page):
    form_model = 'player'
    form_fields = ['comp_choice']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 3


class Task(Page):
    form_model = 'player'
    form_fields = [f'answer_{i}' for i in range(1, C.NUM_TASKS + 1)]
    timeout_seconds = C.TIME_LIMIT_SECONDS if C.TIME_LIMIT_SECONDS else None

    @staticmethod
    def vars_for_template(player: Player):
        return dict(tasks=_get_tasks(player))


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_round_results


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            round_number=player.round_number,
            max_score=player.group.max_score,
            winner_count=player.group.winner_count,
        )


page_sequence = [Unmatched, Introduction, Choice, Task, ResultsWaitPage, Results]
