from otree.api import *
import json
import random

from classroom_utils import (
    bool_config_value,
    bounded_group_matrix,
    currency_config_value,
    group_matrix_for_sizes,
    int_config_value,
    next_app,
    partition_group_sizes,
)


doc = """
Simple competitiveness experiment inspired by Niederle and Vesterlund.
Participants solve math problems under piece-rate and tournament incentives,
then choose their preferred compensation scheme.
"""


class C(BaseConstants):
    NAME_IN_URL = 'competitiveness'
    PLAYERS_PER_GROUP = None
    HEADCOUNT_GROUP_SIZE = 4
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
    effective_group_size = models.IntegerField(initial=0)


class Player(BasePlayer):
    task_data = models.LongStringField(initial='')
    num_correct = models.IntegerField(initial=0)
    comp_choice = models.StringField(
        choices=[['piece', 'Piece-rate'], ['tournament', 'Tournament']],
        blank=True,
    )
    is_tournament_winner = models.BooleanField(initial=False)


for i in range(1, C.NUM_TASKS + 1):
    setattr(
        Player,
        f"answer_{i}",
        models.IntegerField(min=0, blank=True, label=f"Answer {i}"),
    )


def use_flexible_groups(context):
    return bool_config_value(context, 'competitiveness_flexible_grouping', False)


def target_group_size(context):
    default_size = C.HEADCOUNT_GROUP_SIZE if not use_flexible_groups(context) else 4
    return max(3, int_config_value(context, 'competitiveness_target_group_size', default_size))


def maximum_group_size(context):
    if not use_flexible_groups(context):
        return C.HEADCOUNT_GROUP_SIZE
    configured = int_config_value(context, 'competitiveness_max_group_size', 5)
    return max(target_group_size(context), configured)


def minimum_group_size(context):
    if not use_flexible_groups(context):
        return C.HEADCOUNT_GROUP_SIZE
    configured = int_config_value(context, 'competitiveness_min_group_size', 3)
    return max(3, min(configured, maximum_group_size(context)))


def current_group_size(context):
    group = getattr(context, 'group', context)
    return len(group.get_players())


def is_unmatched(player: Player):
    return current_group_size(player) < minimum_group_size(player)


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
    configured = int_config_value(
        context, 'competitiveness_tournament_winners', C.TOURNAMENT_WINNERS
    )
    return max(1, configured)


def effective_tournament_winners(context):
    group = getattr(context, 'group', context)
    return min(current_group_size(group), competitiveness_tournament_winners(group))


class Unmatched(Page):
    template_name = 'global/Unmatched.html'

    @staticmethod
    def is_displayed(player: Player):
        return is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(required_size=minimum_group_size(player))

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return next_app(upcoming_apps)


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        players = subsession.get_players()
        if use_flexible_groups(subsession):
            random.shuffle(players)
            subsession.set_group_matrix(
                bounded_group_matrix(
                    players,
                    target_group_size(subsession),
                    min_group_size=minimum_group_size(subsession),
                    max_group_size=maximum_group_size(subsession),
                )
            )
        else:
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
        tasks = []
        for _ in range(competitiveness_num_tasks(player)):
            a = random.randint(competitiveness_task_min(player), competitiveness_task_max(player))
            b = random.randint(competitiveness_task_min(player), competitiveness_task_max(player))
            tasks.append({'a': a, 'b': b})
        player.task_data = json.dumps(tasks)


def _get_tasks(player: Player):
    tasks = json.loads(player.task_data)
    return [
        dict(index=i, a=task['a'], b=task['b'], field=f'answer_{i}')
        for i, task in enumerate(tasks, start=1)
    ]


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
    ordered_players = sorted(players, key=lambda player: (-player.num_correct, player.id_in_group))
    return ordered_players[: min(top_n, len(ordered_players))]


def set_round_results(group: Group):
    players = group.get_players()
    group.effective_group_size = len(players)

    for player in players:
        player.num_correct = _count_correct(player)
        player.is_tournament_winner = False

    group.max_score = max([player.num_correct for player in players]) if players else 0
    winner_slots = effective_tournament_winners(group)

    round_number = group.subsession.round_number
    if round_number == 1:
        for player in players:
            player.payoff = player.num_correct * competitiveness_piece_rate(group)
        group.winner_count = 0
        return

    if round_number == 2:
        winners = _tournament_winners(players, winner_slots)
        group.winner_count = len(winners)
        for player in players:
            if player in winners:
                player.is_tournament_winner = True
                player.payoff = player.num_correct * competitiveness_tournament_rate(group)
            else:
                player.payoff = cu(0)
        return

    tournament_players = [player for player in players if player.comp_choice == 'tournament']
    winners = _tournament_winners(tournament_players, winner_slots)
    group.winner_count = len(winners)

    for player in players:
        if player.comp_choice == 'piece':
            player.payoff = player.num_correct * competitiveness_piece_rate(group)
        elif player in winners:
            player.is_tournament_winner = True
            player.payoff = player.num_correct * competitiveness_tournament_rate(group)
        else:
            player.payoff = cu(0)


def page_vars(player: Player):
    return dict(
        piece_rate=competitiveness_piece_rate(player),
        tournament_rate=competitiveness_tournament_rate(player),
        tournament_winners=effective_tournament_winners(player.group),
        configured_tournament_winners=competitiveness_tournament_winners(player),
        task_count=competitiveness_num_tasks(player),
        time_limit_seconds=competitiveness_time_limit(player),
        actual_group_size=player.group.effective_group_size or current_group_size(player),
        use_flexible_groups=use_flexible_groups(player),
    )


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return page_vars(player)


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
            **page_vars(player),
        )


page_sequence = [Unmatched, Introduction, Choice, Task, ResultsWaitPage, Results]
