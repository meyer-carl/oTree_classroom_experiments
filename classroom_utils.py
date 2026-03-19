from __future__ import annotations

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
