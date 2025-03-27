import xml.etree.ElementTree as ET
import os
from datetime import datetime

def generate_bookend_zwo(workout_name, description, filename):
    # Create the root element
    workout = ET.Element("workout_file")

    # Add required elements in correct order
    ET.SubElement(workout, "author").text = "Gravel God Cycling"
    ET.SubElement(workout, "name").text = workout_name
    
    # Add description with proper CDATA formatting
    desc = ET.SubElement(workout, "description")
    desc.text = description
    
    sport_type = ET.SubElement(workout, "sportType")
    sport_type.text = "bike"
    
    # Empty tags element
    ET.SubElement(workout, "tags")

    # Create workout section
    workout_section = ET.SubElement(workout, "workout")

    # Warm-up (30 min)
    ET.SubElement(workout_section, "Warmup", 
                  Duration="1800", 
                  PowerLow="0.56", PowerHigh="0.75")

    # Set 1 - First 1.5 hours
    # First 6-min block
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.5")  # Z6, Max Effort
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.15")  # Z5
    ET.SubElement(workout_section, "SteadyState", Duration="120", Power="1.0")  # Z4
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.15")  # Z5
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.5")  # Z6, Max Effort
    
    # 8 min Z2 recovery
    ET.SubElement(workout_section, "SteadyState", Duration="480", Power="0.65")
    
    # Second 6-min block
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.5")  # Z6, Max Effort
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.15")  # Z5
    ET.SubElement(workout_section, "SteadyState", Duration="120", Power="1.0")  # Z4
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.15")  # Z5
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.5")  # Z6, Max Effort

    # Middle section - 2 hours of Z1-3
    ET.SubElement(workout_section, "SteadyState", Duration="7200", Power="0.65")  # Z2

    # Set 2 - Final 90 minutes
    # First 6-min block
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.5")  # Z6, Max Effort
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.15")  # Z5
    ET.SubElement(workout_section, "SteadyState", Duration="120", Power="1.0")  # Z4
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.15")  # Z5
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.5")  # Z6, Max Effort
    
    # 8 min Z2 recovery
    ET.SubElement(workout_section, "SteadyState", Duration="480", Power="0.65")
    
    # Second 6-min block
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.5")  # Z6, Max Effort
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.15")  # Z5
    ET.SubElement(workout_section, "SteadyState", Duration="120", Power="1.0")  # Z4
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.15")  # Z5
    ET.SubElement(workout_section, "SteadyState", Duration="60", Power="1.5")  # Z6, Max Effort

    # Cool-down (30 min)
    ET.SubElement(workout_section, "Cooldown", 
                  Duration="1800", 
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
    workout_data = {
        "workout_name": "Bookend Power Intervals",
        "description": """► Pre-activity Instructions:
- This is a bookend ride designed to build fatigue resistance and fueling ability
- Pre-workout nutrition is crucial - ensure adequate carbohydrate intake (50-75g/hour)
- Hydration: Preload with sodium and water, aim for 500-1000mg sodium/hour
- The middle section should be done on hilly terrain - accumulate tempo on feel
- All intervals should be done on climbs for proper resistance
- If you can't hit target power during intervals, stop and recover - quality over quantity
- Mix up your position during intervals (both seated and standing)
- Remember: Training makes you slow, sleep makes you fast
- Avoid the moral licensing effect - good training doesn't excuse poor recovery choices

► Warm-up:
- 15-20 min progressive warm-up from Z1 to Z2 (RPE 1-3)
- 10 min high cadence Z3 (100-120 rpm, RPE 4-5)

► Set 1 (First 1.5 hours):
- 2 x 6 min blocks with 8 min Z2 recovery between
- Each 6 min block:
  * 1 min @ Z6, Max Effort (RPE 9-10)
  * 1 min @ Z5 (RPE 8-9)
  * 2 min @ Z4 (RPE 7-8)
  * 1 min @ Z5 (RPE 8-9)
  * 1 min @ Z6, Max Effort (RPE 9-10)
- Recovery: 8 min @ Z2 (RPE 2-3)

► Middle Section (2 hours):
- Z1-3 on hilly terrain (RPE 1-5)
- Accumulate tempo on feel
- Focus on proper fueling and hydration
- Keep cadence high (90-100 rpm)
- Mix up positions on climbs

► Set 2 (Final 90 minutes):
- 2 x 6 min blocks with 8 min Z2 recovery between
- Each 6 min block:
  * 1 min @ Z6, Max Effort (RPE 9-10)
  * 1 min @ Z5 (RPE 8-9)
  * 2 min @ Z4 (RPE 7-8)
  * 1 min @ Z5 (RPE 8-9)
  * 1 min @ Z6, Max Effort (RPE 9-10)
- Recovery: 8 min @ Z2 (RPE 2-3)

► Cool-down:
- 30 min Z1-2 (RPE 1-3)
- Focus on high cadence (90-100 rpm)

► Post-workout:
- Clean your bike (chain, drivetrain, frame)
- Do 10 minutes of mobility work
- Refuel with adequate carbohydrates and protein
- Log your workout notes in TrainingPeaks
- Get to bed early for optimal recovery""",
    }

    # Save to desktop with timestamp
    desktop_path = os.path.expanduser("~/Desktop")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(desktop_path, f"Bookend_Power_Intervals_{timestamp}.zwo")
    
    # Generate the workout
    generate_bookend_zwo(**workout_data, filename=filename) 