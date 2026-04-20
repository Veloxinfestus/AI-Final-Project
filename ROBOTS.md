# ROBOTS.md
This file defines the structure and contribution rules for AI agents assisting with the Study Planner project.

## Project Purpose
This project generates weekly study plans for students based on:
- tasks
- estimated hours needed
- daily available study time

The final version will include an optimization or machine learning component.

## Current File Structure (Day 1)
- `src/planner.py` — simple rule-based scheduling prototype.
- `tests/` — empty for now; testing will be added later.
- `README.md` — human-readable project overview.
- `ROBOTS.md` — instructions for AI agents.
- `example_config.json` — example of the data format future versions will support.

## Rules for AI Agents
1. Do not modify existing files unless explicitly instructed.
2. Place all new code inside the `src/` directory.
3. Place all new tests inside the `tests/` directory.
4. Keep functions small, documented, and testable.
5. Do not introduce external dependencies without human approval.
6. Maintain compatibility with Python’s standard library unless told otherwise.
7. Follow the existing structure and naming conventions.

## Future Planned Components
AI agents may create these files in later pull requests:
- `src/optimizer.py` — optimization algorithm for scheduling.
- `src/input_handler.py` — user input or config file parsing.
- `src/ui.py` — desktop or web interface.
- `tests/test_planner.py` — tests for scheduling logic.
- `tests/test_optimizer.py` — tests for optimization logic.

## Contribution Workflow for AI Agents
1. Read this file before generating code.
2. Follow the current architecture.
3. Propose new modules when adding major features.
4. Ensure all new code is documented and testable.
5. Maintain separation between:
   - scheduling logic
   - optimization logic
   - user interface
   - data handling
