from os import environ


def session_doc(summary, recommended_headcount, knobs=None, notes=None):
    parts = [summary, f"Recommended headcount: {recommended_headcount} participants."]
    if knobs:
        parts.append("Session config knobs: " + ", ".join(knobs) + ".")
    if notes:
        parts.append(notes)
    return " ".join(parts)


def config(name, display_name, app_sequence, num_demo_participants, summary, headcount, knobs=None, **extra):
    return dict(
        name=name,
        display_name=display_name,
        app_sequence=app_sequence,
        num_demo_participants=num_demo_participants,
        required_participants=headcount,
        doc=session_doc(summary, headcount, knobs=knobs, notes=extra.pop("notes", None)),
        **extra,
    )


def classroom_bundle(name, display_name, experiment_app, num_demo_participants, headcount, summary, knobs=None):
    return config(
        name=name,
        display_name=display_name,
        app_sequence=[experiment_app, "survey", "payment_info"],
        num_demo_participants=num_demo_participants,
        summary=summary,
        headcount=headcount,
        knobs=(knobs or []) + ["participant labels for payment redemption"],
        notes="Includes the reusable survey and payment_info follow-up apps.",
    )


SESSION_CONFIGS = [
    config(
        name="dictator",
        display_name="Dictator Game",
        app_sequence=["aa_dictator"],
        num_demo_participants=2,
        summary="One player chooses how much of an endowment to keep versus transfer.",
        headcount=2,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="endowment_effect",
        display_name="Endowment Effect (WTA/WTP)",
        app_sequence=["az_endowment_effect"],
        num_demo_participants=2,
        summary="Buyer/seller willingness-to-pay and willingness-to-accept comparison for classroom discussion of the endowment effect.",
        headcount=2,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="ultimatum",
        display_name="Ultimatum Game",
        app_sequence=["ab_ultimatum"],
        num_demo_participants=2,
        summary="Two-player bargaining with optional strategy-method fallback for odd headcounts.",
        headcount=2,
        knobs=["ultimatum_endowment", "use_strategy_method"],
    ),
    config(
        name="trust",
        display_name="Trust Game",
        app_sequence=["ac_trust"],
        num_demo_participants=2,
        summary="Trust game with optional strategy-method fallback and configurable multiplier.",
        headcount=2,
        knobs=["trust_endowment", "trust_multiplier", "trust_send_increment", "use_strategy_method"],
    ),
    config(
        name="nash_demand",
        display_name="Nash Demand Game",
        app_sequence=["ad_nash_demand"],
        num_demo_participants=2,
        summary="Two players request shares of a fixed surplus.",
        headcount=2,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="guess_two_thirds",
        display_name="Guess 2/3 of the Average",
        app_sequence=["ae_guess_two_thirds"],
        num_demo_participants=4,
        summary="Beauty-contest style guessing game with a jackpot for the closest player.",
        headcount=4,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="centipede",
        display_name="Centipede Game",
        app_sequence=["af_centipede"],
        num_demo_participants=2,
        summary="Alternating centipede game with forced strategy mode when headcount is odd.",
        headcount=2,
        knobs=["use_strategy_method"],
        notes="Pot growth parameters remain code-level because strategy labels are generated from constants.",
    ),
    config(
        name="matching_pennies",
        display_name="Matching Pennies",
        app_sequence=["ag_matching_pennies"],
        num_demo_participants=2,
        summary="Two-player zero-sum game with a random paying round.",
        headcount=2,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="coordination_game",
        display_name="Coordination Game",
        app_sequence=["ah_coordination"],
        num_demo_participants=2,
        summary="Two-player coordination game with a random paying round.",
        headcount=2,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="prisoner_mult_rd",
        display_name="Prisoner's Dilemma, multiple rounds",
        app_sequence=["ai_prisoner_mult_rd"],
        num_demo_participants=2,
        summary="Repeated prisoner's dilemma with fixed matching and optional single-round payment.",
        headcount=2,
        knobs=["pd_payoff_a", "pd_payoff_b", "pd_payoff_c", "pd_payoff_d", "pd_pay_single_round"],
    ),
    config(
        name="prisoner_one_rd",
        display_name="Prisoner's Dilemma, one round",
        app_sequence=["ai_prisoner_one_rd"],
        num_demo_participants=2,
        summary="One-shot prisoner's dilemma classroom demo.",
        headcount=2,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="public_goods",
        display_name="Public Goods Game",
        app_sequence=["aj_public_goods"],
        num_demo_participants=3,
        summary="Public goods game with anonymous small groups.",
        headcount=3,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="gift_exchange",
        display_name="Gift Exchange",
        app_sequence=["ba_gift_exchange"],
        num_demo_participants=2,
        summary="Employer-worker gift-exchange game connecting wages, reciprocity, and effort.",
        headcount=2,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="common_pool_resource",
        display_name="Common-Pool Resource",
        app_sequence=["bb_common_pool_resource"],
        num_demo_participants=4,
        summary="Repeated extraction game with resource regeneration for commons and externalities discussions.",
        headcount=4,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="asset_market_bubble",
        display_name="Asset Market Bubble",
        app_sequence=["bc_asset_market_bubble"],
        num_demo_participants=4,
        summary="Repeated asset market with declining fundamentals for classroom bubble and mispricing discussions.",
        headcount=4,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="market_supply_demand",
        display_name="Market: Supply and Demand",
        app_sequence=["ak_market_supply_demand"],
        num_demo_participants=8,
        summary="Single-call market with configurable buyer values, seller costs, and clearing-price rule.",
        headcount=8,
        knobs=["buyer_values", "seller_costs", "clearing_price_rule"],
    ),
    config(
        name="two_sided_auction",
        display_name="Two-Sided Auction",
        app_sequence=["al_two_sided_auction"],
        num_demo_participants=2,
        summary="Single buyer and seller submit a bid and ask.",
        headcount=2,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="english_auction",
        display_name="English Auction",
        app_sequence=["am_english_auction"],
        num_demo_participants=4,
        summary="Ascending-price auction with dropout decisions.",
        headcount=4,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="dutch_auction",
        display_name="Dutch Auction",
        app_sequence=["an_dutch_auction"],
        num_demo_participants=4,
        summary="Descending-price auction with a stop-price decision.",
        headcount=4,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="sealed_bid_first_price",
        display_name="Sealed-Bid First-Price Auction",
        app_sequence=["ao_sealed_bid_first_price"],
        num_demo_participants=4,
        summary="Independent private-values auction where the winner pays their own bid.",
        headcount=4,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="sealed_bid_second_price",
        display_name="Sealed-Bid Second-Price Auction",
        app_sequence=["ap_sealed_bid_second_price"],
        num_demo_participants=4,
        summary="Independent private-values auction where the winner pays the second-highest bid.",
        headcount=4,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="ebay_auction",
        display_name="eBay-Style Auction",
        app_sequence=["aq_ebay_auction"],
        num_demo_participants=4,
        summary="Proxy-bidding auction with an increment rule.",
        headcount=4,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="risk_time_preferences",
        display_name="Risk and Time Preferences",
        app_sequence=["ar_risk_time_preferences"],
        num_demo_participants=1,
        summary="Single-player multiple-price-list elicitation for risk, time, and loss-aversion preferences.",
        headcount=1,
        knobs=[
            "real_world_currency_per_point",
            "include_risk",
            "include_time",
            "include_loss",
            "include_ambiguity",
        ],
    ),
    config(
        name="risk_time_preferences_ambiguity",
        display_name="Risk, Time, and Ambiguity Preferences",
        app_sequence=["ar_risk_time_preferences"],
        num_demo_participants=1,
        summary="Single-player multiple-price-list elicitation for risk, time, loss-aversion, and ambiguity-aversion preferences.",
        headcount=1,
        knobs=["real_world_currency_per_point", "include_ambiguity"],
        include_ambiguity=True,
    ),
    config(
        name="competitiveness",
        display_name="Competitiveness (Tournament Choice)",
        app_sequence=["as_competitiveness"],
        num_demo_participants=4,
        summary="Piece-rate versus tournament-choice task with configurable timing and incentives.",
        headcount=4,
        knobs=[
            "competitiveness_num_tasks",
            "competitiveness_task_min",
            "competitiveness_task_max",
            "competitiveness_time_limit_seconds",
            "competitiveness_piece_rate",
            "competitiveness_tournament_rate",
            "competitiveness_tournament_winners",
        ],
        notes="competitiveness_num_tasks cannot exceed the compiled maximum in the app.",
    ),
    config(
        name="bertrand",
        display_name="Bertrand Competition",
        app_sequence=["at_bertrand"],
        num_demo_participants=2,
        summary="Two-firm price competition.",
        headcount=2,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="cournot",
        display_name="Cournot Competition",
        app_sequence=["au_cournot"],
        num_demo_participants=2,
        summary="Two-firm quantity competition.",
        headcount=2,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="common_value_auction",
        display_name="Common Value Auction",
        app_sequence=["av_common_value_auction"],
        num_demo_participants=4,
        summary="Common-value auction with noisy signals and winner's-curse discussion.",
        headcount=4,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="traveler_dilemma",
        display_name="Traveler's Dilemma",
        app_sequence=["aw_traveler_dilemma"],
        num_demo_participants=2,
        summary="Two-player traveler's dilemma with penalty and reward incentives.",
        headcount=2,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="volunteer_dilemma",
        display_name="Volunteer's Dilemma",
        app_sequence=["ay_volunteer_dilemma"],
        num_demo_participants=3,
        summary="Volunteer dilemma for discussing public provision and free-riding.",
        headcount=3,
        knobs=["real_world_currency_per_point"],
    ),
    config(
        name="survey_payment",
        display_name="Survey + Payment Information",
        app_sequence=["survey", "payment_info"],
        num_demo_participants=1,
        summary="Reusable demographic/CRT survey followed by a payment screen.",
        headcount=1,
        knobs=["participant labels for payment redemption"],
    ),
    classroom_bundle(
        name="trust_with_survey",
        display_name="Trust Game + Survey + Payment Info",
        experiment_app="ac_trust",
        num_demo_participants=2,
        headcount=2,
        summary="Instructor-ready classroom flow for trust followed by the reusable survey and payment instructions.",
        knobs=["trust_endowment", "trust_multiplier", "trust_send_increment", "use_strategy_method"],
    ),
    classroom_bundle(
        name="public_goods_with_survey",
        display_name="Public Goods + Survey + Payment Info",
        experiment_app="aj_public_goods",
        num_demo_participants=3,
        headcount=3,
        summary="Instructor-ready classroom flow for public goods with survey and payment follow-up.",
        knobs=["real_world_currency_per_point"],
    ),
    classroom_bundle(
        name="market_with_survey",
        display_name="Market + Survey + Payment Info",
        experiment_app="ak_market_supply_demand",
        num_demo_participants=8,
        headcount=8,
        summary="Instructor-ready classroom flow for the supply-and-demand market with follow-up survey and payment screen.",
        knobs=["buyer_values", "seller_costs", "clearing_price_rule"],
    ),
    classroom_bundle(
        name="competitiveness_with_survey",
        display_name="Competitiveness + Survey + Payment Info",
        experiment_app="as_competitiveness",
        num_demo_participants=4,
        headcount=4,
        summary="Instructor-ready classroom flow for the competitiveness experiment with survey and payment follow-up.",
        knobs=[
            "competitiveness_num_tasks",
            "competitiveness_task_min",
            "competitiveness_task_max",
            "competitiveness_time_limit_seconds",
            "competitiveness_piece_rate",
            "competitiveness_tournament_rate",
            "competitiveness_tournament_winners",
        ],
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    doc="Instructor-facing classroom experiment session.",
    use_strategy_method=False,
    trust_endowment=100,
    trust_multiplier=3,
    trust_send_increment=10,
    ultimatum_endowment=100,
    pd_payoff_a=300,
    pd_payoff_b=200,
    pd_payoff_c=100,
    pd_payoff_d=0,
    pd_pay_single_round=False,
    competitiveness_num_tasks=6,
    competitiveness_task_min=10,
    competitiveness_task_max=99,
    competitiveness_time_limit_seconds=0,
    competitiveness_piece_rate=10,
    competitiveness_tournament_rate=20,
    competitiveness_tournament_winners=1,
    buyer_values=[100, 90, 80, 70],
    seller_costs=[20, 30, 40, 50],
    clearing_price_rule="midpoint",
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
<p>Instructor-ready oTree classroom experiments.</p>
<p>
The standalone sessions keep their historical names stable. Additional bundled
flows append the reusable survey and payment info apps for classroom use.
</p>
"""


SECRET_KEY = '{{ secret_key }}'

INSTALLED_APPS = ['otree']
