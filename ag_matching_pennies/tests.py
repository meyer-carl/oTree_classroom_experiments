from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number > active_rounds(self.player):
            return

        if self.player.active_this_round is False:
            yield SitOutRound
            expect(self.player.payoff, cu(0))
            return

        yield Choice, dict(penny_side='Heads')
        if role_name(self.player) == C.MATCHER_ROLE:
            expect(self.player.is_winner, True)
        else:
            expect(self.player.is_winner, False)

        if self.player.round_number == active_rounds(self.player):
            total_payoffs = sum(p.payoff for p in self.player.in_all_rounds() if p.round_number <= active_rounds(self.player))
            if pair_cycle_enabled(self.player):
                expect(total_payoffs >= cu(0), True)
            else:
                total_group_payoffs = 0
                for player in self.group.get_players():
                    total_group_payoffs += sum(p.payoff for p in player.in_all_rounds())
                expect(total_group_payoffs, C.STAKES)
