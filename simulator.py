import copy


def simulate_step(current_state, moves):
    next_state = copy.deepcopy(current_state)

    next_state["turn"] += 1
    turn = next_state["turn"]

    board = next_state["board"]
    snakes = board["snakes"]
    food = board["food"]

    # Calculate hazard damage
    if turn < 26:
        hazard_damage = 0
        board["hazards"] = []
    elif turn <= 50:
        hazard_damage = 14
    elif turn <= 75:
        hazard_damage = 28
    elif turn <= 100:
        hazard_damage = 42
    elif turn <= 175:
        hazard_damage = 56
    else:
        hazard_damage = 0
        board["hazards"] = []  # Fully drains after 75 turns of max stacks

    dead_snake_ids = set()

    # Move and subtract health
    for snake in snakes:
        snake_id = snake["id"]
        # If no move is provided
        if snake_id not in moves:
            move = "down"
        else:
            move = moves[snake_id]

        head = snake["body"][0]
        new_head = {"x": head["x"], "y": head["y"]}

        if move == "up":
            new_head["y"] += 1
        elif move == "down":
            new_head["y"] -= 1
        elif move == "left":
            new_head["x"] -= 1
        elif move == "right":
            new_head["x"] += 1

        snake["body"].insert(0, new_head)
        snake["health"] -= 1

        if new_head in board.get("hazards", []):
            snake["health"] -= hazard_damage

    # Check for collisions with walls and other snakes
    for snake in snakes:
        head = snake["body"][0]

        # If the snake moves out of bounds, it dies
        if head["x"] < 0 or head["x"] >= board["width"] or head["y"] < 0 or head["y"] >= board["height"]:
            dead_snake_ids.add(snake["id"])
            continue

        for other_snake in snakes:
            # If the snake collides with itself or another snake's body, it dies
            if head in other_snake["body"][1:]:
                dead_snake_ids.add(snake["id"])
                break

            # If the snake's head collides with another snake's head,
            # the shorter snake dies (or both if they are of the same length)
            if snake["id"] != other_snake["id"]:
                other_head = other_snake["body"][0]
                if head == other_head:
                    if snake["length"] <= other_snake["length"]:
                        dead_snake_ids.add(snake["id"])
                        break

    # Eat food and grow
    for snake in snakes:
        if snake['id'] in dead_snake_ids:
            continue
        head = snake["body"][0]

        # If the snake eats food, it grows (doesn't remove tail),
        # and health resets to 100
        if head in food:
            snake["health"] = 100
            snake["length"] += 1
            food.remove(head)
        # If the snake doesn't eat food,
        # it moves forward without growing
        # (so the tail is removed)
        else:
            snake["body"].pop()

        if snake["health"] <= 0:
            dead_snake_ids.add(snake["id"])

    next_state["board"]["snakes"] = [snake for snake in snakes if snake["id"] not in dead_snake_ids]

    return next_state