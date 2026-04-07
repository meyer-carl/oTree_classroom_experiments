from otree.api import Bot, SubmissionMustFail, cu, expect

from . import C, Contribute, Introduction, Results


class PlayerBot(Bot):
    def play_round(self):
        if self.round_number == 1:
            yield Introduction
            yield SubmissionMustFail(Contribute, dict(contribution=cu(-1)))
            yield SubmissionMustFail(Contribute, dict(contribution=cu(101)))

        contribution = cu(10 if self.round_number == 1 else 20)
        yield Contribute, dict(contribution=contribution)
        yield Results

        actual_group_size = self.player.group.effective_group_size
        multiplier = C.MULTIPLIER
        if self.session.config.get("public_goods_flexible_grouping"):
            multiplier = (
                C.MULTIPLIER
                * actual_group_size
                / self.session.config.get("public_goods_target_group_size", C.HEADCOUNT_GROUP_SIZE)
            )
            assert actual_group_size in {2, 3}, f"actual_group_size={actual_group_size}"
        else:
            assert actual_group_size == C.HEADCOUNT_GROUP_SIZE

        expected_share = cu(contribution * multiplier)
        expect(self.player.group.individual_share, expected_share)
        expect(self.player.payoff, C.ENDOWMENT - contribution + self.group.individual_share)
