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
from MCTS import mcts_search
from snake_helpers import safe_moves


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
    rollout = "heuristic"

    if rollout == "random":
        next_move = random.choice(["up", "down", "left", "right"])
        print(f"MOVE {game_state['turn']}: {next_move} (Random)")

    elif rollout == "heuristic":
        s_moves = safe_moves(game_state, game_state['you']['id'])
        if len(s_moves) == 0:
            print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
            return {"move": "down"}

        # Move towards food instead of random, to regain health and survive longer
        food = game_state['board']['food']
        my_head = game_state['you']['body'][0]
        closest_food = min(food, key=lambda f: abs(f['x'] - my_head['x']) + abs(f['y'] - my_head['y']))

        if closest_food['x'] > my_head['x'] and 'right' in s_moves:
            next_move = 'right'
        elif closest_food['x'] < my_head['x'] and 'left' in s_moves:
            next_move = 'left'
        elif closest_food['y'] > my_head['y'] and 'up' in s_moves:
            next_move = 'up'
        elif closest_food['y'] < my_head['y'] and 'down' in s_moves:
            next_move = 'down'
        else:
            next_move = random.choice(s_moves)


        if random.random() < 0.8:
            # Choose a random move from the safe ones
            next_move = random.choice(s_moves)

        print(f"MOVE {game_state['turn']}: {next_move} (Heuristic)")

    else:
        next_move = mcts_search(game_state)
        print(f"MOVE {game_state['turn']}: {next_move} (MCTS)")

    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
