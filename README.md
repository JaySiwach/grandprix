# Python Grand Prix — ready-to-run project

## Windows (VS Code / PowerShell)
1. Extract this ZIP. Open the `Python_Grand_Prix` folder in VS Code.
2. Open Terminal → New Terminal.
3. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again.
4. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
5. Start the game:
   ```powershell
   python main.py
   ```

Python 3.8+ and Tkinter are required. On Windows, install Python from python.org and enable Tcl/Tk during installation. Pillow is optional for gameplay; it enables textured assets.

## Project structure
- `main.py` — game entry point
- `config/settings.py` — settings and asset paths
- `game/` — game logic, race rendering, questions, UI, data and leaderboard
- `assets/images/` — player and AI car images
- `tools/generate_assets.py` — optional asset generator

The save file `pygp_save.json` is created in this folder after a completed championship.

## Question bank and random questions

- The game includes 50 Python built-in topics.
- Each topic has 2 original questions plus 50 additional questions (52 per topic).
- That gives 2,600 questions across the complete question bank.
- Each Grand Prix asks up to 15 randomly selected Python questions, cycling through its 10 topic categories.
- The player must answer 10 questions correctly to cross the finish line and win; fewer than 10 correct after all 15 questions ends the Grand Prix.
- The 50-topic championship order remains the same; the question within each topic changes randomly.
- Correct answers automatically trigger a boost and load the next question. Three wrong answers end the run.


## Latest gameplay updates
- The player's car advances only after a correct answer.
- Wrong answers do not move the player's car forward.
- Correct answers trigger the automatic boost.
- The next question loads quickly (about 0.35 seconds after feedback).
- The track refreshes frequently for smoother car movement.


## Race results and leaderboard
- Every completed race saves the driver, Grand Prix, actual finishing position, score, time, and date.
- A race ended by the three-wrong-answer rule is also saved with the player's current position.
- The home screen shows the best saved race finishes.
- The Leaderboard screen shows race-by-race history and completed championship rankings.
- Data is stored locally in the JSON file configured in `config/settings.py`.


## Gameplay rules in this version
- Three wrong answers are allowed per Grand Prix. A fourth wrong answer ends only that GP; the counter resets in the next GP.
- Restart Game and Quit Game controls are available during races and on result screens.
- The NPC cars have different speed ranges and individual finish-line crossing times.
- Race standings rank cars that crossed the finish line by crossing time; cars still racing follow by progress.
- If all three NPCs cross the finish line before the player, the player is automatically placed P4 and that GP ends.
- The championship standings are sorted by total score and displayed at the end.
- Every GP receives a fresh shuffled question deck. Questions are drawn without replacement during that GP, and answer options are shuffled.
- The question bank has 102 questions per built-in topic (2 original plus 100 additional prompts).


## Latest pacing and Grand Prix progression update
- NPC cars are now deliberately slower: Byte takes about 125-143 seconds, Lambda about 143-167 seconds, and Numpy about 111-125 seconds to cover the track.
- This gives the player more time to read and answer the 10 quiz questions.
- The Next Grand Prix button is shown only after the player crosses the current Grand Prix finish line.
- If all three NPCs finish first, the player receives P4 and cannot advance to the next Grand Prix.
- If the fourth wrong answer ends the current Grand Prix, the next Grand Prix remains locked.
- The next-race action also checks completion internally, so it cannot be triggered by bypassing the hidden/disabled button.


## Finish-line ranking

- The player crosses the finish line immediately after the 10th correct answer.
- The game compares that timestamp with NPC finish times. First to finish is 1st, next is 2nd, next is 3rd, and last is 4th.
- Players may answer up to 15 questions to reach 10 correct. The third wrong answer still ends the current Grand Prix.
