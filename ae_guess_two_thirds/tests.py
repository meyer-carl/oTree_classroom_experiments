from otree.api import Bot, SubmissionMustFail, expect

from . import C, Guess, Introduction, Results


class PlayerBot(Bot):
    def play_round(self):
        whole_class_mode = self.session.config.get("guess_two_thirds_group_mode") == "whole_class"

        if self.round_number == 1:
            yield Introduction
            if self.player.id_in_subsession == 1:
                for invalid_guess in (-1, 101):
                    yield SubmissionMustFail(Guess, dict(guess=invalid_guess))

        if whole_class_mode:
            guess = 30 if self.round_number == 1 else (9 if self.player.id_in_subsession == 1 else 10)
        else:
            if self.round_number == 1:
                guess = 9 if self.player.id_in_group == 1 else 10
            else:
                guess = 9

        yield Guess, dict(guess=guess)
        yield Results

        if whole_class_mode and self.round_number == 1:
            expect(self.player.payoff, C.JACKPOT / self.group.num_winners)
            assert len(self.player.group.get_players()) == self.session.num_participants
        elif whole_class_mode:
            if self.player.id_in_subsession == 1:
                expect(self.player.is_winner, True)
                expect(self.player.payoff, C.JACKPOT)
            else:
                expect(self.player.payoff, 0)
        elif self.round_number == 1:
            if self.player.id_in_group == 1:
                expect(self.player.payoff, C.JACKPOT)
            else:
                expect(self.player.payoff, 0)
        else:
            expect(self.player.payoff, C.JACKPOT / 2)
