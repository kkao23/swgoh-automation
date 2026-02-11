# SWGOH Automation Scripts

Python automation scripts for Star Wars Galaxy of Heroes using pyautogui and Google Generative AI.

## Setup

### 1. Create Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

```bash
cp .env.example .env
```

Edit `.env` and add your Google API key:
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Scripts

### Morning Routine

```bash
python swgoh_morning.py [step_number]
```

Steps:
- 1: Claim Daily Quests
- 2: Energy (skipped)
- 3: Mod Battles
- 4: Fleet Battles
- 5: Light Side Battles
- 6: Cantina Battles

Run all steps:
```bash
python swgoh_morning.py
```

Run single step:
```bash
python swgoh_morning.py 3  # Run only Mod Battles
```

### Evening Routine

```bash
python swgoh_evening.py [step_number]
```

Steps:
- 1: Coliseum
- 2: Claim Existing Quests
- 3: Galactic War Battle
- 4: Finish 2 Challenges
- 5: Finish 1 Fleet Challenge
- 6: Claim Energy

Run all steps:
```bash
python swgoh_evening.py
```

Run single step:
```bash
python swgoh_evening.py 2  # Run only Claim Quests
```

### Fleet Battles

**First (Going First):**
```bash
python fleet_battle_first.py
```
Sequence: E S W W E Q Q Q T Down Down C

**Second (Going Second):**
```bash
python fleet_battle.py
```
Sequence: W W E E S Q Q Q W T Down Down W Q Q Q W S Q Q W W T Up Up Q Q C

Both scripts press keys with 3-second pauses between each.

## Requirements

- Python 3.8+
- Star Wars Galaxy of Heroes running on emulator or PC
- Google API key for AI features (only used in morning/evening routines)

## How It Works

- Scripts use `pyautogui` to send keyboard presses and mouse clicks
- Window detection finds the SWGOH game window automatically
- Morning/evening routines use Google Gemini AI to analyze screenshots
- Fleet battle scripts are simple key sequences with timed delays

## Safety

- Scripts include 5-second countdown before starting
- Press Ctrl+C to cancel at any time
- Keep the game window visible during automation
