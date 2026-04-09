import json
import os
import random
import subprocess
import sys
import time

GAMES_TO_PLAY = 20
CONFIGS = 10


def get_random_weights():
    # randomly pick numbers
    w_len = random.uniform(0.0, 0.3)
    w_hp = random.uniform(0.1, 0.5)
    w_safe = random.uniform(0.2, 0.6)
    w_food = random.uniform(0.0, 0.4)
    w_reach = random.uniform(0.1, 0.5)

    # make sure they add up to 1
    total = w_len + w_hp + w_safe + w_food + w_reach

    weights = {
        "W_LENGTH": round(w_len / total, 3),
        "W_HEALTH": round(w_hp / total, 3),
        "W_SAFE": round(w_safe / total, 3),
        "W_FOOD": round(w_food / total, 3),
        "W_REACH": round(w_reach / total, 3),
        "W_HAZARD": round(random.uniform(-1.0, -0.1), 3)  # hazard is negative
    }
    return weights


def check_winner():
    if not os.path.exists("tuner_log.json"):
        return "Draw"

    with open("tuner_log.json", "r") as f:
        lines = f.readlines()

    if len(lines) == 0:
        return "Draw"

    # get the very last line of the file to see who is alive
    last_line = ""
    for line in lines:
        if line.strip() != "":
            last_line = line

    try:
        data = json.loads(last_line)
        snakes = data["board"]["snakes"]
        if len(snakes) == 1:
            return snakes[0]["name"]
        else:
            return "Draw"
    except:
        return "Draw"


def main():
    print("starting tuning script...")

    for c in range(CONFIGS):
        weights = get_random_weights()
        print("\ntesting weights:", weights)

        scores = {"Baseline": 0, "Challenger": 0, "Vanilla": 0, "Heuristic": 0, "Draw": 0}
        procs = []

        # 1. start base
        e1 = os.environ.copy()
        e1["PORT"] = "8000"
        e1["SNAKE_BRAIN"] = "mcts"
        p1 = subprocess.Popen([sys.executable, "main.py"], env=e1, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(p1)

        # 2. start challenger
        e2 = os.environ.copy()
        e2["PORT"] = "8001"
        e2["SNAKE_BRAIN"] = "mcts"
        for k in weights:
            e2[k] = str(weights[k])
        p2 = subprocess.Popen([sys.executable, "main.py"], env=e2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(p2)

        # 3. start vanilla
        e3 = os.environ.copy()
        e3["PORT"] = "8002"
        e3["SNAKE_BRAIN"] = "vanilla-mcts"
        p3 = subprocess.Popen([sys.executable, "main.py"], env=e3, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(p3)

        # 4. start heuristic
        e4 = os.environ.copy()
        e4["PORT"] = "8003"
        e4["SNAKE_BRAIN"] = "heuristic"
        p4 = subprocess.Popen([sys.executable, "main.py"], env=e4, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        procs.append(p4)

        time.sleep(3)  # wait for servers

        cmd = [
            "./battlesnake", "play", "-W", "11", "-H", "11", "-g", "standard", "-m", "hz_hazard_pits",
            "--name", "Baseline", "--url", "http://127.0.0.1:8000",
            "--name", "Challenger", "--url", "http://127.0.0.1:8001",
            "--name", "Vanilla", "--url", "http://127.0.0.1:8002",
            "--name", "Heuristic", "--url", "http://127.0.0.1:8003",
            "--timeout", "1000", "--output", "tuner_log.json"
        ]

        for i in range(GAMES_TO_PLAY):
            if os.path.exists("tuner_log.json"):
                os.remove("tuner_log.json")

            print(f"playing game {i + 1}... ", end="", flush=True)
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            winner = check_winner()
            print("winner:", winner)

            if winner in scores:
                scores[winner] += 1
            else:
                scores["Draw"] += 1

        # kill everything before next loop
        for p in procs:
            p.kill()

        print("scores ->", scores)

        if scores["Challenger"] > scores["Baseline"]:
            print("found better weights! saving to file.")
            with open("best_weights.json", "a") as f:
                json.dump({"chal_score": scores["Challenger"], "base_score": scores["Baseline"], "weights": weights}, f)
                f.write("\n")


if __name__ == "__main__":
    main()