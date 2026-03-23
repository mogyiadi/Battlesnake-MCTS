import copy
import math
import random
import time

from snake_helpers import safe_moves
from simulator import simulate_step


class MCTSnode:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.score = 0
        self.visits = 0

    # TODO: Implement a different evaluation function here (assignment mentions Rapid Value Action Estimation)
    def ucb(self):
        if self.visits == 0:
            return float('inf')
        return (self.score / self.visits) + math.sqrt(2) * math.sqrt(math.log(self.parent.visits) / self.visits)


def evaluate_state(state, current_id):
    snakes = state['board']['snakes']
    snake = next((s for s in snakes if s['id'] == current_id), None)

    if snake is None:
        return 0

    if len(state["board"]["snakes"]) == 1:
        return 1

    l_snake = snake['length']
    l_largest_snake = max([s['length'] for s in snakes])

    health_snake = snake['health']

    # TODO: Add better evaluation function here (for example checking how much of the map the snake controls)

    return 0.5 * (l_snake / l_largest_snake) + 0.5 * (health_snake / 100)



def mcts_search(root_state):
    timeout = 0.8
    start_time = time.time()
    my_id = root_state['you']['id']
    root = MCTSnode(root_state)

    while time.time() < start_time + timeout:
        # Selection
        leaf = root
        while leaf.children:
            possible_moves = safe_moves(leaf.state, my_id)
            if len(leaf.children) < len(possible_moves):
                break
            leaf = max(leaf.children, key=lambda c: c.ucb())

        # Expansion
        node_to_simulate = leaf
        is_game_over = my_id not in [s['id'] for s in leaf.state['board']['snakes']]
        if not is_game_over:
            possible_moves = safe_moves(leaf.state, my_id)
            expanded_moves = {child.move for child in leaf.children}
            unexpanded_moves = [m for m in possible_moves if m not in expanded_moves]

            if unexpanded_moves:
                move = random.choice(unexpanded_moves)

                moves = {my_id: move}
                for snake in leaf.state['board']['snakes']:
                    other_snake_id = snake['id']
                    if other_snake_id != my_id:
                        s_moves = safe_moves(leaf.state, other_snake_id)
                        moves[snake['id']] = random.choice(s_moves) if s_moves else "down"

                next_state = simulate_step(leaf.state, moves)
                new_child = MCTSnode(next_state, parent=leaf, move=move)
                leaf.children.append(new_child)
                node_to_simulate = new_child

        # Simulation
        simulation_depth = 15
        current_state = copy.deepcopy(node_to_simulate.state)

        for _ in range(simulation_depth):
            snakes = current_state['board']['snakes']
            if my_id not in [s['id'] for s in snakes] or len(snakes) <= 1:
                break

            rollout_moves = {}
            for snake in snakes:
                potential_moves = safe_moves(current_state, snake['id'])
                rollout_moves[snake['id']] = random.choice(potential_moves) if potential_moves else "down"

            current_state = simulate_step(current_state, rollout_moves)

        score = evaluate_state(current_state, my_id)

        # Backpropagation
        temp_node = node_to_simulate
        while temp_node is not None:
            temp_node.visits += 1
            temp_node.score += score
            temp_node = temp_node.parent

    if not root.children:
        s_moves = safe_moves(root_state, my_id)
        return random.choice(s_moves) if s_moves else "down"

    best_child = max(root.children, key=lambda c: c.visits)
    return best_child.move

