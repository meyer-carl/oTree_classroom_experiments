from os import environ


SESSION_CONFIGS = [
    dict(
        name='dictator',
        display_name="Dictator Game",
        app_sequence=['aa_dictator'],
        num_demo_participants=2,
    ),
    dict(
        name='ultimatum',
        display_name="Ultimatum Game",
        app_sequence=['ab_ultimatum'],
        num_demo_participants=2,
    ),
    dict(
        name='trust',
        display_name="Trust Game",
        app_sequence=['ac_trust'],
        num_demo_participants=2,
    ),
    dict(
        name='nash_demand',
        display_name="Nash Demand Game",
        app_sequence=['ad_nash_demand'],
        num_demo_participants=2,
    ),
    dict(
        name='guess_two_thirds',
        display_name="Guess 2/3 of the Average",
        app_sequence=['ae_guess_two_thirds'],
        num_demo_participants=4,
    ),
    dict(
        name='centipede',
        display_name="Centipede Game",
        app_sequence=['af_centipede'],
        num_demo_participants=2,
    ),
    dict(
        name='matching_pennies',
        display_name="Matching Pennies",
        app_sequence=['ag_matching_pennies'],
        num_demo_participants=2
    ),
    dict(
        name='coordination_game',
        display_name="Coordination Game",
        app_sequence=['ah_coordination'],
        num_demo_participants=2
    ),
    dict(
        name='prisoner_mult_rd',
        display_name="Prisoner's Dilemma, multiple rounds",
        app_sequence=['ai_prisoner_mult_rd'],
        num_demo_participants=2,
    ),
    dict(
        name='prisoner_one_rd',
        display_name="Prisoner's Dilemma, one round",
        app_sequence=['ai_prisoner_one_rd'],
        num_demo_participants=2,
    ),
    dict(
        name='public_goods',
        display_name="Public Goods Game",
        app_sequence=['aj_public_goods'],
        num_demo_participants=3,
    ),
    dict(
        name='market_supply_demand',
        display_name="Market: Supply and Demand",
        app_sequence=['ak_market_supply_demand'],
        num_demo_participants=8,
    ),
    dict(
        name='two_sided_auction',
        display_name="Two-Sided Auction",
        app_sequence=['al_two_sided_auction'],
        num_demo_participants=2,
    ),
    dict(
        name='english_auction',
        display_name="English Auction",
        app_sequence=['am_english_auction'],
        num_demo_participants=4,
    ),
    dict(
        name='dutch_auction',
        display_name="Dutch Auction",
        app_sequence=['an_dutch_auction'],
        num_demo_participants=4,
    ),
    dict(
        name='sealed_bid_first_price',
        display_name="Sealed-Bid First-Price Auction",
        app_sequence=['ao_sealed_bid_first_price'],
        num_demo_participants=4,
    ),
    dict(
        name='sealed_bid_second_price',
        display_name="Sealed-Bid Second-Price Auction",
        app_sequence=['ap_sealed_bid_second_price'],
        num_demo_participants=4,
    ),
    dict(
        name='ebay_auction',
        display_name="eBay-Style Auction",
        app_sequence=['aq_ebay_auction'],
        num_demo_participants=4,
    ),
    dict(
        name='risk_time_preferences',
        display_name="Risk and Time Preferences",
        app_sequence=['ar_risk_time_preferences'],
        num_demo_participants=1,
    ),
    dict(
        name='competitiveness',
        display_name="Competitiveness (Tournament Choice)",
        app_sequence=['as_competitiveness'],
        num_demo_participants=4,
    ),
    dict(
        name='bertrand',
        display_name="Bertrand Competition",
        app_sequence=['at_bertrand'],
        num_demo_participants=2,
    ),
    dict(
        name='cournot',
        display_name="Cournot Competition",
        app_sequence=['au_cournot'],
        num_demo_participants=2,
    ),
    dict(
        name='common_value_auction',
        display_name="Common Value Auction",
        app_sequence=['av_common_value_auction'],
        num_demo_participants=4,
    ),
    dict(
        name='traveler_dilemma',
        display_name="Traveler's Dilemma",
        app_sequence=['aw_traveler_dilemma'],
        num_demo_participants=2,
    ),
    dict(
        name='volunteer_dilemma',
        display_name="Volunteer's Dilemma",
        app_sequence=['ay_volunteer_dilemma'],
        num_demo_participants=3,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
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
Here are some oTree games.
"""


SECRET_KEY = '{{ secret_key }}'

INSTALLED_APPS = ['otree']
