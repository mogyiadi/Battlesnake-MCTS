import typing


def avoid_collision_with_body(is_move_safe, my_head, segment):
    if segment['x'] == my_head['x'] and segment['y'] == my_head['y'] - 1:
        is_move_safe['down'] = False
    elif segment['x'] == my_head['x'] and segment['y'] == my_head['y'] + 1:
        is_move_safe['up'] = False
    elif segment['x'] == my_head['x'] - 1 and segment['y'] == my_head['y']:
        is_move_safe['left'] = False
    elif segment['x'] == my_head['x'] + 1 and segment['y'] == my_head['y']:
        is_move_safe['right'] = False

    return is_move_safe


def safe_moves(game_state: typing.Dict, snake_id):
    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    snakes = game_state["board"]["snakes"]

    # Find snake by id in the list
    my_snake = next((s for s in snakes if s["id"] == snake_id), None)
    if my_snake is None:
        return []

    my_head = my_snake["body"][0]

    my_neck = my_snake["body"][1]  # Coordinates of your "neck"

    if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
        is_move_safe["left"] = False

    elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
        is_move_safe["right"] = False

    elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
        is_move_safe["down"] = False

    elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
        is_move_safe["up"] = False

    # Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    if my_head['x'] - 1 < 0:
        is_move_safe['left'] = False
    elif my_head['x'] + 1 >= board_width:
        is_move_safe['right'] = False

    if my_head['y'] - 1 < 0:
        is_move_safe['down'] = False
    elif my_head['y'] + 1 >= board_height:
        is_move_safe['up'] = False

    # Prevent your Battlesnake from colliding with other Battlesnakes (including itself)

    for snake in snakes:
        snake_health = snake['health']
        # If the snake is at full health, it has just eaten a food pellet,
        # in which case, the tail will stay in the current spot (because the snake grows longer)
        if snake_health == 100 and game_state['turn'] != 1:
            for segment in snake['body']:
                is_move_safe = avoid_collision_with_body(is_move_safe, my_head, segment)

        # If the snake is not at full health, the tail will move forward
        # (because the snake did not grow)
        else:
            for segment in snake['body'][:-1]:
                is_move_safe = avoid_collision_with_body(is_move_safe, my_head, segment)

    # Are there any safe moves left?
    s_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            s_moves.append(move)

    # If 1 or less safe moves, return
    if len(s_moves) <= 1:
        return s_moves
    # If more than 1 safe move, check for potential head-on collisions
    # with other snakes that are the same length or longer
    else:
        for other_snake in snakes:
            if other_snake['id'] == snake_id:
                continue

            if other_snake['length'] >= my_snake['length']:
                other_head = other_snake['body'][0]

                # Calculate the potential next cells for the other snake's head
                potential_other_snake_next_cells = [
                    {"x": other_head["x"], "y": other_head["y"] + 1},
                    {"x": other_head["x"], "y": other_head["y"] - 1},
                    {"x": other_head["x"] - 1, "y": other_head["y"]},
                    {"x": other_head["x"] + 1, "y": other_head["y"]}
                ]

                # Check which moves might collide with the other snake's head
                if is_move_safe["up"] and {"x": my_head["x"], "y": my_head["y"] + 1} in potential_other_snake_next_cells:
                    is_move_safe["up"] = False
                if is_move_safe["down"] and {"x": my_head["x"], "y": my_head["y"] - 1} in potential_other_snake_next_cells:
                    is_move_safe["down"] = False
                if is_move_safe["left"] and {"x": my_head["x"] - 1, "y": my_head["y"]} in potential_other_snake_next_cells:
                    is_move_safe["left"] = False
                if is_move_safe["right"] and {"x": my_head["x"] + 1, "y": my_head["y"]} in potential_other_snake_next_cells:
                    is_move_safe["right"] = False

        new_s_moves = []
        for move, isSafe in is_move_safe.items():
            if isSafe:
                new_s_moves.append(move)
        if new_s_moves:
            return new_s_moves
        # If all safe moves are potentially unsafe due to head-on collisions,
        # return the original safe moves
        else:
            return s_moves