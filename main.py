# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# This file can be a nice home for your Battlesnake logic and helper functions.
#
# To get you started we've included code to prevent your Battlesnake from moving backwards.
# For more info see docs.battlesnake.com
import random
import typing
from MCTS import mcts_search, evaluate_state
from simulator import simulate_step
from snake_helpers import safe_moves
from vanilla_MCTS import vanilla_mcts_search
from heuristic import heuristic_search
from safe_random import safe_random_search
import os


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "The Rizzler",
        "color": "#696969",
        "head": "default",
        "tail": "default",
    }


# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:

    rollout = os.environ.get("SNAKE_BRAIN", "mcts")

    if rollout == "safe - random":
        next_move = safe_random_search(game_state)
        print(f"MOVE {game_state['turn']}: {next_move} (Safe - Random)")

    elif rollout == "heuristic":
        next_move = heuristic_search(game_state)
        print(f"MOVE {game_state['turn']}: {next_move} (Heuristic)")

    elif rollout == 'vanilla-mcts':
        next_move = vanilla_mcts_search(game_state)
        print(f"MOVE {game_state['turn']}: {next_move} (Vanilla MCTS)")

    else:
        next_move = mcts_search(game_state)
        print(f"MOVE {game_state['turn']}: {next_move} (MCTS)")

    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server
    port = os.environ.get("PORT", "8000")
    run_server({"info": info, "start": start, "move": move, "end": end}, port=port)