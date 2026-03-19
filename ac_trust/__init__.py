from otree.api import *
import random

doc = """
Trust Game: This is a standard 2-player trust game where the amount sent by player 1 gets
tripled. The trust game was first proposed by
<a href="http://econweb.ucsd.edu/~jandreon/Econ264/papers/Berg%20et%20al%20GEB%201995.pdf" target="_blank">
    Berg, Dickhaut, and McCabe (1995)
</a>.
The code is slightly modified from the original oTree code, found
<a href="https://github.com/oTree-org/oTree/tree/lite" target="_blank">
    here
</a>.
"""


class C(BaseConstants):
    # Constants shared across all players and rounds
    NAME_IN_URL = 'trust'  # URL name for this app
    PLAYERS_PER_GROUP = 2  # Number of players per group
    NUM_ROUNDS = 1  # Number of rounds in the game
    ENDOWMENT = cu(100)  # Initial amount allocated to P1
    MULTIPLIER = 3  # Multiplier applied to the amount sent by P1
    USE_STRATEGY_METHOD = False  # Set to True or use session config 'use_strategy_method'
    SEND_INCREMENT = 10  # Increment used for strategy method table
    STRATEGY_SEND_AMOUNTS = list(range(0, int(ENDOWMENT) + 1, SEND_INCREMENT))


class Subsession(BaseSubsession):
    # Subsession class for managing rounds
    pass


class Group(BaseGroup):
    # Group class for managing interactions between players
    sent_amount = models.CurrencyField(
        min=cu(0),  # Minimum amount P1 can send
        max=C.ENDOWMENT,  # Maximum amount P1 can send
        doc="""Amount sent by P1""",  # Documentation for this field
        label="How much do you want to send to the other player?",  # Label for the input field
    )
    sent_back_amount = models.CurrencyField(
        min=cu(0),  # Minimum amount P2 can send back
        doc="""Amount sent back by P2""",  # Documentation for this field
        label="How much do you want to send back to the other player?"  # Label for the input field
    )


class Player(BasePlayer):
    # Player class for managing individual player data
    pass


for amount in C.STRATEGY_SEND_AMOUNTS:
    max_back = amount * C.MULTIPLIER
    setattr(
        Player,
        f'strategy_send_back_{amount}',
        models.CurrencyField(
            min=cu(0),
            max=cu(max_back),
            label=f"If P1 sends {cu(amount)} (tripled to {cu(max_back)}), how much do you send back?",
            blank=True,
        ),
    )


def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        session = subsession.session
        has_unmatched = any(
            len(g.get_players()) < C.PLAYERS_PER_GROUP for g in subsession.get_groups()
        )
        session.vars['trust_force_strategy'] = has_unmatched


def is_unmatched(player: Player):
    return len(player.group.get_players()) < C.PLAYERS_PER_GROUP


def use_strategy_method(player: Player):
    session = player.session
    return session.config.get('use_strategy_method', C.USE_STRATEGY_METHOD) or session.vars.get(
        'trust_force_strategy', False
    )


def strategy_fields():
    return [f'strategy_send_back_{amount}' for amount in C.STRATEGY_SEND_AMOUNTS]


def random_second_mover(player: Player):
    candidates = [
        p for p in player.subsession.get_players() if p.id_in_group == 2 and p != player
    ]
    return random.choice(candidates) if candidates else None


# FUNCTIONS
def sent_back_amount_max(group: Group):
    # Function to check that the amount P2 wants to send back doesn't exceed
    # the maximum amount P2 can send back
    return group.sent_amount * C.MULTIPLIER


def set_payoffs(group: Group):
    # Function to calculate payoffs for both players
    players = group.get_players()
    if len(players) < C.PLAYERS_PER_GROUP:
        lone_player = players[0]
        p2 = random_second_mover(lone_player)
        if p2 and use_strategy_method(p2):
            field = f'strategy_send_back_{int(group.sent_amount)}'
            group.sent_back_amount = getattr(p2, field, cu(0)) or cu(0)
        elif p2:
            group.sent_back_amount = p2.group.sent_back_amount or cu(0)
        else:
            group.sent_back_amount = cu(0)

        lone_player.payoff = C.ENDOWMENT - group.sent_amount + group.sent_back_amount
        return

    p1 = group.get_player_by_id(1)  # Get Player 1
    p2 = group.get_player_by_id(2)  # Get Player 2
    if use_strategy_method(p2):
        field = f'strategy_send_back_{int(group.sent_amount)}'
        group.sent_back_amount = getattr(p2, field)
    p1.payoff = C.ENDOWMENT - group.sent_amount + group.sent_back_amount  # Calculate P1's payoff
    p2.payoff = group.sent_amount * C.MULTIPLIER - group.sent_back_amount  # Calculate P2's payoff


# PAGES
class Introduction(Page):
    # Introduction page for explaining the game to players
    pass


class Send(Page):
    """This page is only for P1
    P1 sends amount (all, some, or none) to P2
    This amount is tripled by experimenter,
    i.e if sent amount by P1 is 5, amount received by P2 is 15"""

    form_model = 'group'  # Model to store form data
    form_fields = ['sent_amount']  # Fields to display on the form

    @staticmethod
    def is_displayed(player: Player):
        # Display this page only for Player 1
        return player.id_in_group == 1

    @staticmethod
    def error_message(player: Player, values):
        if use_strategy_method(player):
            amount = int(values['sent_amount'])
            if amount % C.SEND_INCREMENT != 0:
                return f"Please enter a multiple of {C.SEND_INCREMENT}."


class SendBackWaitPage(WaitPage):
    # Wait page for P2 to wait until P1 sends the amount
    pass


class SendBack(Page):
    """This page is only for P2
    P2 sends back some amount (of the tripled amount received) to P1"""

    form_model = 'group'  # Model to store form data
    form_fields = ['sent_back_amount']  # Fields to display on the form

    @staticmethod
    def is_displayed(player: Player):
        # Display this page only for Player 2
        return player.id_in_group == 2 and not use_strategy_method(player)

    @staticmethod
    def vars_for_template(player: Player):
        # Variables to pass to the template
        group = player.group
        tripled_amount = group.sent_amount * C.MULTIPLIER  # Calculate tripled amount
        return dict(tripled_amount=tripled_amount)


class StrategySendBack(Page):
    form_model = 'player'
    form_fields = []

    @staticmethod
    def get_form_fields(player: Player):
        return strategy_fields()

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2 and use_strategy_method(player)

    @staticmethod
    def error_message(player: Player, values):
        missing = [name for name in strategy_fields() if values.get(name) is None]
        if missing:
            return "Please fill in a response for each possible amount."


class ResultsWaitPage(WaitPage):
    # Wait page for calculating payoffs after all players finish
    after_all_players_arrive = set_payoffs  # Call set_payoffs after all players arrive


class Results(Page):
    """This page displays the earnings of each player"""

    @staticmethod
    def vars_for_template(player: Player):
        # Variables to pass to the template
        group = player.group
        return dict(tripled_amount=group.sent_amount * C.MULTIPLIER)  # Calculate tripled amount


class StrategySyncWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def is_displayed(player: Player):
        return use_strategy_method(player)


# Sequence of pages in the app
page_sequence = [
    Introduction,  # Introduction page
    StrategySendBack,
    Send,  # Page for P1 to send amount
    SendBackWaitPage,  # Wait page for P2
    SendBack,  # Page for P2 to send back amount
    StrategySyncWaitPage,
    ResultsWaitPage,  # Wait page for calculating payoffs
    Results,  # Results page to display earnings
]
