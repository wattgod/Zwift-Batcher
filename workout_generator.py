import os
from datetime import datetime
from lxml import etree as ET

def create_workout_file(name, description, segments):
    """Create a Zwift workout file with the given segments."""
    # Create root element
    NSMAP = {None: "http://www.zwift.com"}
    workout = ET.Element("{http://www.zwift.com}workout_file", nsmap=NSMAP)
    
    # Add metadata
    author = ET.SubElement(workout, "author")
    author.text = "Gravel God Cycling"
    
    name_elem = ET.SubElement(workout, "name")
    name_elem.text = name
    
    desc = ET.SubElement(workout, "description")
    desc.text = description
    
    sport = ET.SubElement(workout, "sportType")
    sport.text = "bike"
    
    ET.SubElement(workout, "tags")
    
    # Create workout section
    workout_section = ET.SubElement(workout, "workout")
    
    # Add all segments
    for segment in segments:
        segment_type = segment["type"]
        element = ET.SubElement(workout_section, segment_type)
        for key, value in segment["attributes"].items():
            element.set(key, str(value))
    
    return workout

def save_workout(name, description, segments):
    """Save the workout to a .zwo file."""
    workout = create_workout_file(name, description, segments)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name.replace(' ', '_')}_{timestamp}.zwo"
    filepath = os.path.join(os.path.expanduser("~/Downloads"), filename)
    
    # Convert to string and save
    xml_str = ET.tostring(workout, encoding='UTF-8', xml_declaration=True, pretty_print=True).decode('utf-8')
    with open(filepath, 'w') as f:
        f.write(xml_str)
    
    return filepath

# Example usage
if __name__ == "__main__":
    # Workout description
    description = """60-90 min total ride time with efforts:

10 min low Z3 (280-300w), 95+ rpm

3 sets of 5x30 sec ~420w / 30 sec ~300w; full recovery between."""

    # Define workout segments
    segments = [
        # Warmup
        {
            "type": "Warmup",
            "attributes": {
                "Duration": "600",  # 10 min
                "PowerLow": "0.50",  # 50% FTP
                "PowerHigh": "0.75",  # 75% FTP
                "Cadence": "85"
            }
        },
        # 10 min Z3 block
        {
            "type": "SteadyState",
            "attributes": {
                "Duration": "600",  # 10 min
                "Power": "0.80",    # Low Z3 (~280-300W for 350 FTP)
                "Cadence": "95"
            }
        },
        # Recovery before intervals
        {
            "type": "SteadyState",
            "attributes": {
                "Duration": "180",  # 3 min
                "Power": "0.65",    # Recovery
                "Cadence": "85"
            }
        }
    ]

    # Add 3 sets of intervals with recovery
    for i in range(3):
        # 5x30/30 intervals
        segments.append({
            "type": "IntervalsT",
            "attributes": {
                "Repeat": "5",
                "OnDuration": "30",
                "OffDuration": "30",
                "OnPower": "1.20",    # ~420W
                "OffPower": "0.85",    # ~300W
                "Cadence": "95",
                "CadenceResting": "90"
            }
        })
        
        # Add recovery between sets (except after last set)
        if i < 2:
            segments.append({
                "type": "SteadyState",
                "attributes": {
                    "Duration": "300",  # 5 min
                    "Power": "0.65",    # Recovery
                    "Cadence": "85"
                }
            })

    # Cooldown
    segments.append({
        "type": "Cooldown",
        "attributes": {
            "Duration": "600",  # 10 min
            "PowerLow": "0.75",
            "PowerHigh": "0.50",
            "Cadence": "85"
        }
    })

    # Save the workout
    filepath = save_workout("High_Intensity_Intervals", description, segments)
    print(f"Workout saved to: {filepath}") 