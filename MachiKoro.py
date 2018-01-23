import StaticCardDatabase

from copy import copy
import random

game_db = StaticCardDatabase.load_static_game_database()

class MachiKoro():
    def __init__(self, numPlayers=3, ai=True):
        self.numPlayers = numPlayers
        self.maxCardCost = game_db["max_card_cost"]
        self.bank = game_db["init_bank_amt"]
        self.card_supply = game_db["init_card_supply"][:]
        self.playerTurn = 0
        self.ai = ai
        self.turn_num = 0

        self.players = {}

        for i in range(self.numPlayers):
            p = {}
            p['coins'] = game_db["init_player_coin_amt"]
            p['player_cards'] = game_db["init_player_cards"][:]
            p['landmark_status'] = copy(game_db["init_player_landmark_status"])
            self.players[i] = p

    def patienceFunction(self, player):
       return (1 - self.players[player]['coins']/self.maxCardCost)

    def reset(self):
            self.bank = game_db["init_bank_amt"]
            self.card_supply = game_db["init_card_supply"][:]
            self.playerTurn = 0
            self.players = {}
            self.turn_num = 0

            for i in range(self.numPlayers):
                p = {}
                p['coins'] = game_db["init_player_coin_amt"]
                p['player_cards'] = game_db["init_player_cards"][:]
                p['landmark_status'] = copy(game_db["init_player_landmark_status"])
                self.players[i] = p

    def checkGameOver(self, player):
        return all(self.players[player]['landmark_status'].values())

    def nextPlayer(self):
        self.playerTurn = (self.playerTurn + 1) % self.numPlayers

    def trainStationActivated(self, player):
        return self.players[player]['landmark_status'][15]

    def shoppingMallActivated(self, player):
        return self.players[player]['landmark_status'][16]

    def amusementParkActivated(self, player):
        return self.players[player]['landmark_status'][17]

    def radioTowerActivated(self, player):
        return self.players[player]['landmark_status'][18]

    def rolledDoubles(self, dice):
        if type(dice) == int:
            return False
        else:
            return dice[0] == dice[1]

    def rollDice(self):

        if self.trainStationActivated(self.playerTurn):
            if self.ai:
                numDice = random.randint(1,2)
            else:
                numDice = int(input("Roll 1 or 2 Dice?"))
        else:
            numDice = 1

        if numDice == 1:
            dice = random.randint(1, 6)
            rollTotal = dice
        else:
            dice = random.randint(1, 6), random.randint(1, 6)
            rollTotal = sum(dice)

        # print("Rolled", dice, "for a total of", rollTotal)
        return dice, rollTotal

    def resolveRestaurants(self, rollTotal):
        checkOrder = list(range(self.numPlayers))
        checkOrder = checkOrder[:self.playerTurn][::-1] + checkOrder[self.playerTurn+1:][::-1]

        rest_ids = game_db['roll_card_activations'][rollTotal][2]

        for i in checkOrder:
            for card_id in rest_ids:
                card_id_count = self.players[i]['player_cards'][card_id]
                shoppingMallIncrement = 1 if self.shoppingMallActivated(i) else 0
                transferAmount = min(self.players[self.playerTurn]['coins'], (game_db["card_props"][card_id]["pay_amt"] + shoppingMallIncrement) * int(card_id_count))

                self.players[i]['coins'] = self.players[i]['coins'] + transferAmount
                self.players[self.playerTurn]['coins'] = self.players[self.playerTurn]['coins'] - transferAmount

    def resolvePrimaryAndSecondaryIndustries(self, rollTotal):

        primary_ids = game_db['roll_card_activations'][rollTotal][0]
        secondary_ids = game_db['roll_card_activations'][rollTotal][1]

        #primary_industries

        for i in range(self.numPlayers):
            for card_id in primary_ids:
                card_id_count = self.players[i]['player_cards'][card_id]
                self.players[i]['coins'] = self.players[i]['coins'] + card_id_count * game_db["card_props"][card_id]["pay_amt"]

        # secondary_industries
        for card_id in secondary_ids:
            sec_card_id_count = self.players[self.playerTurn]['player_cards'][card_id]

            if game_db["card_props"][card_id]["pay_amt"] == 0:
                prim_dep = game_db["secondary_ind_dep"][card_id]["dependency_list"]
                multiplier = game_db["secondary_ind_dep"][card_id]["multiplier"]
                prim = self.players[self.playerTurn]['player_cards'][card_id]

                for prim in prim_dep:
                    prim_card_id_count = self.players[self.playerTurn]['player_cards'][prim]
                    self.players[self.playerTurn]['coins'] = (self.players[self.playerTurn]['coins'] +
                                                              prim_card_id_count * multiplier)
            else:
                shoppingMallIncrement = 1 if self.shoppingMallActivated(i) else 0
                if game_db["card_props"][sec_card_id_count]["icon_id"] == 3:
                    self.players[self.playerTurn]['coins'] = (self.players[self.playerTurn]['coins']
                                                              + sec_card_id_count * (shoppingMallIncrement + game_db["card_props"][sec_card_id_count]["pay_amt"]))
                else:
                    self.players[self.playerTurn]['coins'] = (self.players[self.playerTurn]['coins']
                                                              + sec_card_id_count * game_db["card_props"][sec_card_id_count]["pay_amt"])

    def resolveMajorEstablishments(self, rollTotal):

        cards = game_db['roll_card_activations'][rollTotal][3]

        for card_id in cards:
            if self.players[self.playerTurn]['player_cards'][card_id] == 0:
                continue
            else:
                if card_id == 12:
                    for i in range(self.numPlayers):
                        if i == self.playerTurn:
                            continue
                        else:
                            transferAmount = min(self.players[i]['coins'], 2)
                            self.players[i]['coins'] = self.players[i]['coins'] - transferAmount
                            self.players[self.playerTurn]['coins'] = self.players[self.playerTurn]['coins'] + transferAmount
                if card_id == 13:
                    options = set(range(self.numPlayers)) - set([self.playerTurn])

                    if self.ai:
                        player = random.sample(options, 1)[0]
                    else:
                        player = int(input("Select a player " + str(options) + " to take from:"))

                        while player not in options:
                            player = int(input("Select a player " + str(options) + " to take from:"))

                    transferAmount = min(self.players[player]['coins'], 5)
                    self.players[player]['coins'] = self.players[player]['coins'] - transferAmount
                    self.players[self.playerTurn]['coins'] = self.players[self.playerTurn]['coins'] + transferAmount

                if card_id == 14:
                    options = set(range(self.numPlayers)) - set([self.playerTurn])


                    playerOptions = {}
                    for player in range(self.numPlayers):
                        playerCardOptions = {}
                        for (card_id, card_count) in enumerate(self.players[player]['player_cards']):
                            type_id = game_db["card_props"][card_id]["type_id"]
                            if card_count != 0 and type_id not in (3, 4):
                                playerCardOptions[card_id] = card_count

                        playerOptions[player] = playerCardOptions

                    if self.ai:
                        player = random.sample(options, 1)[0]
                        cardToTake = random.choice(list(playerOptions[player].keys()))
                        cardToGive = random.choice(list(playerOptions[self.playerTurn].keys()))
                    else:
                        while player not in options:
                            player = int(input("Select a player " + str(options) + " to swap non-major card with:"))

                        cardToTake = int(input("Select a card " + str(set(playerOptions[player].keys())) + " to take:"))

                        while cardToTake not in playerOptions[player]:
                            cardToTake = int(input("Select a card " + str(set(playerOptions[player].keys())) + " to take:"))

                        cardToGive = int(input("Select a card " + str(set(playerOptions[self.playerTurn].keys())) + " to giverr:"))

                        while cardToGive not in playerOptions[self.playerTurn]:
                           cardToGive = int(input("Select a card " + str(set(playerOptions[self.playerTurn].keys())) + " to giverr:"))


                    self.players[player]['player_cards'][cardToTake] -= 1
                    self.players[self.playerTurn]['player_cards'][cardToTake] += 1

                    self.players[player]['player_cards'][cardToGive] += 1
                    self.players[self.playerTurn]['player_cards'][cardToGive] -= 1

    def resolveRoll(self, rollTotal):

        self.resolveRestaurants(rollTotal)
        self.resolvePrimaryAndSecondaryIndustries(rollTotal)
        self.resolveMajorEstablishments(rollTotal)


    def makePurchaseDecision(self):
        coinTotal = self.players[self.playerTurn]['coins']

        possiblePurchasesWithCoins = set(game_db['cards_for_coin_amt'][min(coinTotal, self.maxCardCost)])

        majorEstablishments = {card_id for (card_id, card_props) in enumerate(game_db['card_props']) if card_props['type_id'] == 3}
        landmarks = {card_id for (card_id, card_props) in enumerate(game_db['card_props']) if card_props['type_id'] == 4}

        playerMajorEstablishmentsNoCapacityToBuy = {card_id for card_id in majorEstablishments if self.players[self.playerTurn]['player_cards'][card_id] == 1}

        playerLandmarksNoCapacityToBuy = {card_id for card_id in self.players[self.playerTurn]['landmark_status'] if self.players[self.playerTurn]['landmark_status'][card_id] == True}
        currentSupply = {card_id for (card_id,supply) in enumerate(self.card_supply) if supply > 0}

        possiblePurchases = possiblePurchasesWithCoins.intersection(currentSupply) - (playerMajorEstablishmentsNoCapacityToBuy) - playerLandmarksNoCapacityToBuy

        if self.ai:
            if random.random() < self.patienceFunction(self.playerTurn) or len(possiblePurchases) == 0:
                purchase = -1
            else:
                purchase = random.sample(possiblePurchases, 1)[0]
        else:
            purchase = int(input("Pick a card to purchase " + str(possiblePurchases) + " or -1 to skip: "))

        if purchase == -1:
            return
        elif purchase in landmarks:
            self.players[self.playerTurn]['landmark_status'][purchase] = True
            self.players[self.playerTurn]['coins'] -= game_db["card_props"][purchase]["cost"]
        else:
            self.players[self.playerTurn]['player_cards'][purchase] += 1
            self.card_supply[purchase] -= 1
            self.players[self.playerTurn]['coins'] -= game_db["card_props"][purchase]["cost"]


    def turn(self):

        while(True):
            self.turn_num += 1
            # print("Turn", self.turn_num)
            #
            # print("Player ", self.playerTurn,"'s Turn", sep="")

            # Roll The Dice
            dice, rollTotal = self.rollDice()

            if self.radioTowerActivated(self.playerTurn):
                # print("Rolls", dice, "for a total of", rollTotal)

                if self.ai:
                    reroll = random.choice(["Y","N"])
                else:
                    reroll = input("Roll again? Y or N")

                if str.lower(reroll) == 'y':
                    dice, rollTotal = self.rollDice()

            # print("Rolls", dice, "for a total of", rollTotal)

            # Resolve The Roll

            self.resolveRoll(rollTotal)
            self.makePurchaseDecision()

            if self.checkGameOver(self.playerTurn):
                break

            # Advance To Next Player

            # for i in range(3):
            #
            #     print("Player", i)
            #     print("---------")
            #     print("Bank:", game.players[i]['coins'])
            #     print("Cards:", game.players[i]["player_cards"])
            # print()

            if self.amusementParkActivated(self.playerTurn) and self.rolledDoubles(dice):
                continue
            else:
                self.nextPlayer()

        # print(self.playerTurn, "Wins!")
        # print("Game Over!")


if __name__ == "__main__":
    pass


