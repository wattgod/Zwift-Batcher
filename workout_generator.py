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
    # Format the workout name with underscores for both the XML and filename
    formatted_name = workout_name.replace(' ', '_')
    
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<workout_file xmlns="http://www.zwift.com">\n    <author>Gravel God Cycling</author>\n    <n>' + formatted_name + '</n>\n    <description><![CDATA[' + format_workout_description(workout_name, description) + ']]></description>\n    <sportType>bike</sportType>\n    <tags/>\n    <workout>\n        <Warmup Duration="600" PowerLow="0.5" PowerHigh="0.65" Cadence="85"/>\n        <SteadyState Duration="600" Power="0.80" Cadence="95"/>\n        <SteadyState Duration="180" Power="0.65" Cadence="85"/>\n        <IntervalsT Repeat="10" OnDuration="30" OffDuration="30" OnPower="1.2" OffPower="0.75" Cadence="90"/>\n        <SteadyState Duration="300" Power="0.65" Cadence="85"/>\n        <IntervalsT Repeat="10" OnDuration="30" OffDuration="30" OnPower="1.2" OffPower="0.75" Cadence="90"/>\n        <SteadyState Duration="300" Power="0.65" Cadence="85"/>\n        <IntervalsT Repeat="10" OnDuration="30" OffDuration="30" OnPower="1.2" OffPower="0.75" Cadence="90"/>\n        <Cooldown Duration="600" PowerLow="0.65" PowerHigh="0.5" Cadence="85"/>\n    </workout>\n</workout_file>'
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{formatted_name}_{timestamp}.zwo"
    
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