from otree.api import Bot, expect
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Introduction
        yield Decision, dict(volunteer=True)
        yield Results
        expect(self.player.group.effective_group_size, len(self.player.group.get_players()))
        expect(self.player.payoff, self.player.group.success_benefit - self.player.group.volunteer_cost)
