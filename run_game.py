import json
import os
import subprocess
import sys
import time
from pathlib import Path

MAX_TURNS = 300
LOG_PATH = Path("game.json")

NUM_SNAKES = 4
BASE_PORT = 8000

CMD = [
    "battlesnake", "play",
    "-W", "11", "-H", "11",
    "-g", "standard",
    "-m", "hz_hazard_pits",

]

for i in range(NUM_SNAKES):
    port = BASE_PORT + i
    CMD.extend(["--name", f"Snake{i+1}", "--url", f"http://127.0.0.1:{port}"])

CMD.extend([
    "--foodSpawnChance", "25",
    "--minimumFood", "2",
    "--seed", "69",
    "--timeout", "1000",
    "--browser",
    "--output", str(LOG_PATH),
])

def load_last_state(path: Path):
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    if not lines:
        return None

    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        if isinstance(obj, dict) and "turn" in obj:
            return obj

    return None

def main():
    if LOG_PATH.exists():
        LOG_PATH.unlink()


    snake_processes = []
    print("Starting ", NUM_SNAKES, " snakes...")
    for i in range(NUM_SNAKES):
        port = BASE_PORT + i
        env = os.environ.copy()
        env["PORT"] = str(port)

        snake_processes.append(
            subprocess.Popen(
                [sys.executable, "main.py"],
                env=env,
            )
        )

    proc = subprocess.Popen(CMD)

    last_turn = -1
    last_state = None

    try:
        while proc.poll() is None:
            state = load_last_state(LOG_PATH)
            if state is not None:
                last_state = state
                turn = int(state.get("turn", -1))

                if turn == -1:
                    time.sleep(0.1)
                    continue

                if turn != last_turn:
                    last_turn = turn
                    print(f"turn={turn}")

                if turn >= MAX_TURNS:
                    print(f"Reached cap at turn {turn}. Stopping game.")
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    break

            time.sleep(0.1)

    finally:
        if proc.poll() is None:
            proc.kill()

        for p in snake_processes:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill()

    if last_state is None:
        print("Game end")
        return

    for snake in last_state["board"]["snakes"]:
          print(snake["name"], snake["length"])


if __name__ == "__main__":
    main()