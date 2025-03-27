# Zwift Workout Generator

A Python script that converts text-based workout descriptions into Zwift-compatible .zwo files.

## Features

- Parses natural workout notation into structured Zwift workouts
- Handles various workout elements:
  - Intervals (e.g., 30/30 max/easy)
  - SFR (Slow Frequency Repetitions) with low cadence
  - Recovery periods
  - Steady state blocks
  - Warm-up and cool-down
- Converts power zones to FTP percentages
- Adds detailed workout descriptions with:
  - Pre-activity instructions
  - Clear workout structure
  - Best practices and form cues

## Example Usage

```python
from workout_generator import save_workout

workout = """Z1-Z2 base with focus on efforts as follows:

-6x5' / 3' recovery done as...
30" max / 30" easy
4' SFR (50-60r, 300-330w)

-1 x 20' Z3 HR (150-160bpm), mostly 85+ rpm"""

filepath = save_workout("SFR_Intervals", workout)
print(f"Workout saved to: {filepath}")
```

## Power Zones

The script uses the following FTP percentages for power zones:
- Z1: 50% FTP
- Z2: 65% FTP
- Z3: 83% FTP
- Z4: 98% FTP
- Z5: 113% FTP
- Z6/Max: 120% FTP

## Dependencies

- Python 3.x
- lxml

## Installation

1. Clone this repository
2. Install dependencies: `pip install lxml`
3. Run the script: `python workout_generator.py`

## File Structure

The generated .zwo files will be saved to your Downloads folder with the format:
`[workout_name]_[timestamp].zwo` 