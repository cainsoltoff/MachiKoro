from abc import ABCMeta, abstractmethod
import random

class PlayerController(metaclass=ABCMeta):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def get_player_choice(self, player_num, message, options, choice_type):
        pass

class HumanPlayerController(PlayerController):
    def get_player_choice(self, player_num, message, options, choice_type):
        if not options:
            return -1
        else:
            self.game.display_game()

            choice = int(input(message))

            while choice not in options and choice != -1:
                choice = int(input(message))

            return choice

class AIPlayerController(PlayerController):
    def get_player_choice(self, player_num, message, options, choice_type):
        if not options:
            return -1
        else:
            return random.choice(options)
