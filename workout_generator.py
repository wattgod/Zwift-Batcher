import os
from datetime import datetime
import re
from lxml import etree as ET

class WorkoutGenerator:
    def __init__(self, ftp=350):
        self.ftp = ftp
        # Zone definitions as percentages of FTP
        self.zones = {
            'Z1': (0, 0.55),
            'Z2': (0.56, 0.75),
            'Z3': (0.76, 0.90),
            'Z4': (0.91, 1.05),
            'Z5': (1.06, 1.20),
            'Z6': (1.20, 1.30),  # Max effort approximation
            'Z7': (1.30, 1.40)   # Max effort approximation
        }
        
    def watts_to_zone(self, watts):
        """Convert watts to training zone"""
        percentage = watts / self.ftp
        for zone, (low, high) in self.zones.items():
            if low <= percentage <= high:
                return zone
        return 'Z7' if percentage > 1.40 else 'Z1'
    
    def zone_to_ftp_percentage(self, zone, position='mid'):
        """Convert zone to FTP percentage"""
        if zone not in self.zones:
            return 0.65  # Default to Z2
        low, high = self.zones[zone]
        if position == 'low':
            return low
        elif position == 'high':
            return high
        return (low + high) / 2  # mid

    def generate_standard_warmup(self, workout_section):
        """Generate standard warmup structure"""
        # Progressive warmup from Z1 to Z3
        warmup = ET.SubElement(workout_section, "Warmup")
        warmup.set("Duration", "600")  # 10 minutes
        warmup.set("PowerLow", str(self.zone_to_ftp_percentage('Z1', 'mid')))
        warmup.set("PowerHigh", str(self.zone_to_ftp_percentage('Z3', 'low')))
        warmup.set("Cadence", "85")
        
        # Add activation efforts
        for _ in range(3):
            # 30 seconds at Z4
            activation = ET.SubElement(workout_section, "IntervalsT")
            activation.set("Repeat", "1")
            activation.set("OnDuration", "30")
            activation.set("OffDuration", "30")
            activation.set("OnPower", str(self.zone_to_ftp_percentage('Z4', 'mid')))
            activation.set("OffPower", str(self.zone_to_ftp_percentage('Z2', 'mid')))
            activation.set("Cadence", "95")
            activation.set("CadenceResting", "85")

    def format_workout_description(self, workout_name, main_set_description):
        """Format the workout description with proper structure"""
        return f"""► Pre-activity Instructions:
- Ensure proper fueling: eat 2-3 hours before or light snack 30 mins before
- Start well hydrated and plan for 1 bottle/hour minimum
- Do a proper bike fit check before starting
- Focus on smooth pedaling throughout
- Monitor breathing and form during hard efforts

► Warm-up:
- Progressive 10-minute warm-up from Z1 to Z3
- 3 x 30-second activation efforts at Z4 with 30 seconds easy between
- Keep cadence smooth and controlled

► Main Set:
{main_set_description}

► Best Practices:
- Maintain proper form throughout, especially during high-power efforts
- If power drops significantly during intervals, take extra recovery
- Keep cadence high during hard efforts unless specified otherwise
- Focus on smooth transitions between power targets
- Use recovery periods effectively to prepare for next effort"""

    def generate_workout_xml(self, workout_name, description):
        """Generate the workout XML structure"""
        # Create root element with proper namespace
        NSMAP = {None: "http://www.zwift.com"}
        workout = ET.Element("{http://www.zwift.com}workout_file", nsmap=NSMAP)
        
        # Add metadata
        author = ET.SubElement(workout, "author")
        author.text = "Gravel God Cycling"
        
        name = ET.SubElement(workout, "name")
        name.text = workout_name
        
        desc = ET.SubElement(workout, "description")
        desc.text = description
        
        sport = ET.SubElement(workout, "sportType")
        sport.text = "bike"
        
        ET.SubElement(workout, "tags")
        
        # Create workout section
        workout_section = ET.SubElement(workout, "workout")
        
        # Add standard warmup
        self.generate_standard_warmup(workout_section)
        
        # Add steady state Z3 block
        steady = ET.SubElement(workout_section, "SteadyState")
        steady.set("Duration", "600")  # 10 minutes
        steady.set("Power", str(self.zone_to_ftp_percentage('Z3', 'low')))
        steady.set("Cadence", "95")
        
        # Add recovery before intervals
        recovery = ET.SubElement(workout_section, "SteadyState")
        recovery.set("Duration", "180")  # 3 minutes
        recovery.set("Power", str(self.zone_to_ftp_percentage('Z2', 'low')))
        recovery.set("Cadence", "85")
        
        # Add 3 sets of intervals with full recovery
        for _ in range(3):
            # 5 x 30/30 intervals
            intervals = ET.SubElement(workout_section, "IntervalsT")
            intervals.set("Repeat", "5")
            intervals.set("OnDuration", "30")
            intervals.set("OffDuration", "30")
            intervals.set("OnPower", str(self.zone_to_ftp_percentage('Z6', 'low')))  # ~420W
            intervals.set("OffPower", str(self.zone_to_ftp_percentage('Z3', 'low')))  # ~300W
            intervals.set("Cadence", "95")
            intervals.set("CadenceResting", "90")
            
            # Full recovery between sets (if not last set)
            if _ < 2:
                recovery = ET.SubElement(workout_section, "SteadyState")
                recovery.set("Duration", "300")  # 5 minutes
                recovery.set("Power", str(self.zone_to_ftp_percentage('Z2', 'low')))
                recovery.set("Cadence", "85")
        
        # Add cooldown
        cooldown = ET.SubElement(workout_section, "Cooldown")
        cooldown.set("Duration", "600")
        cooldown.set("PowerLow", str(self.zone_to_ftp_percentage('Z2', 'mid')))
        cooldown.set("PowerHigh", str(self.zone_to_ftp_percentage('Z1', 'mid')))
        cooldown.set("Cadence", "85")
        
        return workout

def save_workout(workout_name, main_set_description, ftp=350):
    """Save the workout to a file"""
    generator = WorkoutGenerator(ftp)
    
    # Generate full description
    full_description = generator.format_workout_description(workout_name, main_set_description)
    
    # Generate workout XML
    workout = generator.generate_workout_xml(workout_name, full_description)
    
    # Convert to string
    xml_str = ET.tostring(workout, encoding='UTF-8', xml_declaration=True, pretty_print=True).decode('utf-8')
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{workout_name.replace(' ', '_')}_{timestamp}.zwo"
    
    # Save to Downloads folder
    downloads_dir = os.path.expanduser("~/Downloads")
    filepath = os.path.join(downloads_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write(xml_str)
    
    return filepath

# Example usage
if __name__ == "__main__":
    workout_description = """10 minutes low Z3 (RPE 4-5), 95+ rpm

3 sets of:
- 5 x 30 seconds Max Effort (RPE 9-10)
- 30 seconds Z3 (RPE 4-5)
- 5 minutes full recovery between sets

Total Time: ~60-90 minutes including warm-up and cool-down"""

    filepath = save_workout("VO2_Max_Intervals", workout_description)
    print(f"Workout saved to: {filepath}") 