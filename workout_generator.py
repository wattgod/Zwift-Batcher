import os
from datetime import datetime
import re
from lxml import etree as ET

def format_workout_description(workout_name, description):
    """Format the workout description with pre-activity instructions and structure."""
    return f"""► Pre-activity Instructions:
- Ensure proper fueling: eat 2-3 hours before or a light snack 30 mins before
- Hydration: Start well hydrated and plan for 1 bottle/hour
- For surges: Focus on smooth power transitions
- During VO2/max efforts: Maintain form even as fatigue sets in
- Recovery periods are crucial - keep them easy to ensure quality intervals

► Workout Structure:
{description}

► Best Practices:
- Maintain proper form throughout, especially during high-power efforts
- If power drops significantly during intervals, take extra recovery
- Keep cadence high (90-95) during surges and VO2 efforts
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
        <Warmup Duration="10:00" PowerLow="0.5" PowerHigh="0.65" Cadence="85"/>
        <SteadyState Duration="10:00" Power="0.80" Cadence="95"/>
        <SteadyState Duration="3:00" Power="0.65" Cadence="85"/>
        <IntervalsT Repeat="5" OnDuration="0:30" OffDuration="0:30" OnPower="1.2" OffPower="0.85" Cadence="90"/>
        <SteadyState Duration="5:00" Power="0.65" Cadence="85"/>
        <IntervalsT Repeat="5" OnDuration="0:30" OffDuration="0:30" OnPower="1.2" OffPower="0.85" Cadence="90"/>
        <SteadyState Duration="5:00" Power="0.65" Cadence="85"/>
        <IntervalsT Repeat="5" OnDuration="0:30" OffDuration="0:30" OnPower="1.2" OffPower="0.85" Cadence="90"/>
        <Cooldown Duration="10:00" PowerLow="0.65" PowerHigh="0.5" Cadence="85"/>
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

# Example usage
if __name__ == "__main__":
    # Workout description
    description = """60-90 min total ride time with efforts:

10 min low Z3 (280-300w), 95+ rpm

3 sets of 5x30 sec ~420w / 30 sec ~300w; full recovery between."""

    filepath = save_workout("High_Intensity_Intervals", description)
    print(f"Workout saved to: {filepath}") 