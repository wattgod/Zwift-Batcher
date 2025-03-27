import os
from datetime import datetime
import re
from lxml import etree as ET

def parse_power_zone(text):
    """Convert zone notation to FTP percentages."""
    text = text.lower()
    if 'max' in text:
        return 1.2  # 120% FTP
    if 'z1' in text:
        return 0.5  # 50% FTP
    elif 'z2' in text:
        return 0.65  # 65% FTP
    elif 'z3' in text:
        return 0.83  # 83% FTP
    elif 'z4' in text:
        return 0.98  # 98% FTP
    elif 'z5' in text:
        return 1.13  # 113% FTP
    elif 'z6' in text:
        return 1.2  # 120% FTP
    return 0.65  # Default to Z2

def parse_duration(text):
    """Convert duration notation (e.g., '30"' or '5'') to seconds."""
    if '"' in text:  # Seconds
        return int(re.search(r'(\d+)"', text).group(1))
    elif "'" in text:  # Minutes
        return int(re.search(r"(\d+)'", text).group(1)) * 60
    return 300  # Default 5 minutes

def parse_cadence(text):
    """Extract cadence information."""
    # Look for explicit cadence ranges
    cadence_match = re.search(r'(\d+)-(\d+)r', text)
    if cadence_match:
        low = int(cadence_match.group(1))
        high = int(cadence_match.group(2))
        return (low + high) // 2
    
    # Default cadences based on type
    if 'sfr' in text.lower():
        return 55  # SFR default
    elif 'max' in text.lower():
        return 90  # Max effort default
    return 85  # General default

def parse_block(text):
    """Parse a block of workout text into structured data."""
    blocks = []
    
    # Split into lines and process each
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    current_block = None
    for line in lines:
        # Remove leading dash if present
        line = line.lstrip('-')
        
        # New block starts with numbers or specific keywords
        if re.match(r'^\d+x|^\d+\'|^\d+"', line) or 'base' in line.lower():
            if current_block:
                blocks.append(current_block)
            current_block = {'text': line, 'subsets': []}
        elif current_block:
            current_block['subsets'].append(line)
    
    if current_block:
        blocks.append(current_block)
    
    return blocks

def generate_workout_xml(workout_name, description):
    """Generate the workout XML structure."""
    # Create root element with proper namespace
    NSMAP = {None: "http://www.zwift.com"}
    workout = ET.Element("{http://www.zwift.com}workout_file", nsmap=NSMAP)
    
    # Add metadata
    author = ET.SubElement(workout, "author")
    author.text = "Gravel God Cycling"
    
    name = ET.SubElement(workout, "name")
    name.text = workout_name
    
    desc = ET.SubElement(workout, "description")
    desc.text = ET.CDATA(description)
    
    sport = ET.SubElement(workout, "sportType")
    sport.text = "bike"
    
    ET.SubElement(workout, "tags")
    
    # Create workout section
    workout_section = ET.SubElement(workout, "workout")
    
    # Parse the description into blocks
    blocks = parse_block(description)
    
    # Process each block
    for block in blocks:
        text = block['text'].lower()
        
        # Handle base/warmup
        if 'base' in text or 'z1-z2' in text:
            warmup = ET.SubElement(workout_section, "Warmup")
            warmup.set("Duration", "600")
            warmup.set("PowerLow", "0.5")
            warmup.set("PowerHigh", "0.65")
            warmup.set("Cadence", "85")
            continue
        
        # Handle interval sets
        sets_match = re.search(r'(\d+)x', text)
        if sets_match:
            sets = int(sets_match.group(1))
            
            for set_num in range(sets):
                # First, add the 30/30 intervals
                intervals = ET.SubElement(workout_section, "IntervalsT")
                intervals.set("Repeat", "5")
                intervals.set("OnDuration", "30")
                intervals.set("OffDuration", "30")
                intervals.set("OnPower", "1.2")
                intervals.set("OffPower", "0.65")
                intervals.set("Cadence", "90")
                
                # Then add the SFR block
                sfr = ET.SubElement(workout_section, "SteadyState")
                sfr.set("Duration", "240")
                sfr.set("Power", "0.83")
                sfr.set("Cadence", "55")
                
                # Add recovery between sets if not the last set
                if set_num < sets - 1:
                    recovery_match = re.search(r"(\d+)'\s*recovery", text)
                    if recovery_match:
                        recovery_time = int(recovery_match.group(1)) * 60
                        recovery = ET.SubElement(workout_section, "SteadyState")
                        recovery.set("Duration", str(recovery_time))
                        recovery.set("Power", "0.65")
                        recovery.set("Cadence", "85")
        
        # Handle steady state blocks
        elif re.search(r'\d+\'.*z3', text) or re.search(r'\d+\'.*hr', text):
            duration_match = re.search(r'(\d+)\'', text)
            if duration_match:
                duration = int(duration_match.group(1)) * 60
                steady = ET.SubElement(workout_section, "SteadyState")
                steady.set("Duration", str(duration))
                steady.set("Power", "0.83")
                steady.set("Cadence", "90")
    
    # Add cooldown
    cooldown = ET.SubElement(workout_section, "Cooldown")
    cooldown.set("Duration", "600")
    cooldown.set("PowerLow", "0.65")
    cooldown.set("PowerHigh", "0.5")
    cooldown.set("Cadence", "85")
    
    return workout

def format_workout_description(workout_name, description):
    """Format the workout description with pre-activity instructions and structure."""
    return f"""► Pre-activity Instructions:
- Ensure proper fueling: eat 2-3 hours before or a light snack 30 mins before
- Hydration: Start well hydrated and plan for 1 bottle/hour
- For SFR (Slow Frequency Repetitions): Focus on smooth pedaling at low cadence
- During max efforts: Aim for max sustainable power while maintaining form
- Recovery periods are crucial - keep them easy to ensure quality intervals

► Workout Structure:
{description}

► Best Practices:
- Maintain proper form throughout, especially during SFR
- If power drops significantly during intervals, end the set early
- Keep cadence high (85-95) during regular intervals, low (50-60) during SFR
- Stay seated during SFR unless specified otherwise
- Monitor heart rate during Z3 blocks to stay in target zone"""

def save_workout(workout_name, description):
    """Save the workout to a .zwo file."""
    # Generate the XML
    workout = generate_workout_xml(workout_name, format_workout_description(workout_name, description))
    
    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{workout_name.replace(' ', '_')}_{timestamp}.zwo"
    filepath = os.path.join(os.path.expanduser("~/Downloads"), filename)
    
    # Convert to string and fix the name tag
    xml_str = ET.tostring(workout, encoding='UTF-8', xml_declaration=True, pretty_print=True).decode('utf-8')
    xml_str = xml_str.replace('<n>', '<name>').replace('</n>', '</name>')
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(xml_str)
    
    return filepath

# Test the generator
if __name__ == "__main__":
    test_workout = """Z1-Z2 base with focus on efforts as follows:

-6x5' / 3' recovery done as...
30" max / 30" easy
4' SFR (50-60r, 300-330w)

-1 x 20' Z3 HR (150-160bpm), mostly 85+ rpm"""

    filepath = save_workout("SFR_Intervals", test_workout)
    print(f"Workout saved to: {filepath}") 