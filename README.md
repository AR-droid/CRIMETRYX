# CRIMETRYX
# CRIMETRYX

A sophisticated crime analysis system that helps law enforcement agencies analyze crime patterns, predict potential criminal activities, and visualize relationships between suspects, locations, and crime types.

## Features

- Interactive crime hotspot visualization
- Suspect risk assessment and profiling
- Crime pattern analysis
- Network graph visualization of criminal relationships
- Predictive analytics for crime prevention

## Project Structure

```
.
├── backend/                 # Flask backend
│   ├── app.py              # Main application
│   ├── neo4j_ingest.py     # Database ingestion
│   ├── train_model.py      # ML model training
│   ├── requirements.txt    # Python dependencies
│   ├── utils/             # Utility functions
│   ├── models/            # Trained models
│   ├── data/              # Data files
│   └── analysis/          # Analysis scripts
│
└── frontend/               # Frontend
    ├── public/            # Static files
    └── src/               # Source code
```

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Start the backend server:
```bash
python app.py
```

4. Open the frontend in a web browser:
```bash
open frontend/public/index.html
```

## Data

The system uses the following data sources:
- Crime records
- Suspect profiles
- Location data
- MO (Modus Operandi) patterns
- Risk assessment scores

## Features in Detail

### Crime Hotspot Map
- Interactive map showing crime hotspots
- Color-coded risk levels
- Clickable markers with detailed information

### Network Graph
- Visualization of relationships between:
  - Suspects
  - Locations
  - Crime types
  - MO patterns
  - Weapons used

### Risk Assessment
- Suspect risk scoring
- Pattern recognition
- Predictive analytics

For inquiries, reach out via email: anjanarangarajan06@gmail.com
