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
        if snake_health == 100:
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

    return s_moves