from csv import reader
import pickle
import os.path

__CSV_FILE_PATH = "csv_game_db_files/"

"""
StaticCardDatabase.py

DATABASE
--------
[Structure: Dict]

static_card_database is a dictionary with the following keys which each represent a table:
"card_props": properties for each card_id where each card_id is a unique int 
"card_types": unique id/description for card_types (i.e. Primary Industry, Secondary Industry)
"card_icons": unique id/description for icons_for cards (i.e. Corn, Cow)
"roll_card_activations": the set of cards triggered by each roll from 1-12
"roll_cond": unique id/description for the roll condition for the card to activate (i.e. any player, your own roll)
"pay_from": unique id/description for where the card payment comes from (i.e. bank, player who rolled)
"secondary_ind_dep": for each secondary ind card, the pay multiplier and set of primary ind cards used to calculate pay 
"cards_for_coin_amt": for each total coin amount, all possible cards that can be purchased/unlocked
"max_card_cost": the maximum cost for any card

TABLES
------

card_props
----------
[Structure: list --> dict]

list index is card_id which is a unique int from 0 to n-1 representing each of the n cards

dict has keys ["card_name", "type_id" ,"icon_id","cost","roll_cond_id","pay_amt","pay_from_id"]

"card_name": card name (i.e Wheat Field, Ranch)
"type_id": int mapping to "card_types" table
"icon_id": int mapping to "card_icons" table
"cost": cost to purchase/activate card
"roll_cond_id": int mapping to roll_cond" table
"pay_amt": int payment amount for card (0 if card doesn't have any pmt associated)
"pay_from_id": maps to "pay_from" table

----------
card_types
----------
[Structure: list]

index is type_id

value is description of type (i.e. Primary Industry, Secondary Industry)

----------
card_icons
----------
[Structure: list]

index is icon_id

value is description of icon (i.e. Corn, Cow, Cup)

---------------------
roll_card_activations
---------------------
[Structure: dict -> list]

dict key is dice roll int

value is list of card_id's that are activated by that dice roll

----------
roll_cond
----------
[Structure: list]

index is roll_cond_id

value is description of roll_cond (i.e. "Any Player", "You", "Another Player", "n.a.")

----------
pay_from
----------
[Structure: list]

index is pay_from_id

value is description of pay_from (i.e. "Bank", "Player Who Rolled", "All Players", "Any One Player", "n.a."))

-------------------
secondary_ind_dep
-------------------
[Structure: dict -> dict]

dict key is card_id for a secondary industry

for value dict:
"multiplier" key is the pmt per primary industry item for that secondary industry card
"dependency_list" is the list of primary industries card_id's that are part of the secondary industry card pmt calc


-------------------
cards_for_coin_amt
-------------------
[Structure: dict -> list]

dict key is int coin_amt with keys going from 0 to the max cost of any card

value list is a list of card_id's that can be purchased with that coin amount (no checking on availablity which will be done during game time)

-------------------
max_card_cost
-------------------
int maximum cost of any card

-------------------
init_player_coin_amt
-------------------
int of starting coin amount for player


-----------------
init_player_cards
-----------------
[Structure: list]

index is card_id

value is amount of that card player starts with

---------------------------
init_player_landmark_status
---------------------------
[Structure: dict]

key is card_id

value is True/False depending on whether it has been purchased/activated

"""

def __generate_card_properties(filename="card_props.csv"):

    with open(__CSV_FILE_PATH+filename) as f:
        csv_file = reader(f)

        next(csv_file)
        card_properties = []

        for row in csv_file:
            card = {}
            card["card_name"] = row[1]
            card["type_id"] = int(row[2])
            card["icon_id"] = int(row[3])
            card["cost"] = int(row[4])
            card["roll_cond"] = int(row[5])
            card["pay_amt"] = int(row[6])
            card["pay_from"] = int(row[7])
            card["roll_activ"] = list(map(int, row[8].split(";")))
            card["init_card_supply"] = int(row[9])

            card_properties.append(card)

        return card_properties


def __generate_card_types(filename="card_types.csv"):

    with open(__CSV_FILE_PATH+filename) as f:
        csv_file = reader(f)
        next(csv_file)
        card_types = []

        for row in csv_file:
            card_types.append(row[1])

        return card_types


def __generate_card_icons(filename="card_icons.csv"):

    with open(__CSV_FILE_PATH+filename) as f:
        csv_file = reader(f)
        next(csv_file)
        card_icons = []

        for row in csv_file:
            card_icons.append(row[1])

        return card_icons


def __generate_roll_card_activations(table):

    from collections import defaultdict

    type_ids = set()
    roll_card_activations = {}

    for (card_id, card_props) in enumerate(table):
        type_ids.add(card_props["type_id"])

    for x in range(0, 13):
        roll_card_activations[x] = defaultdict(list)

    for (card_id, card_props) in enumerate(table):
        for roll in card_props["roll_activ"]:
            roll_card_activations[roll][card_props["type_id"]].append(card_id)

    return roll_card_activations

