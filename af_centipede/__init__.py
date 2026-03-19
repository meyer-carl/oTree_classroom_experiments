from otree.api import *
import random

doc = """
Centipede Game:
Players alternate deciding whether to take a larger share of a growing pot or pass it on.
If no one takes by the final node, the pot is split equally.
"""

class C(BaseConstants):
    NAME_IN_URL        = 'centipede'
    PLAYERS_PER_GROUP  = 2
    NUM_ROUNDS         = 6        # e.g. 6 decision nodes
    INITIAL_POT        = cu(100)  # starting pot
    POT_INCREMENT      = cu(50)   # added each pass
    SHARE_TAKER        = 0.6      # fraction for taker
    SHARE_OTHER        = 0.4      # fraction for other
    PCT_TAKER        = SHARE_TAKER * 100     # fraction for taker
    PCT_OTHER        = SHARE_OTHER * 100     # fraction for other
    USE_STRATEGY_METHOD = False  # Set to True or use session config 'use_strategy_method'

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    taken      = models.BooleanField(initial=False)
    taker      = models.IntegerField(null=True)  # 1 or 2
    take_round = models.IntegerField(null=True)

    # at each node: True=Take, False=Pass
    take = models.BooleanField(
        choices=[
            [True,  'Stop'],
            [False, 'Pass to your opponent'],
        ],
        widget=widgets.RadioSelect,
        label=""
    )

    def current_pot(self):
        return C.INITIAL_POT + (self.round_number - 1) * C.POT_INCREMENT
    
class Player(BasePlayer):
    pass


for r in range(1, C.NUM_ROUNDS + 1):
    pot = C.INITIAL_POT + (r - 1) * C.POT_INCREMENT
    setattr(
        Player,
        f'strategy_take_{r}',
        models.BooleanField(
            choices=[
                [True, 'Stop'],
                [False, 'Pass to your opponent'],
            ],
            widget=widgets.RadioSelect,
            label=f"Round {r}: pot = {pot}",
            blank=True,
        ),
    )


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        session = subsession.session
        has_unmatched = any(
            len(g.get_players()) < C.PLAYERS_PER_GROUP for g in subsession.get_groups()
        )
        session.vars['centipede_force_strategy'] = has_unmatched


def use_strategy_method(player: Player):
    session = player.session
    return session.config.get('use_strategy_method', C.USE_STRATEGY_METHOD) or session.vars.get(
        'centipede_force_strategy', False
    )


def strategy_fields_for_player(player: Player):
    fields = []
    for r in range(1, C.NUM_ROUNDS + 1):
        if (r % 2 == 1 and player.id_in_group == 1) or (
            r % 2 == 0 and player.id_in_group == 2
        ):
            fields.append(f'strategy_take_{r}')
    return fields


def strategy_choice(player: Player, round_number: int):
    return getattr(player, f'strategy_take_{round_number}')


def random_opponent(player: Player):
    target_id = 2 if player.id_in_group == 1 else 1
    candidates = [
        p for p in player.subsession.get_players() if p.id_in_group == target_id and p != player
    ]
    return random.choice(candidates) if candidates else None


def compute_strategy_outcome(p1: Player, p2: Player):
    for r in range(1, C.NUM_ROUNDS + 1):
        if r % 2 == 1:
            if strategy_choice(p1, r):
                return True, 1, r
        else:
            if strategy_choice(p2, r):
                return True, 2, r
    return False, None, None

