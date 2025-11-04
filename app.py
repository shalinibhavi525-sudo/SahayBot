from flask import Flask, render_template, request, jsonify
import re
from datetime import datetime

app = Flask(__name__)

# Emergency helplines database
HELPLINES = {
    'mental_health': {
        'name': 'KIRAN Mental Health Helpline',
        'number': '1800-599-0019',
        'available': '24/7',
        'languages': 'Hindi, English, and 13 regional languages'
    },
    'suicide_prevention': {
        'name': 'iCall Suicide Prevention',
        'number': '9152987821',
        'available': 'Mon-Sat 8AM-10PM',
        'languages': 'Hindi, English, Marathi'
    },
    'disaster': {
        'name': 'National Disaster Helpline',
        'number': '1078 / 1070',
        'available': '24/7',
        'languages': 'All Indian languages'
    },
    'medical': {
        'name': 'Medical Emergency',
        'number': '108',
        'available': '24/7',
        'languages': 'Regional languages'
    },
    'police': {
        'name': 'Police Emergency',
        'number': '100',
        'available': '24/7',
        'languages': 'Regional languages'
    },
    'women_helpline': {
        'name': 'Women Helpline',
        'number': '1091 / 181',
        'available': '24/7',
        'languages': 'Regional languages'
    }
}

# Crisis keywords for detection
CRISIS_KEYWORDS = {
    'high_risk': ['suicide', 'kill myself', 'end it all', 'can\'t go on', 'no reason to live', 
                  'better off dead', 'harm myself'],
    'mental_distress': ['depressed', 'hopeless', 'anxious', 'panic', 'scared', 'worthless', 
                       'alone', 'overwhelmed', 'can\'t cope'],
    'disaster': ['flood', 'earthquake', 'cyclone', 'fire', 'evacuation', 'trapped', 
                 'emergency shelter', 'rescue'],
    'medical': ['chest pain', 'breathing difficulty', 'bleeding', 'unconscious', 
                'poisoning', 'allergic reaction', 'seizure'],
    'violence': ['abuse', 'domestic violence', 'assault', 'threatened', 'unsafe']
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_message():
    """
    Analyze user message and provide contextual support
    """
    try:
        data = request.json
        message = data.get('message', '').lower()
        
        # Detect crisis type
        crisis_type = detect_crisis_type(message)
        
        # Generate response based on crisis type
        response = generate_response(crisis_type, message)
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def detect_crisis_type(message):
    """
    Detect the type of crisis from user message
    """
    scores = {
        'high_risk': 0,
        'mental_distress': 0,
        'disaster': 0,
        'medical': 0,
        'violence': 0
    }
    
    # Check for keywords
    for crisis_type, keywords in CRISIS_KEYWORDS.items():
        for keyword in keywords:
            if keyword in message:
                scores[crisis_type] += 1
    
    # Get highest scoring crisis type
    if max(scores.values()) == 0:
        return 'general'
    
    return max(scores, key=scores.get)

def generate_response(crisis_type, message):
    """
    Generate contextual response based on crisis type
    """
    responses = {
        'high_risk': {
            'severity': 'CRITICAL',
            'message': 'I\'m really concerned about you. Your life matters, and there are people who want to help.',
            'immediate_action': 'Please call the suicide prevention helpline RIGHT NOW. They have trained counselors available.',
            'helplines': ['suicide_prevention', 'mental_health'],
            'tips': [
                'Remove any means of self-harm from your immediate area',
                'Call a trusted friend or family member immediately',
                'Go to a public place if you\'re alone',
                'Text a crisis counselor if calling feels hard',
                'Remember: This feeling is temporary, even if it doesn\'t feel that way'
            ],
            'color': 'red'
        },
        'mental_distress': {
            'severity': 'HIGH',
            'message': 'I hear you, and what you\'re feeling is valid. You don\'t have to face this alone.',
            'immediate_action': 'Consider reaching out to a mental health professional or helpline for support.',
            'helplines': ['mental_health', 'suicide_prevention'],
            'tips': [
                'Take 5 deep breaths: inhale for 4, hold for 4, exhale for 6',
                'Write down what you\'re feeling - getting it out helps',
                'Reach out to someone you trust',
                'Remember: You\'ve survived 100% of your worst days so far',
                'Consider professional help - it\'s a sign of strength, not weakness'
            ],
            'color': 'orange'
        },
        'disaster': {
            'severity': 'URGENT',
            'message': 'Stay calm. Your safety is the priority. Follow these steps carefully.',
            'immediate_action': 'If you\'re in immediate danger, call the disaster helpline or move to safety.',
            'helplines': ['disaster', 'police'],
            'tips': [
                'Move to higher ground if flooding',
                'Stay indoors during cyclone/storm',
                'Have emergency supplies ready (water, food, flashlight)',
                'Keep phone charged and with you',
                'Follow official evacuation orders immediately'
            ],
            'color': 'yellow'
        },
        'medical': {
            'severity': 'URGENT',
            'message': 'Medical emergencies require immediate professional care.',
            'immediate_action': 'Call 108 (medical emergency) NOW if symptoms are severe.',
            'helplines': ['medical'],
            'tips': [
                'Stay calm and keep the person calm',
                'Don\'t move person if spinal injury suspected',
                'Apply pressure to bleeding wounds with clean cloth',
                'If unconscious, check breathing and place in recovery position',
                'Write down all symptoms to tell the emergency team'
            ],
            'color': 'red'
        },
        'violence': {
            'severity': 'URGENT',
            'message': 'Your safety comes first. You deserve to be safe.',
            'immediate_action': 'If you\'re in immediate danger, call 100 (police) or move to a safe location.',
            'helplines': ['women_helpline', 'police'],
            'tips': [
                'Trust your instincts - if you feel unsafe, you probably are',
                'Have an escape plan and practice it',
                'Keep important documents and emergency money accessible',
                'Tell someone you trust about the situation',
                'Remember: This is NOT your fault'
            ],
            'color': 'red'
        },
        'general': {
            'severity': 'NORMAL',
            'message': 'I\'m here to help. Tell me what\'s on your mind.',
            'immediate_action': 'Feel free to share more, or ask me anything about safety and wellbeing.',
            'helplines': ['mental_health'],
            'tips': [
                'Take care of basic needs: sleep, food, water',
                'Reach out to friends and family',
                'Practice self-care activities you enjoy',
                'Remember: It\'s okay to ask for help',
                'You deserve support and understanding'
            ],
            'color': 'green'
        }
    }
    
    response_data = responses.get(crisis_type, responses['general'])
    
    # Add helpline details
    helpline_details = []
    for helpline_key in response_data.get('helplines', []):
        if helpline_key in HELPLINES:
            helpline_details.append(HELPLINES[helpline_key])
    
    response_data['helpline_details'] = helpline_details
    response_data['timestamp'] = datetime.now().isoformat()
    
    return response_data

@app.route('/resources')
def get_resources():
    """
    Get all emergency resources
    """
    return jsonify({
        'helplines': HELPLINES,
        'self_care': {
            'breathing': '4-7-8 technique: Inhale 4 sec, hold 7 sec, exhale 8 sec',
            'grounding': '5-4-3-2-1: Name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste',
            'movement': 'Walk for 10 minutes or do simple stretches',
            'connection': 'Text or call one person who cares about you'
        },
        'emergency_numbers': {
            'All India': {
                'Police': '100',
                'Ambulance': '108',
                'Fire': '101',
                'Disaster': '1078',
                'Women Helpline': '1091'
            }
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