def __generate_player_rolling_condition(filename="roll_cond.csv"):

    with open(__CSV_FILE_PATH+filename) as f:
        csv_file = reader(f)
        next(csv_file)
        player_rolling_condition = []

        for row in csv_file:
            player_rolling_condition.append(row[1])

        return player_rolling_condition


def __generate_payoff_from(filename="pay_from.csv"):

    with open(__CSV_FILE_PATH+filename) as f:
        csv_file = reader(f)
        next(csv_file)

        payoff_from = []

        for row in csv_file:
            payoff_from.append(row[1])

        return payoff_from


def __generate_secondary_industry_dependencies(filename="secondary_ind_dep.csv"):

    with open(__CSV_FILE_PATH+filename) as f:
        csv_file = reader(f)
        next(csv_file)
        secondary_industry_dependencies = {}

        for row in csv_file:
            dependency_list = []
            key = int(row[0])
            multiplier = int(row[1])
            for r in row[2:]:

                if r != '':
                    dependency_list.append(int(r))

            d = {"multiplier":multiplier,"dependency_list":dependency_list}

            secondary_industry_dependencies[key] = d

        return secondary_industry_dependencies


def __generate_cards_for_coin_amount(table):

    from collections import defaultdict

    costDict = defaultdict(list)

    maxCost = 0

    for (card_id, card_info) in enumerate(table):
        if card_info["cost"] > maxCost:
            maxCost = card_info["cost"]
        costDict[card_info["cost"]].append(card_id)

    cards_for_coin = []

    for i in range(0, maxCost+1):
        card_list = []
        for cost_key in costDict.keys():
            if cost_key <= i:
                card_list.extend(costDict[cost_key])

        cards_for_coin.append(card_list)

    return cards_for_coin


def __generate_max_card_cost(table):

    max_card_cost = 0

    for (_, card_info) in enumerate(table):
        if card_info["cost"] > max_card_cost:
            max_card_cost = card_info["cost"]

    return max_card_cost

def __generate_init_player_cards(filename="init_player_cards.csv"):

    with open(__CSV_FILE_PATH+filename) as f:
        csv_file = reader(f)
        next(csv_file)

        init_player_cards = []

        for row in csv_file:
            init_player_cards.append(int(row[1]))

        return init_player_cards

def __generate_init_player_landmark_status(filename="init_player_landmark_status.csv"):

    with open(__CSV_FILE_PATH+filename) as f:
        csv_file = reader(f)
        next(csv_file)

        init_player_landmark_status = {}

        for row in csv_file:
            key = int(row[0])
            init_player_landmark_status[key] = bool(int(row[1]))

        return init_player_landmark_status

def __generate_init_card_supply(table):
    init_card_supply = []

    for (card_id, card_info) in enumerate(table):
        init_card_supply.append(card_info["init_card_supply"])

    return init_card_supply

def __generate_static_game_database_file_from_csv(settingsFile="initial_values.csv"):
    load_pipeline = [("card_props", __generate_card_properties),
                ("card_types", __generate_card_types),
                ("card_icons", __generate_card_icons),
                ("roll_cond", __generate_player_rolling_condition),
                ("pay_from", __generate_payoff_from),
                ("secondary_ind_dep", __generate_secondary_industry_dependencies),
                ("init_player_cards", __generate_init_player_cards),
                ("init_player_landmark_status", __generate_init_player_landmark_status)]

    static_game_database = {}

    for step in load_pipeline:
        static_game_database[step[0]] = step[1]()


    calc_pipeline = [("roll_card_activations", __generate_roll_card_activations, "card_props"),
                     ("cards_for_coin_amt", __generate_cards_for_coin_amount, "card_props"),
                     ("max_card_cost", __generate_max_card_cost, "card_props"),
                     ("init_card_supply", __generate_init_card_supply, "card_props")]

    for step in calc_pipeline:
        static_game_database[step[0]] = step[1](static_game_database[step[2]])

    with open(__CSV_FILE_PATH+settingsFile) as f:
        csv_file = reader(f)
        next(csv_file)

        for row in csv_file:
            static_game_database[row[0]] = int(row[1])


    with open("static_game_db.pkl", "wb")  as f:
        pickle.dump(static_game_database, f)


def load_static_game_database(forceReloadFromCSV=False, csvFilePath="csv_game_files/"):
    """
    'static_game_info.pkl' should contain all the static game information about cards and initial set up

    if 'static_game_info.pkl' doesn't exist or forceReloadFromCSV is True, it will regenerate the file
    from the csv tables

    uses default file location for CSV tables unless otherwise specified

    returns the loaded database

    """

    __CSV_FILE_PATH = csvFilePath

    if not os.path.isfile("static_game_db.pkl") or forceReloadFromCSV:
        __generate_static_game_database_file_from_csv()

    with open("static_game_db.pkl", "rb")  as f:
        static_card_database = pickle.load(f)

    return static_card_database
