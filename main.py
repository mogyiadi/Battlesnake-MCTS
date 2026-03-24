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

    elif rollout == "safe - random":
        s_moves = safe_moves(game_state, game_state['you']['id'])
        if len(s_moves) == 0:
            print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
            return {"move": "down"}
        next_move = random.choice(s_moves)
        print(f"MOVE {game_state['turn']}: {next_move} (Safe - Random)")

    elif rollout == "heuristic":
        my_id = game_state['you']['id']

        my_s_moves = safe_moves(game_state, my_id)

        moves = {}
        for snake in game_state['board']['snakes']:
            if snake['id'] != my_id:
                s_moves = safe_moves(game_state, snake['id'])
                moves[snake['id']] = random.choice(s_moves) if s_moves else "down"

        best_score = -float('inf')
        best_move = random.choice(my_s_moves) if my_s_moves else 'down'
        for move in my_s_moves:
            moves[my_id] = move
            potential_next_state = simulate_step(game_state, moves)
            score = evaluate_state(potential_next_state, my_id)

            if score > best_score:
                best_score = score
                best_move = move

        next_move = best_move
        print(f"MOVE {game_state['turn']}: {best_move} (Heuristic)")

    else:
        next_move = mcts_search(game_state)
        print(f"MOVE {game_state['turn']}: {next_move} (MCTS)")

    return {"move": next_move}


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
