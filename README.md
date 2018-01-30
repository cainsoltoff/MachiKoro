# Machi Koro Game by Cain Soltoff

#### I recently played Machi Koro for the first time with some friends.  Given the relative simplicity, it seemed like the perfect game on which to train a deep neural net, so that's what I'm working on!  For now, I've implenented the base game in python (with an ability to play manually or using randomized AI) and run some basic simulations using the randomized AI. 


###<u> Python Machi Koro Game Implementation</u> 
### The MachiKoro package contains all the necessary code to play the game with humans, AI players, or a mix.

<b>MachiKoro.GameController</b> - This is the main sub-module.  In addition to the GameController class which will run the game,
                           there's also a top-level reloadDB method that forces the regeneration of the .pkl file from
                           the underlying CSV files.

<b>MachiKoro.PlayerController</b> - Contains an abstract base class Player Controller that can be sub-classed to create new player controllers.
                             Also includes two player controller types - a randomized AI and a human player (where the game queries the player for input).
                             Add PlayerControllers to the GameController via the latter's add_player_controller method.

<b>MachiKoro.StaticCardDatabase</b> - generates a serialized python object containing all the base game information on cards
                               and players (through the csv files in csv_game_db_files).


<u>Example: Three Player Game with One Human and Two AI's</u>

```
from MachiKoro.GameController import GameController
from MachiKoro.GameController import game_db
from MachiKoro.PlayerController import RandomAIPlayerController, HumanPlayerController


game = GameController(num_players=3, print_actions=False)

game.add_player_controller(HumanPlayerController(game))
game.add_player_controller(RandomAIPlayerController(game))
game.add_player_controller(RandomAIPlayerController(game))

game.run_game()

```
