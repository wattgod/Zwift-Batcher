import xml.etree.ElementTree as ET
import os
from datetime import datetime
import json
from typing import List, Dict

class WorkoutGenerator:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.expanduser("~/Desktop")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Define zone boundaries based on FTP percentages
        self.zones = {
            "Z1": (0, 0.55),
            "Z2": (0.56, 0.75),
            "Z3": (0.76, 0.90),
            "Z4": (0.91, 1.05),
            "Z5": (1.06, 1.20),
            "Z6": "Max Effort",
            "Z7": "Max Effort"
        }
        
        # Define RPE scale
        self.rpe_scale = {
            "Z1": "1-2",
            "Z2": "2-3",
            "Z3": "4-5",
            "Z4": "6-7",
            "Z5": "8-9",
            "Z6": "9-10",
            "Z7": "10"
        }

    def power_to_zone(self, power_decimal: float) -> str:
        """Convert power as decimal of FTP to appropriate zone."""
        for zone, (lower, upper) in self.zones.items():
            if isinstance(lower, (int, float)) and isinstance(upper, (int, float)):
                if lower <= power_decimal <= upper:
                    return f"{zone}, RPE {self.rpe_scale[zone]}"
        if power_decimal > 1.20:
            return f"Max Effort, RPE {self.rpe_scale['Z6']}"
        return "Z1, RPE 1-2"  # Default fallback

    def generate_workout(self, workout_data: Dict) -> str:
        """Generate a single workout file and return the filename."""
        # Create the root element
        workout = ET.Element("workout_file")

        # Add required elements in correct order
        ET.SubElement(workout, "author").text = "Gravel God Cycling"
        ET.SubElement(workout, "name").text = workout_data["workout_name"]
        
        # Standard pre-activity instructions
        standard_instructions = """► Pre-activity Instructions:
- Ensure adequate carbohydrate intake (50-75g/hour for workouts >90min)
- Hydration: Preload with sodium and water (500-1000mg sodium/hour)
- Quality over quantity - if you can't hit target power, stop and recover
- Mix up your position during intervals (seated and standing)
- Remember: Training makes you slow, sleep makes you fast
- Avoid the moral licensing effect - good training doesn't excuse poor recovery

► Warm-up:
- 15-20 min progressive warm-up from Z1 to Z2 (RPE 1-3)
- 10 min high cadence Z3 (100-120 rpm, RPE 4-5)

"""
        
        # Combine standard instructions with workout-specific description
        full_description = standard_instructions + workout_data["description"]
        
        # Add description with proper CDATA formatting
        desc = ET.SubElement(workout, "description")
        desc.text = full_description
        
        sport_type = ET.SubElement(workout, "sportType")
        sport_type.text = "bike"
        
        # Empty tags element
        ET.SubElement(workout, "tags")

        # Create workout section
        workout_section = ET.SubElement(workout, "workout")

        # Add workout sections based on the structure
        for section in workout_data.get("sections", []):
            if section["type"] == "Warmup":
                ET.SubElement(workout_section, "Warmup", 
                            Duration=str(section["duration"]), 
                            PowerLow=str(section["power_low"]), 
                            PowerHigh=str(section["power_high"]))
            elif section["type"] == "Cooldown":
                ET.SubElement(workout_section, "Cooldown", 
                            Duration=str(section["duration"]), 
                            PowerLow=str(section["power_low"]), 
                            PowerHigh=str(section["power_high"]))
            elif section["type"] == "Intervals":
                for _ in range(section["repeats"]):
                    ET.SubElement(workout_section, "SteadyState", 
                                Duration=str(section["on_duration"]), 
                                Power=str(section["on_power"]))
                    ET.SubElement(workout_section, "SteadyState", 
                                Duration=str(section["off_duration"]), 
                                Power=str(section["off_power"]))
            elif section["type"] == "Tempo":
                for _ in range(section["repeats"]):
                    ET.SubElement(workout_section, "SteadyState", 
                                Duration=str(section["duration"]), 
                                Power=str(section["power"]))
                    if section.get("recovery_duration"):
                        ET.SubElement(workout_section, "SteadyState", 
                                    Duration=str(section["recovery_duration"]), 
                                    Power=str(section["recovery_power"]))

        # Convert XML to a formatted string
        tree = ET.ElementTree(workout)
        ET.indent(tree, space="\t")

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, 
                              f"{workout_data['workout_name'].replace(' ', '_')}_{timestamp}.zwo")

        # Save to file with proper XML declaration and CDATA
        with open(filename, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            xml_str = ET.tostring(workout, encoding='unicode')
            xml_str = xml_str.replace('<description>', '<description><![CDATA[')
            xml_str = xml_str.replace('</description>', ']]></description>')
            f.write(xml_str.encode('utf-8'))

        return filename

    def batch_generate(self, workout_descriptions: List[Dict]) -> List[str]:
        """Generate multiple workout files from a list of descriptions."""
        generated_files = []
        for workout_data in workout_descriptions:
            try:
                filename = self.generate_workout(workout_data)
                generated_files.append(filename)
                print(f"Generated: {filename}")
            except Exception as e:
                print(f"Error generating {workout_data.get('workout_name', 'Unknown')}: {str(e)}")
        return generated_files

def process_workout_descriptions(descriptions_file: str, output_dir: str = None) -> List[str]:
    """Process workout descriptions from a JSON file."""
    with open(descriptions_file, 'r') as f:
        workout_descriptions = json.load(f)
    
    generator = WorkoutGenerator(output_dir)
    return generator.batch_generate(workout_descriptions)

if __name__ == "__main__":
    # Example usage for the workout you described
    example_workouts = [
        {
            "workout_name": "High-Intensity Power Blocks",
            "description": """► Pre-activity Instructions:
- This is a high-intensity session - ensure you are well rested
- Avoid any hard training 48 hours before this session
- Pre-workout nutrition: Light meal 2-3 hours before (low fat, moderate protein, high carb)
- Hydration: Start hydrating 24 hours before, aim for clear urine pre-workout
- Mental preparation: This workout requires focus - find a quiet space
- Have nutrition ready: You'll need quick energy between sets
- If power drops >10% during intervals, end the session
- Recovery is crucial after this type of session - plan accordingly

► Warm-up:
- 15-20 min progressive warm-up from Z1 to Z2 (RPE 1-3)
- 10 min high cadence Z3 (100-120 rpm, RPE 4-5)
- 3 x 30s building efforts (Z3→Z4→Z5) with 30s easy between

► Main Set (4 x 8min blocks):
- Each block consists of:
  • First 2 minutes: 4 x (30s Max Effort / 30s Z2)
    - Max Effort: Z6 (RPE 9-10)
    - Recovery: Z2 (RPE 2-3)
    - Focus: Explosive power, high cadence (100+ rpm)
  • Middle 4 minutes: Threshold
    - Hold Z4 (RPE 6-7)
    - Focus: Smooth pedaling, controlled breathing
  • Final 2 minutes: 4 x (30s Max Effort / 30s Z2)
    - Max Effort: Z6 (RPE 9-10)
    - Recovery: Z2 (RPE 2-3)
    - Focus: Maintain form despite fatigue
- Recovery between blocks:
  • 6-8 minutes Z2 (RPE 2-3)
  • Focus on complete recovery before next block
  • Hydrate and fuel during this time

► Cool-down:
- 10-15 minutes Z1-Z2 (RPE 1-3)
- Keep cadence high but power very light
- Focus on controlled breathing

► Post-workout:
- Immediate: 30g fast-acting carbs + 20g protein
- Within 2 hours: Full recovery meal
- Mobility work: Focus on hip flexors and lower back
- Plan for 8-9 hours sleep tonight
- No high-intensity work for 48-72 hours
- Monitor HRV for next 2-3 days""",
            "sections": [
                {
                    "type": "Warmup",
                    "duration": 1800,  # 30 minutes
                    "power_low": 0.56,  # Z1
                    "power_high": 0.75  # Z2
                },
                # Warm-up primers
                {
                    "type": "Intervals",
                    "repeats": 3,
                    "on_duration": 30,
                    "on_power": 1.15,  # Z5
                    "off_duration": 30,
                    "off_power": 0.65  # Z2
                },
                # First block example (others would be repeated similarly)
                # 2 minutes of 30/30s
                {
                    "type": "Intervals",
                    "repeats": 4,
                    "on_duration": 30,
                    "on_power": 1.5,  # Z6/Max Effort
                    "off_duration": 30,
                    "off_power": 0.65  # Z2
                },
                # 4 minutes threshold
                {
                    "type": "SteadyState",
                    "duration": 240,
                    "power": 1.0  # Z4
                },
                # 2 minutes of 30/30s
                {
                    "type": "Intervals",
                    "repeats": 4,
                    "on_duration": 30,
                    "on_power": 1.5,  # Z6/Max Effort
                    "off_duration": 30,
                    "off_power": 0.65  # Z2
                },
                # Recovery between blocks
                {
                    "type": "SteadyState",
                    "duration": 420,  # 7 minutes
                    "power": 0.65  # Z2
                },
                # Cooldown
                {
                    "type": "Cooldown",
                    "duration": 900,  # 15 minutes
                    "power_low": 0.56,  # Z1
                    "power_high": 0.75  # Z2
                }
            ]
        }
    ]

    # Save example workouts to a JSON file
    with open('example_workouts.json', 'w') as f:
        json.dump(example_workouts, f, indent=2)

    # Process the workouts
    generator = WorkoutGenerator()
    generated_files = generator.batch_generate(example_workouts)
    print(f"\nGenerated {len(generated_files)} workout files") 