def set_payoffs(group: Group):
    players = group.get_players()
    use_strategy = use_strategy_method(players[0])

    if use_strategy:
        if len(players) < C.PLAYERS_PER_GROUP:
            lone_player = players[0]
            opponent = random_opponent(lone_player)
            if opponent:
                taken, taker, take_round = compute_strategy_outcome(
                    lone_player if lone_player.id_in_group == 1 else opponent,
                    opponent if lone_player.id_in_group == 1 else lone_player,
                )
            else:
                taken, taker, take_round = False, None, None
            group.taken = taken
            group.taker = taker
            group.take_round = take_round
            r = take_round or C.NUM_ROUNDS
            pot = C.INITIAL_POT + (r - 1) * C.POT_INCREMENT
            if taken and taker == lone_player.id_in_group:
                lone_player.payoff = pot * C.SHARE_TAKER
            elif taken:
                lone_player.payoff = pot * C.SHARE_OTHER
            else:
                lone_player.payoff = pot / 2
            return

        p1 = group.get_player_by_id(1)
        p2 = group.get_player_by_id(2)
        taken, taker, take_round = compute_strategy_outcome(p1, p2)
        group.taken = taken
        group.taker = taker
        group.take_round = take_round

    # determine which round ultimately ended the game
    take_round = group.field_maybe_none('take_round')
    r = take_round or C.NUM_ROUNDS
    pot = C.INITIAL_POT + (r - 1) * C.POT_INCREMENT

    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)

    if group.taken:
        if group.taker == 1:
            p1.payoff = pot * C.SHARE_TAKER
            p2.payoff = pot * C.SHARE_OTHER
        else:
            p2.payoff = pot * C.SHARE_TAKER
            p1.payoff = pot * C.SHARE_OTHER
    else:
        # no one took by final node → split equally
        p1.payoff = pot / 2
        p2.payoff = pot / 2

# PAGES
class Introduction(Page):
    """Show once in round 1."""
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Decision(Page):
    form_model  = 'group'
    form_fields = ['take']

    @staticmethod
    def is_displayed(player: Player):
        if use_strategy_method(player):
            return False
        g = player.group
        # show only if game still going and it's your turn
        if g.taken:
            return False
        # odd rounds → P1; even → P2
        return (player.id_in_group == 1 and player.round_number % 2 == 1) or \
               (player.id_in_group == 2 and player.round_number % 2 == 0)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            pot = player.group.current_pot(),
        )

    def before_next_page(player: Player, timeout_happened):
        g = player.group
        if g.take:
            g.taken = True
            g.taker = player.id_in_group
            g.take_round = player.round_number


class StrategyDecision(Page):
    form_model = 'player'
    form_fields = []

    @staticmethod
    def get_form_fields(player: Player):
        return strategy_fields_for_player(player)

    @staticmethod
    def is_displayed(player: Player):
        return use_strategy_method(player) and player.round_number == 1


class DecisionWaitPage(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        if use_strategy_method(player):
            return False
        return not player.group.taken and player.round_number < C.NUM_ROUNDS


class ResultsWaitPage(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        g = player.group
        if use_strategy_method(player):
            return player.round_number == 1
        take_round = g.field_maybe_none('take_round')
        return g.taken and player.round_number == take_round or \
               not g.taken and player.round_number == C.NUM_ROUNDS

    after_all_players_arrive = set_payoffs

class StrategySyncWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player):
        return use_strategy_method(player) and player.round_number == 1

class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        g = player.group
        # show in the round somebody took, or in final round if nobody did
        if use_strategy_method(player):
            return player.round_number == 1
        take_round = g.field_maybe_none('take_round')
        return (g.taken and player.round_number == take_round) or \
               (not g.taken and player.round_number == C.NUM_ROUNDS)

    @staticmethod
    def vars_for_template(player: Player):
        g = player.group
        take_round = g.field_maybe_none('take_round')
        r = take_round or C.NUM_ROUNDS
        pot = C.INITIAL_POT + (r - 1) * C.POT_INCREMENT
        taker = g.field_maybe_none('taker')
        return dict(
            final_round = r,
            final_pot   = pot,
            taker       = taker,
            share_taker = C.SHARE_TAKER,
            share_other = C.SHARE_OTHER,
        )

page_sequence = [
    Introduction,
    StrategyDecision,
    Decision,
    DecisionWaitPage,
    StrategySyncWaitPage,
    ResultsWaitPage,
    Results,
]
