# MachiKoroAI

## I recently played Machi Koro for the first time with some friends.  Given the relative simplicity, it seemed like the perfect game on which to train a deep neural net, so that's what I'm working on!  For now, I've implenented the base game in python (with an ability to play manually or using randomized AI) and run some basic simulations using the randomized AI. 

## Files

StaticCardDatabase.py - generates a serialized python object containing all the base game information on cards and players (through the csv files in csv_game_db_files).  This ultimately feeds into the game manager.  

MachiKoro.py - the main game module.  MachiKoro is the main class.  The init method takes the number of players.  There's also a reloadDB method that forces the regeneration fo the pkl file from the underlying CSV files. 

MachiKoroAIAnalysis.ipynb - Contains simulations and analysis.  For now, it contains some results from running 50000 simulated games with three AI players that behave randomly.  