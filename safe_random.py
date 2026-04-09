import random
from snake_helpers import safe_moves

def safe_random_search(state):
    my_id = state['you']['id']
    possible_moves = safe_moves(state, my_id)

    if not possible_moves:
        return "down"  # Default if no moves are safe

    return random.choice(possible_moves)

