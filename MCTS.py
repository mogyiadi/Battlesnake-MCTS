import copy
import math
import random
import time
from collections import deque

from snake_helpers import safe_moves
from simulator import simulate_step


class MCTSnode:
    def __init__(self, state, parent=None, move=None, heuristic_score=0):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.score = 0
        self.visits = 0

        self.heuristic_score = heuristic_score

    # TODO: Implement a different evaluation function here (assignment mentions Rapid Value Action Estimation)
    def ucb(self):
        if self.visits == 0:
            return float('inf')
        exploitation = self.score / self.visits
        exploration = math.sqrt(2) * math.sqrt(math.log(self.parent.visits) / self.visits)

        # Progressive Bias
        W = 5
        mean_reward = self.score / self.visits
        progressive_bias = W * self.heuristic_score / (self.visits * (1 - mean_reward) + 1)
        return exploration + exploitation + progressive_bias


def evaluate_state(state, current_id):
    snakes = state['board']['snakes']
    snake = next((s for s in snakes if s['id'] == current_id), None)

    # If dead, return -1000
    if snake is None:
        return -1000

    # if no other snakes, return 1
    if len(state["board"]["snakes"]) == 1:
        return 1

    # Snake length heuristic
    l_snake = snake['length']
    l_largest_snake = max([s['length'] for s in snakes])
    l_snake_score = l_snake / l_largest_snake

    # Health heuristic
    health_snake = snake['health']
    health_score = health_snake / 100

    # Safe moves heuristic
    s_moves = safe_moves(state, current_id)
    if len(s_moves) == 0:
        return -1000
    safe_moves_score = len(s_moves) / 4

    # Food distance heuristic
    my_head = snake['body'][0]
    closest_dist_to_food = float('inf')
    foods = state['board']['food']
    if foods:
        for food in state['board']['food']:
            dist = abs(food['x'] - my_head['x']) + abs(food['y'] - my_head['y'])
            if dist < closest_dist_to_food:
                closest_dist_to_food = dist
        board_max_dist = state['board']['width'] + state['board']['height']
        food_score = 1 - (closest_dist_to_food / board_max_dist)
    else:
        food_score = 0.5


    # Reachable cells heuristic
    board_size = state['board']['width'] * state['board']['height']
    reachable_cells = num_reachable_cells(state, current_id)
    reachable_score = reachable_cells / board_size

    # Hazard heuristic
    hazard_penalty = 0
    if state['turn'] >= 26:
        hazards = state['board'].get('hazards', [])
        if {'x': my_head['x'], 'y': my_head['y']} in hazards:
            hazard_penalty = -0.5

    # Combine heuristics with weights
    score = (
            0.05 * l_snake_score +
            0.25 * health_score +
            0.35 * safe_moves_score +
            0.15 * food_score +
            0.2 * reachable_score +
            hazard_penalty
    )

    return score


def num_reachable_cells(state, snake_id):
    snake = next((s for s in state['board']['snakes'] if s['id'] == snake_id), None)
    head = snake['body'][0]
    head_position = (head['x'], head['y'])

    visited = set()
    queue = deque([head_position])

    blocked = set()
    for s in state['board']['snakes']:
        for segment in s['body']:
            blocked.add((segment['x'], segment['y']))


    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))

        # Look in all 4 directions
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy

            # Don't go out of bounds
            if not (0 <= nx < state['board']['width'] and
                    0 <= ny < state['board']['height']):
                continue

            # Don't go through snakes
            if (nx, ny) in blocked:
                continue

            if (nx, ny) in visited:
                continue

            queue.append((nx, ny))

    return len(visited)




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
                        moves[other_snake_id] = random.choice(s_moves) if s_moves else "down"

                next_state = simulate_step(leaf.state, moves)
                heuristic_score = evaluate_state(next_state, my_id)
                new_child = MCTSnode(next_state, parent=leaf, move=move, heuristic_score=heuristic_score)
                leaf.children.append(new_child)
                node_to_simulate = new_child

        # Simulation
        simulation_depth = 50
        current_state = copy.deepcopy(node_to_simulate.state)

        for _ in range(simulation_depth):
            if current_state['turn'] >= 300:
                break

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

