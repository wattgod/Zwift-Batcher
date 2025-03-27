from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
from datetime import datetime
from lxml import etree as ET
import logging
import re
import traceback
import time

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

# Create a directory for workout files
if 'DYNO' in os.environ:  # Running on Heroku
    WORKOUT_DIR = '/tmp/generated_workouts'  # Use Heroku's ephemeral filesystem
else:
    WORKOUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_workouts')
os.makedirs(WORKOUT_DIR, exist_ok=True)
logger.info(f"Using directory for workouts: {WORKOUT_DIR}")

def sanitize_filename(filename):
    """Sanitize filename by removing invalid characters."""
    # Replace invalid characters with underscores
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove any non-ASCII characters
    filename = re.sub(r'[^\x00-\x7F]+', '_', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Replace multiple underscores with a single one
    filename = re.sub(r'_+', '_', filename)
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    return filename if filename else "workout"  # Fallback if filename is empty

def parse_workout_description(description):
    """Parse the workout description into structured segments."""
    sections = {
        'warmup': [],
        'main': [],
        'cooldown': []
    }
    
    lines = description.split('\n')
    current_section = 'main'  # Default to main if no section specified
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Identify if line contains base/warmup info
        if 'base' in line.lower() or 'z1-z2' in line.lower():
            sections['warmup'].append(line)
            continue
            
        # Add to main set by default
        sections['main'].append(line)
    
    return sections

def parse_interval_set(text):
    """Parse interval notation like '6x5' / 3' recovery'."""
    try:
        # Extract sets and interval structure
        sets_match = re.search(r'(\d+)x(\d+)', text)
        if sets_match:
            sets = int(sets_match.group(1))
            interval_length = int(sets_match.group(2))
        else:
            sets = 1
            interval_length = 0

        # Extract recovery
        recovery_match = re.search(r'(\d+)\'\s*recovery', text)
        recovery = int(recovery_match.group(1)) * 60 if recovery_match else 0

        # Look for SFR notation
        sfr_match = re.search(r'SFR.*?(\d+)-(\d+)r', text)
        sfr_cadence = None
        if sfr_match:
            sfr_cadence_low = int(sfr_match.group(1))
            sfr_cadence_high = int(sfr_match.group(2))
            sfr_cadence = (sfr_cadence_low + sfr_cadence_high) // 2

        return {
            'sets': sets,
            'interval_length': interval_length * 60,  # Convert to seconds
            'recovery': recovery,
            'sfr_cadence': sfr_cadence
        }
    except Exception as e:
        logger.error(f"Error parsing interval set: {e}")
        return None

def parse_power_zone(text):
    """Convert zone notation to FTP percentages."""
    text = text.lower()
    
    # Handle max efforts
    if 'max' in text:
        return 1.2  # 120% FTP
        
    # Handle zone notation
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
        
    # Default to Z2 if no zone specified
    return 0.65

def parse_duration(text):
    """Extract duration in seconds from text."""
    # Default duration (5 minutes)
    duration = 300
    
    # Look for time indicators
    if 'min' in text.lower():
        try:
            duration = int(re.search(r'(\d+)\s*min', text.lower()).group(1)) * 60
        except (AttributeError, ValueError):
            pass
    elif 'sec' in text.lower():
        try:
            duration = int(re.search(r'(\d+)\s*sec', text.lower()).group(1))
        except (AttributeError, ValueError):
            pass
            
    return str(duration)

def create_30_30_workout(workout_section):
    """Create a 30/30 over/under workout structure."""
    # Warm-up (15 minutes progressive)
    ET.SubElement(workout_section, "Warmup",
                 Duration="900",  # 15 minutes
                 PowerLow="0.50",  # 50% FTP
                 PowerHigh="0.75",  # 75% FTP
                 Cadence="85")

    # 5 minutes steady state
    ET.SubElement(workout_section, "SteadyState",
                 Duration="300",  # 5 minutes
                 Power="0.75",    # 75% FTP
                 Cadence="90")

    # Main set: 3 sets of 10 minutes (30 sec over, 30 sec under)
    for _ in range(3):
        # 10 minutes of 30/30s (20 repetitions)
        ET.SubElement(workout_section, "IntervalsT",
                     Repeat="10",           # 10 repeats = 10 minutes
                     OnDuration="30",       # 30 seconds over
                     OffDuration="30",      # 30 seconds under
                     OnPower="1.05",        # 105% FTP (over)
                     OffPower="0.95",       # 95% FTP (under)
                     Cadence="90")
        
        # 3 minutes recovery between sets
        if _ < 2:  # Don't add recovery after last set
            ET.SubElement(workout_section, "SteadyState",
                         Duration="180",     # 3 minutes
                         Power="0.65",       # 65% FTP
                         Cadence="85")

    # Cool-down (10 minutes)
    ET.SubElement(workout_section, "Cooldown",
                 Duration="600",  # 10 minutes
                 PowerLow="0.75", # 75% FTP
                 PowerHigh="0.50", # 50% FTP
                 Cadence="85")

def create_gavin_special_workout(workout_section):
    """Create the Gavin Special workout structure."""
    # Progressive Warm-up (15 minutes)
    ET.SubElement(workout_section, "Warmup",
                 Duration="900",  # 15 minutes
                 PowerLow="0.50",  # Z1
                 PowerHigh="0.75",  # Z2
                 Cadence="85")
    
    # High cadence section (10 minutes at Z3)
    ET.SubElement(workout_section, "SteadyState",
                 Duration="600",  # 10 minutes
                 Power="0.85",    # Z3
                 Cadence="100")
    
    # 3x30s building efforts
    for _ in range(3):
        ET.SubElement(workout_section, "Ramp",
                     Duration="30",   # 30 seconds
                     PowerLow="0.85", # Z3
                     PowerHigh="1.05", # Z5
                     Cadence="95")
        ET.SubElement(workout_section, "SteadyState",
                     Duration="30",   # 30 seconds recovery
                     Power="0.65",    # Z2
                     Cadence="85")
    
    # Main Set (4 x 8-minute blocks)
    for _ in range(4):
        # First 40/20 block (2 minutes = 3 repeats)
        ET.SubElement(workout_section, "IntervalsT",
                     Repeat="3",
                     OnDuration="40",
                     OffDuration="20",
                     OnPower="1.2",    # Z6/Max
                     OffPower="0.65",   # Z2
                     Cadence="100")
        
        # 4 min Z3/Z4 block
        ET.SubElement(workout_section, "SteadyState",
                     Duration="240",    # 4 minutes
                     Power="0.9",       # Z3/Z4
                     Cadence="90")
        
        # Second 40/20 block
        ET.SubElement(workout_section, "IntervalsT",
                     Repeat="3",
                     OnDuration="40",
                     OffDuration="20",
                     OnPower="1.2",    # Z6/Max
                     OffPower="0.65",   # Z2
                     Cadence="100")
        
        # Recovery
        if _ < 3:  # Don't add recovery after last set
            ET.SubElement(workout_section, "SteadyState",
                         Duration="240",    # 4 minutes
                         Power="0.65",      # Z2
                         Cadence="85")
    
    # Cool-down (10 minutes)
    ET.SubElement(workout_section, "Cooldown",
                 Duration="600",  # 10 minutes
                 PowerLow="0.75", # Z2
                 PowerHigh="0.50", # Z1
                 Cadence="85")

def format_workout_description(workout_name, description):
    """Format the workout description with pre-activity instructions and structure."""
    if not description:
        if 'gavin' in workout_name.lower():
            return """► Pre-activity Instructions:
- Focus on maintaining high cadence (100+ RPM) during the high cadence section
- During 40/20s, aim for max power output (121-151% FTP)
- Keep recovery periods easy to ensure quality of the next interval
- Pre-workout nutrition: Ensure adequate carbohydrate intake (50-75g/hour for workouts >90min)
- Hydration: Preload with sodium and water, aim for 500-1000mg sodium/hour during workout
- If you can't hit target power during intervals, stop and recover - quality over quantity
- Mix up your position during intervals (both seated and standing)

► Warm-up:
- 15 min progressive warm-up from Z1 to Z2 (RPE 1-3)
- 10 min high cadence Z3 (100-120 rpm, RPE 4-5)
- 3x30s building efforts (Z3 to Z5)

► Main Set (4 x 8-minute blocks):
- 2 min 40/20s (40s Max Effort, 20s Z2)
- 4 min @ Z3/Z4 (RPE 5-6)
- 2 min 40/20s (40s Max Effort, 20s Z2)
- 4 min recovery @ Z2 (RPE 2-3)

► Cool-down:
- 10 min easy Z1/Z2"""
        else:  # 30/30 workout
            return """► Pre-activity Instructions:
- Focus on maintaining steady cadence around 90 RPM
- Over intervals at 105% FTP, Under intervals at 95% FTP
- Keep form during both over and under segments
- Stay seated unless specified
- Hydration: Drink to thirst

► Warm-up:
- 15 min progressive warm-up
- 5 min steady state @ 75% FTP

► Main Set (3 x 10-minute blocks):
- 10 min of 30/30s (30s over, 30s under)
- 3 min recovery between sets @ 65% FTP

► Cool-down:
- 10 min easy"""
    return description

def create_workout_xml(name, description):
    """Create the XML structure for a workout."""
    # Create root element
    workout_file = ET.Element("workout_file")
    
    # Add author
    author = ET.SubElement(workout_file, "author")
    author.text = "Gravel God Cycling"
    
    # Add name
    workout_name = ET.SubElement(workout_file, "name")
    workout_name.text = name
    
    # Add description
    workout_description = ET.SubElement(workout_file, "description")
    workout_description.text = format_workout_description(name, description)
    
    # Add sportType
    sport_type = ET.SubElement(workout_file, "sportType")
    sport_type.text = "bike"
    
    # Add workout tag
    tags = ET.SubElement(workout_file, "tags")
    tag = ET.SubElement(tags, "tag")
    tag.text = "Gravel God Cycling"
    
    # Add workout section
    workout = ET.SubElement(workout_file, "workout")
    
    # Parse the description and create workout structure
    sections = parse_workout_description(description)
    
    # Add warmup if present
    if sections['warmup']:
        ET.SubElement(workout, "Warmup",
                     Duration="900",  # 15 minutes
                     PowerLow="0.50",  # Z1
                     PowerHigh="0.75",  # Z2
                     Cadence="85")
    
    # Process main set
    for line in sections['main']:
        if 'x' in line:  # Interval set
            interval_data = parse_interval_set(line)
            if interval_data:
                # Add intervals
                ET.SubElement(workout, "IntervalsT",
                            Repeat=str(interval_data['sets']),
                            OnDuration=str(interval_data['interval_length']),
                            OffDuration=str(interval_data['recovery']),
                            OnPower="1.0",  # 100% FTP
                            OffPower="0.65",  # Recovery
                            Cadence="90")
        else:
            # Add steady state
            ET.SubElement(workout, "SteadyState",
                        Duration=parse_duration(line),
                        Power=str(parse_power_zone(line)),
                        Cadence="90")
    
    # Add cooldown
    ET.SubElement(workout, "Cooldown",
                 Duration="600",  # 10 minutes
                 PowerLow="0.75",  # Z2
                 PowerHigh="0.50",  # Z1
                 Cadence="85")
    
    return workout_file

def generate_zwo_file(name, description):
    """Generate a ZWO file from the workout description."""
    try:
        # Sanitize the filename
        safe_filename = sanitize_filename(name)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_filename}_{timestamp}.zwo"
        
        # Create full path
        filepath = os.path.join(WORKOUT_DIR, filename)
        
        # Create the XML structure
        workout_xml = create_workout_xml(name, description)
        
        # Save the file
        with open(filepath, 'wb') as f:
            f.write(ET.tostring(workout_xml, pretty_print=True, xml_declaration=True, encoding='UTF-8'))
        
        return filename
        
    except Exception as e:
        logger.error(f"Error generating ZWO file: {str(e)}\n{traceback.format_exc()}")
        raise

@app.route('/generate', methods=['POST'])
def generate_workout():
    try:
        data = request.get_json()
        
        # Get the workout name and description
        workout_name = data.get('name', '').strip()
        workout_description = data.get('description', '').strip()
        
        if not workout_name or not workout_description:
            return jsonify({'error': 'Missing workout name or description'}), 400
            
        # Generate the workout file
        filename = generate_zwo_file(workout_name, workout_description)
        
        # Create full path for the workout file
        filepath = os.path.join(WORKOUT_DIR, filename)
        
        # Return the file
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/xml'
        )
        
    except Exception as e:
        logger.error(f"Error generating workout: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Error generating workout: {str(e)}'}), 500

@app.route('/download/<filename>')
def download(filename):
    try:
        filepath = os.path.join(WORKOUT_DIR, filename)
        logger.info(f"Attempting to download: {filepath}")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Workout file not found: {filename}")
            
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        logger.error(f"Error in download: {e}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
