from snake_helpers import safe_moves
from simulator import simulate_step
from MCTS import evaluate_state


def heuristic_search(state):
    my_id = state['you']['id']
    possible_moves = safe_moves(state, my_id)

    if not possible_moves:
        return "down"

    best_move = possible_moves[0]
    best_score = -float('inf')

    for move in possible_moves:
        moves = {my_id: move}
        for s in state['board']['snakes']:
            if s['id'] != my_id:
                moves[s['id']] = "up"

        next_state = simulate_step(state, moves)
        score = evaluate_state(next_state, my_id)

        if score > best_score:
            best_score = score
            best_move = move

    return best_move