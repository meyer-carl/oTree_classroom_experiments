from otree.api import *

from classroom_utils import (
    balanced_group_matrix,
    bool_config_value,
    group_matrix_for_sizes,
    int_config_value,
    next_app,
    partition_group_sizes,
)


class C(BaseConstants):
    NAME_IN_URL = "public_goods_simple"
    PLAYERS_PER_GROUP = 1
    HEADCOUNT_GROUP_SIZE = 3
    NUM_ROUNDS = 2
    ENDOWMENT = cu(100)
    MULTIPLIER = 1.8


def use_flexible_groups(context) -> bool:
    return bool_config_value(context, "public_goods_flexible_grouping", False)


def target_group_size(context) -> int:
    return max(2, int_config_value(context, "public_goods_target_group_size", C.HEADCOUNT_GROUP_SIZE))


def minimum_group_size(context) -> int:
    return 2 if use_flexible_groups(context) else C.HEADCOUNT_GROUP_SIZE


def active_group_size(context) -> int:
    group = getattr(context, "group", context)
    return len(group.get_players())


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    if subsession.round_number > 1:
        subsession.group_like_round(1)
        return

    players = subsession.get_players()
    if use_flexible_groups(subsession):
        subsession.set_group_matrix(
            balanced_group_matrix(
                players,
                target_group_size(subsession),
                min_group_size=minimum_group_size(subsession),
            )
        )
        return

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


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    effective_group_size = models.IntegerField()
    effective_multiplier = models.FloatField()


class Player(BasePlayer):
    contribution = models.CurrencyField(
        min=0, max=C.ENDOWMENT, label="How much will you contribute?"
    )


def is_unmatched(player: Player):
    return active_group_size(player) < minimum_group_size(player)


def effective_multiplier(group: Group) -> float:
    if not use_flexible_groups(group.session):
        return C.MULTIPLIER
    return C.MULTIPLIER * active_group_size(group) / target_group_size(group.session)


class Unmatched(Page):
    template_name = "global/Unmatched.html"

    @staticmethod
    def is_displayed(player: Player):
        return is_unmatched(player) and player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(required_size=minimum_group_size(player))

    @staticmethod
    def app_after_this_page(player: Player, upcoming_apps):
        return next_app(upcoming_apps)


def set_payoffs(group: Group):
    players = group.get_players()
    contributions = [player.contribution for player in players]
    group.effective_group_size = active_group_size(group)
    group.effective_multiplier = effective_multiplier(group)
    group.total_contribution = sum(contributions)
    group.individual_share = (
        group.total_contribution * group.effective_multiplier / group.effective_group_size
    )
    for player in players:
        player.payoff = C.ENDOWMENT - player.contribution + group.individual_share


def intro_vars(player: Player):
    actual_size = active_group_size(player)
    current_multiplier = effective_multiplier(player.group)
    return dict(
        actual_group_size=actual_size,
        target_group_size=target_group_size(player),
        use_flexible_groups=use_flexible_groups(player),
        effective_multiplier=current_multiplier,
        marginal_per_capita_return=round(current_multiplier / actual_size, 2),
    )


class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return intro_vars(player)


class Contribute(Page):
    form_model = "player"
    form_fields = ["contribution"]

    @staticmethod
    def vars_for_template(player: Player):
        return intro_vars(player)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        total = sum(round_player.payoff for round_player in player.in_all_rounds())
        return dict(
            total_payoff=total,
            actual_group_size=player.group.effective_group_size,
            effective_multiplier=player.group.effective_multiplier,
            use_flexible_groups=use_flexible_groups(player),
        )


page_sequence = [Unmatched, Introduction, Contribute, ResultsWaitPage, Results]
