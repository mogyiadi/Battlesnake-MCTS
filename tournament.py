import json
import os
import subprocess
import sys
import time

GAMES = 15

# Changed ports to 8010+ to avoid the "ghost" servers from the tuner crashing the game!
snakes = [
    {"name": "Steered_MCTS", "port": "8010", "brain": "mcts"},
    {"name": "Vanilla_MCTS", "port": "8011", "brain": "vanilla-mcts"},
    {"name": "Heuristic", "port": "8012", "brain": "heuristic"},
    {"name": "Safe_Random", "port": "8013", "brain": "safe - random"}
]

elo = {
    "Steered_MCTS": 1200,
    "Vanilla_MCTS": 1200,
    "Heuristic": 1200,
    "Safe_Random": 1200
}


def update_elo(rankings):
    global elo
    # rankings is ordered worst to best
    for i in range(len(rankings)):
        for j in range(i + 1, len(rankings)):
            player_a = rankings[i]  # this player lost
            player_b = rankings[j]  # this player won

            ra = elo[player_a]
            rb = elo[player_b]

            exp_a = 1 / (1 + 10 ** ((rb - ra) / 400))
            exp_b = 1 / (1 + 10 ** ((ra - rb) / 400))

            elo[player_a] = ra + 32 * (0 - exp_a)
            elo[player_b] = rb + 32 * (1 - exp_b)


def get_survivors():
    if not os.path.exists("tourney_log.json"):
        return []

    with open("tourney_log.json", "r") as f:
        lines = f.readlines()

    if len(lines) == 0:
        return []

    # get the last line of the log
    last_line = ""
    for line in lines:
        if line.strip() != "":
            last_line = line

    try:
        data = json.loads(last_line)
        alive_snakes = data["board"]["snakes"]

        # sort by length to see who did best
        alive_snakes.sort(key=lambda s: s["length"])

        survivors = []
        for s in alive_snakes:
            survivors.append(s["name"])

        return survivors
    except:
        return []


def main():
    print("starting final tournament...")

    procs = []

    # boot up all 4 snakes
    for s in snakes:
        env = os.environ.copy()
        env["PORT"] = s["port"]
        env["SNAKE_BRAIN"] = s["brain"]

        p = subprocess.Popen([sys.executable, "main.py"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(p)

    time.sleep(3)  # wait for them to wake up

    cmd = [
        "./battlesnake", "play", "-W", "11", "-H", "11", "-g", "standard", "-m", "hz_hazard_pits",
        "--timeout", "1000", "--output", "tourney_log.json"
    ]

    # add the snake urls to the command
    for s in snakes:
        cmd.append("--name")
        cmd.append(s["name"])
        cmd.append("--url")
        cmd.append("http://127.0.0.1:" + s["port"])

    for i in range(GAMES):
        if os.path.exists("tourney_log.json"):
            os.remove("tourney_log.json")

        print(f"playing game {i + 1}... ", end="", flush=True)

        # We capture stderr here so if the engine crashes again, it prints the real reason!
        proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

        survivors = get_survivors()

        if len(survivors) == 0:
            print("Crash or Error!")
            if proc.stderr:
                print("Error reason:", proc.stderr.strip())
        else:
            print("survivors:", ", ".join(survivors))
            if len(survivors) > 1:
                update_elo(survivors)

    # kill background snakes
    for p in procs:
        p.kill()

    print("\n--- FINAL ELO ---")
    # sort dictionary by elo value
    sorted_elo = sorted(elo.items(), key=lambda x: x[1], reverse=True)
    for rank, (name, score) in enumerate(sorted_elo):
        print(f"{rank + 1}. {name}: {round(score, 1)}")


if __name__ == "__main__":
    main()