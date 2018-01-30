import StaticCardDatabase

from PlayerControllers import AIPlayerController, HumanPlayerController
from copy import copy
import random

class NumberOfPlayerControllersDoNotMatchNumberOfPlayers(Exception):
    pass

game_db = StaticCardDatabase.load_static_game_database()

def reloadDB():
    """
    Force a reload of the database if you make changes to the unerlying csv files.
    """
    StaticCardDatabase.load_static_game_database(forceReloadFromCSV=True)

class MachiKoro():
    def __init__(self, num_players=3, print_actions=False):
        self.num_players = num_players
        self.player_turn = 0
        self.turn_num = 0
        self.print_actions = print_actions
        self.landmark_cards = {card_id for (card_id, card_props) in enumerate(game_db['card_props']) if card_props['type_id'] == 4}
        self.major_establishment_cards = {card_id for (card_id, card_props) in enumerate(game_db['card_props']) if card_props['type_id'] == 3}
        self.max_card_cost = game_db["max_card_cost"]
        self.bank = game_db["init_bank_amt"]
        self.card_supply = game_db["init_card_supply"][:]

        self.players = []
        self.player_controllers = []

        self.initialize_players()

    def add_player_controller(self, player_controller):
        self.player_controllers.append(player_controller)

        if len(self.player_controllers) > self.num_players:
            raise NumberOfPlayerControllersDoNotMatchNumberOfPlayers

    def display_game(self):
        print()
        print()
        print("GAME STATUS")

        print("Supply",end=":")
        for (cards, count) in enumerate(self.card_supply):
            if game_db['card_props'][cards]['type_id'] != 4:
                print(game_db['card_props'][cards]['card_name'], "[", count, "]", sep="", end=";")
        print("")
        for i in range(self.num_players):
            print("Player", i, end=":")
            print("Coins:", self.players[i]['coins'], end=";")

            for (cards, count) in enumerate(self.players[i]['player_cards']):
                if game_db['card_props'][cards]['type_id'] != 4 and count != 0:
                    print(game_db['card_props'][cards]['card_name'],"[",count,"]", sep="", end=";")

            for (cards, status) in self.players[i]['landmark_status'].items():
                if status != False:
                    print(game_db['card_props'][cards]['card_name'], sep="", end=";")

            print("")
        print("")

    def initialize_players(self):
        for i in range(self.num_players):
            p = {}
            p['coins'] = game_db["init_player_coin_amt"]
            p['player_cards'] = game_db["init_player_cards"][:]
            p['landmark_status'] = copy(game_db["init_player_landmark_status"])
            self.players.append(p)

    def reset(self):
            self.bank = game_db["init_bank_amt"]
            self.card_supply = game_db["init_card_supply"][:]
            self.player_turn = 0
            self.players = []
            self.turn_num = 0

    def check_game_over(self, player):
        return all(self.players[player]['landmark_status'].values())

    def advance_to_next_player(self):
        self.player_turn = (self.player_turn + 1) % self.num_players

    def train_station_constructed(self, player):
        return self.players[player]['landmark_status'][15]

    def shopping_mall_constructed(self, player):
        return self.players[player]['landmark_status'][16]

    def amusement_park_constructed(self, player):
        return self.players[player]['landmark_status'][17]

    def radio_tower_constructed(self, player):
        return self.players[player]['landmark_status'][18]

    def secondary_industry_depends_on_primary_industries(self, secondary_card_id):
        return game_db["card_props"][secondary_card_id]["pay_amt"] == 0

    def rolled_doubles(self, dice):
        if len(dice) == 1:
            return False
        else:
            return dice[0] == dice[1]

    def roll_dice(self):

        num_dice = 1

        if self.train_station_constructed(self.player_turn):
            num_dice = self.player_controllers[self.player_turn].get_player_choice(self.player_turn, "Roll 1 or 2 Dice?", [1, 2], "dice")

        if num_dice == 1:
            dice = random.randint(1, 6),
            roll_sum = sum(dice)
        else:
            dice = random.randint(1, 6), random.randint(1, 6)
            roll_sum = sum(dice)

        return dice, roll_sum

    def resolve_restaurants(self, roll_sum):

        players = list(range(self.num_players))
        player_order_to_check_restaurants = players[:self.player_turn][::-1] + players[self.player_turn+1:][::-1] # counterclockwise

        restaurant_cards_activated_for_roll = game_db['roll_card_activations'][roll_sum][2]

        for i in player_order_to_check_restaurants:
            for card_id in restaurant_cards_activated_for_roll:
                number_of_cards_owned = self.players[i]['player_cards'][card_id]

                shopping_mall_restaurant_boost = 1 if self.shopping_mall_constructed(i) else 0

                amount_to_transfer = min(
                    self.players[self.player_turn]['coins'],
                    (game_db["card_props"][card_id]["pay_amt"] + shopping_mall_restaurant_boost) * int(number_of_cards_owned))

                self.players[i]['coins'] += amount_to_transfer
                self.players[self.player_turn]['coins'] -= amount_to_transfer

    def resolve_primary_industries(self, roll_sum):

        primary_cards_activated_for_roll = game_db['roll_card_activations'][roll_sum][0]

        for i in range(self.num_players):
            for card_id in primary_cards_activated_for_roll:
                number_of_cards_owned = self.players[i]['player_cards'][card_id]
                card_payout = game_db["card_props"][card_id]["pay_amt"]
                self.players[i]['coins'] += number_of_cards_owned * card_payout

    def resolve_secondary_industries(self, roll_sum):

        secondary_cards_activated_for_roll = game_db['roll_card_activations'][roll_sum][1]

        for secondary_card_id in secondary_cards_activated_for_roll:
            number_of_secondary_card_owned = self.players[self.player_turn]['player_cards'][secondary_card_id]

            if game_db["card_props"][secondary_card_id]["icon_id"] == 3 and self.shopping_mall_constructed(self.player_turn):
                shopping_mall_secondary_boost = 1
            else:
                shopping_mall_secondary_boost = 0

            if self.secondary_industry_depends_on_primary_industries(secondary_card_id):
                primary_industries_for_secondary_industry = game_db["secondary_ind_dep"][secondary_card_id]["dependency_list"]
                pay_per_primary_industry = game_db["secondary_ind_dep"][secondary_card_id]["multiplier"]

                for primary_card_id in primary_industries_for_secondary_industry:
                    number_of_primary_card_owned = self.players[self.player_turn]['player_cards'][primary_card_id]
                    self.players[self.player_turn]['coins'] += (number_of_primary_card_owned * pay_per_primary_industry
                                                               + shopping_mall_secondary_boost) * number_of_secondary_card_owned
            else:
                secondary_card_payout = game_db["card_props"][number_of_secondary_card_owned]["pay_amt"]
                self.players[self.player_turn]['coins'] += (shopping_mall_secondary_boost + secondary_card_payout) * number_of_secondary_card_owned


    def resolve_major_establishments(self, roll_sum):

        major_establishment_cards_activated = game_db['roll_card_activations'][roll_sum][3]

        for card_id in major_establishment_cards_activated:
            if self.players[self.player_turn]['player_cards'][card_id] != 0:
                if card_id == 12:
                    for i in range(self.num_players):
                        if i != self.player_turn:
                            transfer_amount = min(self.players[i]['coins'], 2)
                            self.players[i]['coins'] -= transfer_amount
                            self.players[self.player_turn]['coins'] += transfer_amount
                elif card_id == 13:
                    players_to_choose_from = [i for i in range(self.num_players) if i != self.player_turn]

                    player = self.player_controllers[self.player_turn].get_player_choice(
                        self.player_turn, "Select player to take from", players_to_choose_from, "tv_station")

                    transfer_amount = min(self.players[player]['coins'], 5)
                    self.players[player]['coins'] -= transfer_amount
                    self.players[self.player_turn]['coins'] += transfer_amount
                elif card_id == 14:
                    players_to_choose_from = [i for i in range(self.num_players) if i != self.player_turn]

                    swappable_cards_for_players = {}
                    for player in range(self.num_players):
                        swappable_cards = []
                        for (card_id, amount_owned) in enumerate(self.players[player]['player_cards']):
                            type_id = game_db["card_props"][card_id]["type_id"]
                            if amount_owned != 0 and type_id not in (3, 4):
                                swappable_cards.append(card_id)

                            swappable_cards_for_players[player] = swappable_cards

                    player_to_swap_with = self.player_controllers[self.player_turn].get_player_choice(
                        self.player_turn, "Select player to swap card with", players_to_choose_from, "business_center_player")

                    cardToTake = self.player_controllers[self.player_turn].get_player_choice(self.player_turn, "Select card to take",
                                                        swappable_cards_for_players[player_to_swap_with], "business_center_take")

                    cardToGive = self.player_controllers[self.player_turn].get_player_choice(self.player_turn, "Select card to give",
                                                        swappable_cards_for_players[self.player_turn], "business_center_give")

                    self.players[player_to_swap_with]['player_cards'][cardToTake] -= 1
                    self.players[self.player_turn]['player_cards'][cardToTake] += 1

                    self.players[player_to_swap_with]['player_cards'][cardToGive] += 1
                    self.players[self.player_turn]['player_cards'][cardToGive] -= 1

    def resolve_roll(self, roll_sum):

        self.resolve_restaurants(roll_sum)
        self.resolve_primary_industries(roll_sum)
        self.resolve_secondary_industries(roll_sum)
        self.resolve_major_establishments(roll_sum)


    def make_purchase_decision(self):

        player_coin_total = self.players[self.player_turn]['coins']

        cards_affordable_with_player_coin_total = set(game_db['cards_for_coin_amt'][min(player_coin_total, self.max_card_cost)])

        major_establishments_already_owned = {card_id for card_id in self.major_establishment_cards
                                              if self.players[self.player_turn]['player_cards'][card_id] == 1}

        landmarks_already_built = {card_id for card_id in self.players[self.player_turn]['landmark_status']
                                   if self.players[self.player_turn]['landmark_status'][card_id] == True}

        cards_with_supply_left = {card_id for (card_id, supply) in enumerate(self.card_supply) if supply > 0}

        purchase_options = list((cards_affordable_with_player_coin_total & cards_with_supply_left)
                              - major_establishments_already_owned
                              - landmarks_already_built)

        if self.player_turn == 0: print(purchase_options)

        purchase_choice = self.player_controllers[self.player_turn].get_player_choice(
            self.player_turn, "Pick a card to purchase or -1 to skip:", purchase_options, "purchase")

        if purchase_choice != -1:
            if purchase_choice in self.landmark_cards:
                self.players[self.player_turn]['landmark_status'][purchase_choice] = True
                self.players[self.player_turn]['coins'] -= game_db["card_props"][purchase_choice]["cost"]
            else:
                self.players[self.player_turn]['player_cards'][purchase_choice] += 1
                self.card_supply[purchase_choice] -= 1
                self.players[self.player_turn]['coins'] -= game_db["card_props"][purchase_choice]["cost"]

    def execute_turn(self):
        self.turn_num += 1

        if self.print_actions: print("Turn ", self.turn_num, ",", " Player ", self.player_turn, sep="")

        # Roll The Dice
        dice, roll_sum = self.roll_dice()

        if self.print_actions: print("DICE ROLL:", dice)

        if self.radio_tower_constructed(self.player_turn):
            # print("Rolls", dice, "for a total of", rollTotal)

            reroll = self.player_controllers[self.player_turn].get_player_choice(self.player_turn,
                                                                                 "Roll again? 1 for Yes. 0 For No",
                                                                                 [0, 1], "radio_tower")

            if reroll == 1:
                dice, roll_sum = self.roll_dice()
                if self.print_actions: print("Rerolling dice")
                if self.print_actions: print("DICE ROLL:", dice)

        if self.amusement_park_constructed(self.player_turn) and self.rolled_doubles(dice):
            if self.print_actions: print("Doubles Rolled So Player", self.player_turn, "gets another turn!")
        else:
            self.advance_to_next_player()

        # print("Rolls", dice, "for a total of", rollTotal)

        # Resolve The Roll

        self.resolve_roll(roll_sum)
        self.make_purchase_decision()

    def run_game(self):

        if len(self.player_controllers) != self.num_players:
            raise NumberOfPlayerControllersDoNotMatchNumberOfPlayers

        while(True):
            self.execute_turn()

            if self.check_game_over(self.player_turn):
                break

            if self.print_actions: self.display_game()


if __name__ == "__main__":

    game = MachiKoro()

    game.add_player_controller(AIPlayerController(game))
    game.add_player_controller(AIPlayerController(game))
    game.add_player_controller(HumanPlayerController(game))

    game.run_game()