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
        
        # Handle surges within steady state
        if 'surge' in text and 'every' in text:
            # Extract base duration and surge pattern
            base_duration = int(re.search(r'(\d+)\'', text).group(1)) * 60  # Total duration in seconds
            surge_duration = int(re.search(r'(\d+)"', text).group(1))  # Surge duration in seconds
            interval_duration = int(re.search(r'every\s*(\d+)\'', text).group(1)) * 60  # Time between surges
            
            # Calculate number of surges
            num_intervals = base_duration // interval_duration
            
            for _ in range(num_intervals):
                # Base interval before surge
                steady = ET.SubElement(workout_section, "SteadyState")
                steady.set("Duration", str(interval_duration - surge_duration))
                steady.set("Power", "0.83")  # Z3
                steady.set("Cadence", "90")
                
                # Surge
                surge = ET.SubElement(workout_section, "SteadyState")
                surge.set("Duration", str(surge_duration))
                surge.set("Power", "1.13")  # Z5
                surge.set("Cadence", "95")
            
            # Add any remaining time at base power
            remaining_time = base_duration % interval_duration
            if remaining_time > 0:
                steady = ET.SubElement(workout_section, "SteadyState")
                steady.set("Duration", str(remaining_time))
                steady.set("Power", "0.83")  # Z3
                steady.set("Cadence", "90")
        
        # Handle VO2 max efforts
        elif 'vo2' in text or 'near max' in text:
            duration = int(re.search(r'(\d+)\'', text).group(1)) * 60
            vo2 = ET.SubElement(workout_section, "SteadyState")
            vo2.set("Duration", str(duration))
            vo2.set("Power", "1.15")  # Just above Z5
            vo2.set("Cadence", "95")
        
        # Handle alternating intervals
        elif 'x' in text and 'alt' in ' '.join(block['subsets']).lower():
            sets_match = re.search(r'(\d+)x(\d+)', text)
            if sets_match:
                sets = int(sets_match.group(1))
                duration = int(sets_match.group(2)) * 60  # Convert to seconds
                
                for _ in range(sets):
                    # Create alternating 30/30 intervals
                    intervals = ET.SubElement(workout_section, "IntervalsT")
                    intervals.set("Repeat", str(duration // 60))  # Number of repeats for the block
                    intervals.set("OnDuration", "30")
                    intervals.set("OffDuration", "30")
                    intervals.set("OnPower", "1.2")  # Max
                    intervals.set("OffPower", "0.75")  # Z2-Z3
                    intervals.set("Cadence", "90")
                    
                    # Add recovery between sets if not the last set
                    if _ < sets - 1:
                        recovery = ET.SubElement(workout_section, "SteadyState")
                        recovery.set("Duration", "180")  # 3 minutes recovery
                        recovery.set("Power", "0.65")
                        recovery.set("Cadence", "85")
        
        # Handle other steady state blocks
        elif re.search(r'\d+\'.*z[3-6]', text):
            duration_match = re.search(r'(\d+)\'', text)
            if duration_match:
                duration = int(duration_match.group(1)) * 60
                power = parse_power_zone(text)
                steady = ET.SubElement(workout_section, "SteadyState")
                steady.set("Duration", str(duration))
                steady.set("Power", str(power))
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
- For surges: Focus on smooth power transitions
- During max efforts: Maintain form even as fatigue sets in
- Recovery periods are crucial - keep them easy to ensure quality intervals

► Workout Structure:
{description}

► Best Practices:
- Maintain proper form throughout, especially during high-power efforts
- If power drops significantly during intervals, take extra recovery
- Keep cadence high (90-95) during surges and max efforts
- Focus on smooth transitions between power targets
- Use recovery periods effectively to prepare for next effort"""

def save_workout(workout_name, description):
    """Save the workout to a file."""
    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<workout_file xmlns="http://www.zwift.com">
    <author>Gravel God Cycling</author>
    <name>{workout_name}</name>
    <description><![CDATA[{format_workout_description(workout_name, description)}]]></description>
    <sportType>bike</sportType>
    <tags/>
    <workout>
'''
    
    # Parse the description line by line
    lines = [line.strip() for line in description.split('\n') if line.strip()]
    
    # Add warmup
    if any('z1-z2' in line.lower() for line in lines):
        xml_content += '''        <Warmup Duration="600" PowerLow="0.5" PowerHigh="0.65" Cadence="85"/>
'''
    
    # Process each line for workout elements
    current_block = None
    block_subsets = []
    first_effort = True
    
    for line in lines:
        line = line.strip().lower()
        if not line or line.startswith('z1-z2'):
            continue
            
        # Remove leading dash if present
        line = line.lstrip('-')
        
        # Check if this is a new block header
        if line.endswith('...'):
            current_block = line[:-3].strip()  # Store the block header without '...'
            block_subsets = []
            continue
            
        # If we're collecting subsets for a block
        if current_block:
            if line.startswith('-') or line.startswith('30"'):
                block_subsets.append(line.lstrip('- '))
            continue
        
        # Handle Z3 with surges
        if 'z3' in line and 'surge' in line:
            if not first_effort:
                xml_content += '''        <SteadyState Duration="180" Power="0.65" Cadence="85"/>
'''
            
            base_time = int(re.search(r'(\d+)\'', line).group(1)) * 60
            surge_duration = int(re.search(r'(\d+)"', line).group(1))
            interval_period = int(re.search(r'every\s*(\d+)\'', line).group(1)) * 60
            
            num_intervals = base_time // interval_period
            
            for _ in range(num_intervals):
                xml_content += f'''        <SteadyState Duration="{interval_period - surge_duration}" Power="0.83" Cadence="90"/>
        <SteadyState Duration="{surge_duration}" Power="1.15" Cadence="95"/>
'''
            
            remaining_time = base_time % interval_period
            if remaining_time > 0:
                xml_content += f'''        <SteadyState Duration="{remaining_time}" Power="0.83" Cadence="90"/>
'''
            first_effort = False
                
        # Handle Z6 (near max) effort
        elif 'z6' in line or 'near max' in line:
            if not first_effort:
                xml_content += '''        <SteadyState Duration="180" Power="0.65" Cadence="85"/>
'''
            
            duration = int(re.search(r'(\d+)\'', line).group(1)) * 60
            xml_content += f'''        <SteadyState Duration="{duration}" Power="1.2" Cadence="95"/>
'''
            first_effort = False
        
        # Handle alternating intervals directly in the line
        elif 'x' in line and not current_block:
            if not first_effort:
                xml_content += '''        <SteadyState Duration="180" Power="0.65" Cadence="85"/>
'''
            
            sets_match = re.search(r'(\d+)x(\d+)', line)
            if sets_match:
                sets = int(sets_match.group(1))
                duration = int(sets_match.group(2)) * 60
                repeats = duration // 60
                
                for set_num in range(sets):
                    xml_content += f'''        <IntervalsT Repeat="{repeats}" OnDuration="30" OffDuration="30" OnPower="1.2" OffPower="0.75" Cadence="90"/>
'''
                    if set_num < sets - 1:
                        xml_content += '''        <SteadyState Duration="180" Power="0.65" Cadence="85"/>
'''
            first_effort = False
    
    # Process any remaining block
    if current_block and block_subsets:
        if not first_effort:
            xml_content += '''        <SteadyState Duration="180" Power="0.65" Cadence="85"/>
'''
        
        # Handle 2x10' with 30/30 intervals
        if 'x' in current_block:
            sets_match = re.search(r'(\d+)x(\d+)', current_block)
            if sets_match:
                sets = int(sets_match.group(1))
                duration = int(sets_match.group(2)) * 60
                repeats = duration // 60
                
                for set_num in range(sets):
                    xml_content += f'''        <IntervalsT Repeat="{repeats}" OnDuration="30" OffDuration="30" OnPower="1.2" OffPower="0.75" Cadence="90"/>
'''
                    if set_num < sets - 1:
                        xml_content += '''        <SteadyState Duration="180" Power="0.65" Cadence="85"/>
'''
    
    # Add cooldown
    xml_content += '''        <Cooldown Duration="600" PowerLow="0.65" PowerHigh="0.5" Cadence="85"/>
    </workout>
</workout_file>'''
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{workout_name.replace(' ', '_')}_{timestamp}.zwo"
    
    # Save to Downloads folder
    downloads_dir = os.path.expanduser("~/Downloads")
    filepath = os.path.join(downloads_dir, filename)
    
    with open(filepath, 'w') as f:
        f.write(xml_content)
    
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