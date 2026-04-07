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


def bounded_group_sizes(total_players, preferred_group_size, min_group_size=2, max_group_size=None):
    if total_players <= 0:
        return []

    min_size = max(1, int(min_group_size))
    preferred = max(min_size, int(preferred_group_size))
    max_size = max(preferred, int(max_group_size or preferred))

    if total_players < min_size:
        return [total_players]

    if min_size <= total_players <= max_size:
        return [total_players]

    min_groups = math.ceil(total_players / max_size)
    max_groups = total_players // min_size

    if min_groups <= max_groups:
        candidate_group_counts = range(min_groups, max_groups + 1)
        best_group_count = min(
            candidate_group_counts,
            key=lambda count: (
                abs(total_players / count - preferred),
                abs(count - round(total_players / preferred)),
                count,
            ),
        )
        base_size, remainder = divmod(total_players, best_group_count)
        return [
            base_size + 1 if index < remainder else base_size
            for index in range(best_group_count)
        ]

    return [
        len(group)
        for group in balanced_group_matrix(
            list(range(total_players)),
            preferred,
            min_group_size=min_size,
        )
    ]


def bounded_group_matrix(players, preferred_group_size, min_group_size=2, max_group_size=None):
    players = list(players)
    if not players:
        return []
    return group_matrix_for_sizes(
        players,
        bounded_group_sizes(
            len(players),
            preferred_group_size,
            min_group_size=min_group_size,
            max_group_size=max_group_size,
        ),
    )


def round_robin_pair_schedule(participant_codes, num_rounds):
    participant_codes = list(participant_codes)
    if not participant_codes or num_rounds <= 0:
        return []

    slots = participant_codes[:]
    if len(slots) % 2 == 1:
        slots.append(None)

    unique_rounds = max(1, len(slots) - 1)
    current = slots[:]
    schedule = []

    for _ in range(unique_rounds):
        round_groups = []
        half = len(current) // 2
        for index in range(half):
            left = current[index]
            right = current[-(index + 1)]
            group = [code for code in (left, right) if code is not None]
            if group:
                round_groups.append(group)
        schedule.append(round_groups)

        if len(current) > 2:
            current = [current[0], current[-1], *current[1:-1]]

    return [
        [group[:] for group in schedule[index % len(schedule)]]
        for index in range(num_rounds)
    ]


def schedule_active_counts(schedule):
    counts = {}
    for round_groups in schedule:
        for group in round_groups:
            if len(group) == 2:
                for participant_code in group:
                    counts[participant_code] = counts.get(participant_code, 0) + 1
    return counts


def role_assignment_schedule(schedule, role_a, role_b):
    assignments = []
    last_role = {}
    role_counts = {}

    def option_score(participant_code, proposed_role):
        counts = role_counts.setdefault(participant_code, {role_a: 0, role_b: 0})
        other_role = role_b if proposed_role == role_a else role_a
        repeat_penalty = 4 if last_role.get(participant_code) == proposed_role else 0
        proposed_count = counts[proposed_role] + 1
        other_count = counts[other_role]
        balance_penalty = abs(proposed_count - other_count)
        return repeat_penalty + balance_penalty

    for round_groups in schedule:
        round_assignment = {}
        for group in round_groups:
            if len(group) != 2:
                continue

            first, second = group
            option_one = option_score(first, role_a) + option_score(second, role_b)
            option_two = option_score(first, role_b) + option_score(second, role_a)

            if option_two < option_one:
                first_role, second_role = role_b, role_a
            else:
                first_role, second_role = role_a, role_b

            round_assignment[first] = first_role
            round_assignment[second] = second_role

            role_counts.setdefault(first, {role_a: 0, role_b: 0})[first_role] += 1
            role_counts.setdefault(second, {role_a: 0, role_b: 0})[second_role] += 1
            last_role[first] = first_role
            last_role[second] = second_role

        assignments.append(round_assignment)

    return assignments


def schedule_var_key(app_name, suffix):
    return f"{app_name}_{suffix}"


def apply_pair_schedule(subsession, round_groups, role_assignments=None, primary_role=None):
    player_by_code = {
        player.participant.code: player
        for player in subsession.get_players()
    }
    matrix = []
    for group_codes in round_groups:
        group_players = [player_by_code[code] for code in group_codes if code in player_by_code]
        if role_assignments and primary_role and len(group_players) == 2:
            group_players.sort(
                key=lambda player: 0 if role_assignments.get(player.participant.code) == primary_role else 1
            )
        matrix.append(group_players)
    subsession.set_group_matrix(matrix)


def normalized_average_payoff(player, raw_payoff, active_round_count):
    if active_round_count <= 0:
        return cu(0)
    return raw_payoff / active_round_count
