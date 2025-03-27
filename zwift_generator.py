import xml.etree.ElementTree as ET
import os
from datetime import datetime

# Function to generate a Zwift workout .zwo file
def generate_zwo(workout_name, description, warmup_time, intervals, cooldown_time, filename, num_sets):
    # Create the root element
    workout = ET.Element("workout_file")

    # Add required elements in correct order
    ET.SubElement(workout, "author").text = "Gravel God Cycling"
    ET.SubElement(workout, "name").text = workout_name
    
    # Add description with proper CDATA formatting
    desc = ET.SubElement(workout, "description")
    desc.text = description  # The CDATA will be handled in the XML output
    
    sport_type = ET.SubElement(workout, "sportType")
    sport_type.text = "bike"
    
    # Empty tags element
    ET.SubElement(workout, "tags")

    # Create workout section
    workout_section = ET.SubElement(workout, "workout")

    # Warm-up (Using range-based power)
    ET.SubElement(workout_section, "Warmup", 
                  Duration=str(warmup_time), 
                  PowerLow="0.56", PowerHigh="0.75")

    # Main Set - Repeat 5 times
    for _ in range(num_sets):  # Repeat the entire sequence 5 times
        # First 40/20 block (2 minutes = 3 repeats)
        ET.SubElement(workout_section, "IntervalsT",
                     Repeat="3",  # 3 repeats = 2 minutes (3 x (40s + 20s))
                     OnDuration="40",
                     OnPower="1.2",  # Max Effort
                     OffDuration="20",
                     OffPower="0.65")  # Z2
        
        # 4 min Z3/Z4 block
        ET.SubElement(workout_section, "SteadyState",
                     Duration="240",
                     Power="0.85")  # Z3/Z4
        
        # Second 40/20 block (2 minutes = 3 repeats)
        ET.SubElement(workout_section, "IntervalsT",
                     Repeat="3",  # 3 repeats = 2 minutes (3 x (40s + 20s))
                     OnDuration="40",
                     OnPower="1.2",  # Max Effort
                     OffDuration="20",
                     OffPower="0.65")  # Z2
        
        # 4 min recovery (1:1 ratio with the 4 min Z3/Z4 block)
        ET.SubElement(workout_section, "SteadyState",
                     Duration="240",
                     Power="0.65")  # Z2

    # Cool-down (Using range-based power)
    ET.SubElement(workout_section, "Cooldown", 
                  Duration=str(cooldown_time), 
                  PowerLow="0.56", PowerHigh="0.75")

    # Convert XML to a formatted string
    tree = ET.ElementTree(workout)
    ET.indent(tree, space="\t")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Save to file with proper XML declaration and CDATA
    with open(filename, "wb") as f:
        f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        # Write the description with CDATA
        xml_str = ET.tostring(workout, encoding='unicode')
        xml_str = xml_str.replace('<description>', '<description><![CDATA[')
        xml_str = xml_str.replace('</description>', ']]></description>')
        f.write(xml_str.encode('utf-8'))

    print(f"Workout '{workout_name}' saved as {filename}")

if __name__ == "__main__":
    # Create two workout variations
    workouts = [
        {
            "workout_name": "Gavin Special - 3x8min",
            "description": """► Pre-activity Instructions:
- Focus on maintaining high cadence (100+ RPM) during the high cadence section
- During 40/20s, aim for max power output (121-151% FTP)
- Keep recovery periods easy to ensure quality of the next interval
- Pre-workout nutrition: Ensure adequate carbohydrate intake (50-75g/hour for workouts >90min)
- Hydration: Preload with sodium and water, aim for 500-1000mg sodium/hour during workout
- If you can't hit target power during intervals, stop and recover - quality over quantity
- Mix up your position during intervals (both seated and standing)

► Warm-up:
- 15-20 min progressive warm-up from Z1 to Z2 (RPE 1-3)
- 10 min high cadence Z3 (100-120 rpm, RPE 4-5)

► Main Set (Repeat 3x):
- 2 min 40/20s (40s Max Effort, 20s Z2, RPE 2-3)
- 4 min @ Z3/Z4 (RPE 5-6)
- 2 min 40/20s (40s Max Effort, 20s Z2, RPE 2-3)
- 4 min recovery @ Z2 (RPE 2-3) - 1:1 recovery ratio

► Cool-down:
- Z2 for remaining time (typically 90 min total, RPE 2-3)""",
            "warmup_time": 1800,  # 30 minutes total warm-up
            "intervals": [],  # We're not using the intervals parameter anymore
            "cooldown_time": 1800,  # 30 minutes cool-down
            "num_sets": 3
        },
        {
            "workout_name": "Gavin Special - 4x8min",
            "description": """► Pre-activity Instructions:
- Focus on maintaining high cadence (100+ RPM) during the high cadence section
- During 40/20s, aim for max power output (121-151% FTP)
- Keep recovery periods easy to ensure quality of the next interval
- Pre-workout nutrition: Ensure adequate carbohydrate intake (50-75g/hour for workouts >90min)
- Hydration: Preload with sodium and water, aim for 500-1000mg sodium/hour during workout
- If you can't hit target power during intervals, stop and recover - quality over quantity
- Mix up your position during intervals (both seated and standing)

► Warm-up:
- 15-20 min progressive warm-up from Z1 to Z2 (RPE 1-3)
- 10 min high cadence Z3 (100-120 rpm, RPE 4-5)

► Main Set (Repeat 4x):
- 2 min 40/20s (40s Max Effort, 20s Z2, RPE 2-3)
- 4 min @ Z3/Z4 (RPE 5-6)
- 2 min 40/20s (40s Max Effort, 20s Z2, RPE 2-3)
- 4 min recovery @ Z2 (RPE 2-3) - 1:1 recovery ratio

► Cool-down:
- Z2 for remaining time (typically 90 min total, RPE 2-3)""",
            "warmup_time": 1800,  # 30 minutes total warm-up
            "intervals": [],  # We're not using the intervals parameter anymore
            "cooldown_time": 1800,  # 30 minutes cool-down
            "num_sets": 4
        }
    ]

    # Save to desktop with timestamp
    desktop_path = os.path.expanduser("~/Desktop")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Generate both workouts
    for workout in workouts:
        num_sets = workout.pop("num_sets")  # Remove num_sets from dict before passing to generate_zwo
        filename = os.path.join(desktop_path, f"{workout['workout_name'].replace(' ', '_')}_{timestamp}.zwo")
        generate_zwo(**workout, filename=filename, num_sets=num_sets)
