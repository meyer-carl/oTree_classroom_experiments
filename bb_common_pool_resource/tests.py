from otree.api import Bot, SubmissionMustFail, expect
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield Introduction

        yield SubmissionMustFail(Extract, dict(extraction=100))
        yield Extract, dict(extraction=2)

        yield Results
        expect(self.player.group.effective_group_size, len(self.player.group.get_players()))
        expect(self.player.group.effective_max_extraction >= 2, True)

        if self.round_number == C.NUM_ROUNDS:
            expect(sum(p.payoff for p in self.player.in_all_rounds()), cu(C.NUM_ROUNDS * 2))
