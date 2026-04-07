from __future__ import annotations

import math
import random

from otree.api import cu


def session_config_value(context, key, default=None):
    session = getattr(context, "session", context)
    return session.config.get(key, default)


def bool_config_value(context, key, default=False):
    return bool(session_config_value(context, key, default))


def int_config_value(context, key, default=0):
    return int(session_config_value(context, key, default))


def currency_config_value(context, key, default=0):
    return cu(session_config_value(context, key, default))


def currency_list_config_value(context, key, default_values):
    raw = session_config_value(context, key, default_values)
    return [cu(value) for value in raw]


def is_incomplete_group(player, required_size):
    return len(player.group.get_players()) < required_size


def unmatched_template_vars(required_size):
    return dict(required_size=required_size)


def next_app(upcoming_apps):
    return upcoming_apps[0] if upcoming_apps else None


def ensure_random_paying_round(session, key, num_rounds, enabled=True):
    if key not in session.vars:
        session.vars[key] = random.randint(1, num_rounds) if enabled else None
    return session.vars[key]


def total_payoff(player):
    return sum(round_player.payoff for round_player in player.in_all_rounds())


def partition_group_sizes(total_players, target_group_size, allow_variable_group_sizes=False, minimum_group_size=2):
    if total_players <= 0:
        return []

    target = max(minimum_group_size, int(target_group_size))

    if not allow_variable_group_sizes:
        full_groups, remainder = divmod(total_players, target)
        sizes = [target] * full_groups
        if remainder:
            sizes.append(remainder)
        return sizes or [total_players]

    group_count = max(1, round(total_players / target))
    while group_count > 1 and group_count * minimum_group_size > total_players:
        group_count -= 1

    base_size, remainder = divmod(total_players, group_count)
    return [
        base_size + 1 if index < remainder else base_size
        for index in range(group_count)
    ]


def group_matrix_for_sizes(players, group_sizes):
    groups = []
    cursor = 0
    for size in group_sizes:
        groups.append(players[cursor:cursor + size])
        cursor += size
    return groups


def balanced_group_matrix(players, target_group_size, min_group_size=2):
    players = list(players)
    if not players:
        return []
    if len(players) < min_group_size:
        return [players]
    if target_group_size < min_group_size:
        raise ValueError("target_group_size must be at least min_group_size")

    group_count = math.ceil(len(players) / target_group_size)
    max_groups = max(1, len(players) // min_group_size)
    group_count = min(group_count, max_groups)

    base_size = len(players) // group_count
    remainder = len(players) % group_count
    matrix = []
    start = 0
    for index in range(group_count):
        size = base_size + (1 if index < remainder else 0)
        matrix.append(players[start:start + size])
        start += size
    return matrix
