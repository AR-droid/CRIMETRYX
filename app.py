from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__, template_folder='../frontend/public')

# ---------------------- Path Setup ----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PREDICTIONS_PATH = os.path.join(DATA_DIR, "rule_based_predictions.csv")
RISK_SCORES_PATH = os.path.join(DATA_DIR, "risk_scores.csv")
LOCATIONS_PATH = os.path.join(DATA_DIR, "locations.csv")

print(f"Loading data from:")
print(f"PREDICTIONS_PATH: {PREDICTIONS_PATH}")
print(f"RISK_SCORES_PATH: {RISK_SCORES_PATH}")
print(f"LOCATIONS_PATH: {LOCATIONS_PATH}")

# Load data
try:
    # Check if files exist
    if not os.path.exists(PREDICTIONS_PATH):
        raise FileNotFoundError(f"Predictions file not found at {PREDICTIONS_PATH}")
    if not os.path.exists(RISK_SCORES_PATH):
        raise FileNotFoundError(f"Risk scores file not found at {RISK_SCORES_PATH}")
    if not os.path.exists(LOCATIONS_PATH):
        raise FileNotFoundError(f"Locations file not found at {LOCATIONS_PATH}")

    # Load the data
    pred_df = pd.read_csv(PREDICTIONS_PATH)
    print(f"Loaded predictions: {len(pred_df)} rows")
    
    risk_df = pd.read_csv(RISK_SCORES_PATH)
    print(f"Loaded risk scores: {len(risk_df)} rows")
    
    locations_df = pd.read_csv(LOCATIONS_PATH)
    print(f"Loaded locations: {len(locations_df)} rows")
    
    # Merge predictions and risk scores
    df = pd.merge(pred_df, risk_df, on="SuspectID", how="left")
    print(f"After first merge: {len(df)} rows")
    
    # Add location information
    df['LocationID'] = df['SuspectID'].apply(lambda x: f"L{x[1:].zfill(4)}")
    df = pd.merge(df, locations_df, on="LocationID", how="left")
    print(f"After second merge: {len(df)} rows")
    
except Exception as e:
    print(f"Error loading data: {str(e)}")
    # Create sample data for testing
    df = pd.DataFrame({
        'SuspectID': ['S001', 'S002', 'S003', 'S004', 'S005'],
        'PredictedCrimeType': ['Robbery', 'Fraud', 'Murder', 'Cybercrime', 'Temple Theft'],
        'RiskScore': [2.8, 2.1, 3.2, 1.8, 2.5],
        'Area': ['T. Nagar', 'Anna Nagar', 'Velachery', 'Adyar', 'Mylapore'],
        'Latitude': [13.0827, 13.0878, 12.9815, 13.0012, 13.0337],
        'Longitude': [80.2707, 80.2037, 80.2180, 80.2565, 80.2687]
    })
    print("Using sample data instead")

# ---------------------- Dashboard Route ----------------------
@app.route('/')
def dashboard():
    try:
        total_suspects = len(df['SuspectID'].unique())
        crime_types = df['PredictedCrimeType'].unique()
        crime_type_count = len(crime_types)
        high_risk = len(df[df['RiskScore'] >= 2.5])
        
        print(f"Dashboard stats:")
        print(f"Total suspects: {total_suspects}")
        print(f"Crime types: {crime_type_count}")
        print(f"High risk: {high_risk}")
        
        return render_template('index.html', 
                            total_suspects=total_suspects,
                            crime_types=crime_type_count,
                            high_risk=high_risk)
    except Exception as e:
        print(f"Error in dashboard route: {str(e)}")
        return render_template('index.html', 
                            total_suspects=0,
                            crime_types=0,
                            high_risk=0)

