from otree.api import Bot
import json
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.player.round_number == 1:
            yield Introduction

        if self.player.round_number == 3:
            yield Choice, dict(comp_choice='piece')

        tasks = json.loads(self.player.task_data)
        answers = {
            f'answer_{i}': task['a'] + task['b']
            for i, task in enumerate(tasks, start=1)
        }
        yield Task, answers
        yield Results