# ---------------------- Crime Hotspots API ----------------------
@app.route('/api/hotspots')
def get_hotspots():
    if df.empty:
        return jsonify({'hotspots': []})
    
    # Get unique locations with their highest risk scores
    location_risks = {}
    for _, row in df.iterrows():
        location = row['LocationID']
        risk_score = row.get('RiskScore', 2)
        if location not in location_risks or risk_score > location_risks[location]['risk_score']:
            location_risks[location] = {
                'risk_score': risk_score,
                'crime_type': row.get('PredictedCrimeType', 'Unknown'),
                'severity': row.get('SeverityComponent', 2),
                'lat': row.get('Latitude'),
                'lon': row.get('Longitude'),
                'area': row.get('Area', 'Unknown')
            }
    
    hotspots = []
    for location, info in location_risks.items():
        if info['lat'] is not None and info['lon'] is not None:
            hotspots.append({
                'location': info['area'],
                'lat': float(info['lat']),
                'lon': float(info['lon']),
                'risk_score': float(info['risk_score']),
                'crime_type': info['crime_type'],
                'severity': int(info['severity']),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
    
    hotspots.sort(key=lambda x: x['risk_score'], reverse=True)
    return jsonify({'hotspots': hotspots})

# ---------------------- Patrol Schedule API ----------------------
@app.route('/api/patrol-schedule')
def get_patrol_schedule():
    if df.empty:
        return jsonify({'schedule': []})
    
    schedule = []
    current_time = datetime.now()
    
    # Get unique locations with their highest risk scores
    location_risks = {}
    for _, row in df.iterrows():
        location = row['LocationID']
        risk_score = row.get('RiskScore', 2)
        if location not in location_risks or risk_score > location_risks[location]['risk_score']:
            location_risks[location] = {
                'risk_score': risk_score,
                'crime_type': row.get('PredictedCrimeType', 'Unknown'),
                'severity': row.get('SeverityComponent', 2),
                'lat': row.get('Latitude'),
                'lon': row.get('Longitude'),
                'area': row.get('Area', 'Unknown')
            }
    
    # Sort locations by risk score
    sorted_locations = sorted(location_risks.items(), key=lambda x: x[1]['risk_score'], reverse=True)
    
    for i, (location, info) in enumerate(sorted_locations):
        if info['lat'] is None or info['lon'] is None:
            continue
            
        if info['risk_score'] > 2.5:
            patrol_duration = '3 hours'
            patrol_interval = 2
        elif info['risk_score'] > 2:
            patrol_duration = '2 hours'
            patrol_interval = 3
        else:
            patrol_duration = '1 hour'
            patrol_interval = 4
        
        patrol_time = current_time + timedelta(hours=i*patrol_interval)
        
        schedule.append({
            'location': info['area'],
            'coordinates': {'lat': float(info['lat']), 'lon': float(info['lon'])},
            'time': patrol_time.strftime('%Y-%m-%d %H:%M:%S'),
            'risk_level': 'High' if info['risk_score'] > 2.5 else 'Medium' if info['risk_score'] > 2 else 'Low',
            'patrol_duration': patrol_duration,
            'crime_type': info['crime_type'],
            'risk_score': float(info['risk_score']),
            'severity': int(info['severity'])
        })
    
    return jsonify({'schedule': schedule})

# ---------------------- Time Analysis API ----------------------
@app.route('/api/time-analysis')
def get_time_analysis():
    if df.empty:
        return jsonify({
            'hourly_patterns': {},
            'weekday_patterns': {},
            'location_patterns': {}
        })
    
    # Generate some sample time-based patterns
    hourly_patterns = {}
    weekday_patterns = {}
    
    current_hour = datetime.now().hour
    current_day = datetime.now().weekday()
    
    # Sample data for current hour
    hourly_patterns[str(current_hour)] = {
        'count': len(df),
        'most_common': df['PredictedCrimeType'].mode().iloc[0],
        'severity_avg': float(df['SeverityComponent'].mean())
    }
    
    # Sample data for current day
    weekday_patterns[str(current_day)] = {
        'count': len(df),
        'most_common': df['PredictedCrimeType'].mode().iloc[0],
        'severity_avg': float(df['SeverityComponent'].mean())
    }
    
    return jsonify({
        'hourly_patterns': hourly_patterns,
        'weekday_patterns': weekday_patterns
    })

# ---------------------- Predictions View ----------------------
@app.route('/predictions')
def predictions():
    try:
        search = request.args.get('search', '')
        crime = request.args.get('crime', '')
        risk = request.args.get('risk', '')
        
        filtered = df.copy()
        if search:
            filtered = filtered[
                (filtered['SuspectID'].str.contains(search, case=False)) |
                (filtered['Area'].str.contains(search, case=False))
            ]
        if crime:
            filtered = filtered[filtered['PredictedCrimeType'] == crime]
        if risk:
            if risk == 'High':
                filtered = filtered[filtered['RiskScore'] >= 2.5]
            elif risk == 'Medium':
                filtered = filtered[(filtered['RiskScore'] >= 2) & (filtered['RiskScore'] < 2.5)]
            elif risk == 'Low':
                filtered = filtered[filtered['RiskScore'] < 2]
        
        return render_template('predictions.html', 
                            data=filtered.to_dict('records'),
                            crimes=df['PredictedCrimeType'].unique().tolist())
    except Exception as e:
        return render_template('predictions.html', data=[], crimes=[])

# ---------------------- Graph API ----------------------
@app.route('/graph')
def graph():
    return render_template('graph.html')

@app.route('/api/graph')
def get_graph():
    try:
        # Create nodes from suspects
        nodes = []
        for _, row in df.iterrows():
            nodes.append({
                'id': row['SuspectID'],
                'risk': row['RiskScore'],
                'crime_type': row['PredictedCrimeType'],
                'location': row['Area']
            })
        
        # Create links based on shared locations and crime types
        links = []
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if (nodes[i]['location'] == nodes[j]['location'] or 
                    nodes[i]['crime_type'] == nodes[j]['crime_type']):
                    links.append({
                        'source': nodes[i]['id'],
                        'target': nodes[j]['id']
                    })
        
        return jsonify({
            'nodes': nodes,
            'links': links
        })
    except Exception as e:
        # Return sample data if there's an error
        return jsonify({
            'nodes': [
                {'id': 'S001', 'risk': 2.8, 'crime_type': 'Robbery', 'location': 'T. Nagar'},
                {'id': 'S002', 'risk': 1.5, 'crime_type': 'Theft', 'location': 'Anna Nagar'},
                {'id': 'S003', 'risk': 3.2, 'crime_type': 'Murder', 'location': 'Velachery'},
                {'id': 'S004', 'risk': 2.1, 'crime_type': 'Fraud', 'location': 'Adyar'},
                {'id': 'S005', 'risk': 1.8, 'crime_type': 'Assault', 'location': 'Nungambakkam'}
            ],
            'links': [
                {'source': 'S001', 'target': 'S002'},
                {'source': 'S001', 'target': 'S003'},
                {'source': 'S002', 'target': 'S004'},
                {'source': 'S003', 'target': 'S005'},
                {'source': 'S004', 'target': 'S005'}
            ]
        })

# ---------------------- Suspect Details View ----------------------
@app.route('/suspect/<sid>')
def suspect_details(sid):
    try:
        suspect_data = df[df['SuspectID'] == sid].iloc[0].to_dict()
        return render_template('suspect.html', suspect=suspect_data)
    except Exception as e:
        return render_template('suspect.html', suspect=None)

# ---------------------- Suspect API ----------------------
@app.route('/api/suspect/<sid>')
def get_suspect(sid):
    try:
        suspect_data = df[df['SuspectID'] == sid].iloc[0].to_dict()
        return jsonify(suspect_data)
    except Exception as e:
        return jsonify({'error': 'Suspect not found'}), 404

@app.route('/api/graph-data')
def get_graph_data():
    # Sample data structure matching the image
    graph_data = {
        "nodes": [
            {"id": "S0005", "label": "S0005", "type": "suspect", "risk_score": 2.8},
            {"id": "L05", "label": "L05", "type": "location"},
            {"id": "Robbery", "label": "Robbery", "type": "crime_type"},
            {"id": "Temple hundi theft", "label": "Temple\nhundi theft", "type": "mo_pattern"},
            {"id": "Screwdriver", "label": "Screwdriver", "type": "weapon"},
            {"id": "S0004", "label": "S0004", "type": "suspect", "risk_score": 2.2},
            {"id": "L04", "label": "L04", "type": "location"}
        ],
        "links": [
            {"source": "S0005", "target": "L05", "type": "ACTIVE_IN"},
            {"source": "S0005", "target": "Robbery", "type": "LIKELY_TO_COMMIT"},
            {"source": "S0005", "target": "Temple hundi theft", "type": "MATCHED_WITH"},
            {"source": "S0005", "target": "Screwdriver", "type": "LIKELY_TO_USE"},
            {"source": "S0004", "target": "Temple hundi theft", "type": "MATCHED_WITH"},
            {"source": "S0004", "target": "Robbery", "type": "LIKELY_TO_COMMIT"},
            {"source": "S0004", "target": "L04", "type": "ACTIVE_IN"},
            {"source": "S0004", "target": "Screwdriver", "type": "LIKELY_TO_USE"}
        ]
    }
    return jsonify(graph_data)

# ---------------------- Main ----------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
