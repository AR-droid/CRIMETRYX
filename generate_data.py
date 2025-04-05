import pandas as pd
import random
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
from collections import defaultdict
import math  # For exponential decay in risk calculation

# Initialize with Indian locale and seed for reproducibility
fake = Faker('en_IN')
random.seed(42)
np.random.seed(42)

# Constants with Tamil Nadu context
NUM_RECORDS = 50
DATASET_PATH = "backend/data/"

CITIES = {
    "Chennai": {"areas": ["T. Nagar", "Anna Nagar", "Adyar", "Velachery", "Nungambakkam", "Mylapore", "Kilpauk", "Tambaram", "Pallavaram", "Perambur"], 
               "lat_range": (13.0, 13.2), "lon_range": (80.1, 80.3),
               "crime_hotspots": ["T. Nagar", "Velachery", "Pallavaram"]},
    "Coimbatore": {"areas": ["Gandhipuram", "Peelamedu", "Saibaba Colony", "R.S. Puram", "Ukkadam", "Singanallur", "Saravanampatti"], 
                  "lat_range": (11.0, 11.1), "lon_range": (76.9, 77.0),
                  "crime_hotspots": ["Gandhipuram", "Ukkadam"]},
    "Madurai": {"areas": ["Koodal Nagar", "Goripalayam", "Simmakkal", "Tallakulam", "Villapuram", "Anna Nagar"], 
               "lat_range": (9.9, 10.0), "lon_range": (78.1, 78.2),
               "crime_hotspots": ["Goripalayam", "Simmakkal"]},
    "Trichy": {"areas": ["Srirangam", "Woraiyur", "Cantonment", "K.K. Nagar", "Thillai Nagar"], 
              "lat_range": (10.8, 10.9), "lon_range": (78.6, 78.7),
              "crime_hotspots": ["Srirangam", "Cantonment"]},
    "Salem": {"areas": ["Hasthampatti", "Fairlands", "Suramangalam", "Ammapet", "Kondalampatti"], 
             "lat_range": (11.6, 11.7), "lon_range": (78.1, 78.2),
             "crime_hotspots": ["Hasthampatti", "Fairlands"]}
}

# Tamil Nadu specific gangs
GANGS = {
    "Chennai": ["Arcot Gang", "Washermenpet Don", "Pallavaram Mafia"],
    "Madurai": ["Karuppu Gang", "Pandi Group"],
    "Coimbatore": ["Peelamedu Boys", "RS Puram Network"],
    "Trichy": ["Srirangam Syndicate", "Cantonment Crew"],
    "Salem": ["Hasthampatti Group", "Fairlands Alliance"]
}

# Indian castes/surnames with Tamil Nadu focus
indian_castes = [
    "Iyer", "Iyengar", "Pillai", "Mudaliar", "Chettiar", "Naidu", "Reddy", 
    "Gounder", "Thevar", "Nadar", "Vanniyar", "Konar", "Yadav", "Maravar",
    "Vellalar", "Brahmin", "Agamudayar", "Devanga", "Sengunthar", "Vannar",
    "Ambattar", "Asari", "Chakkiliyar", "Pallar", "Paraiyar", "Kongu Vellalar",
    "Kamma", "Balija", "Rajput", "Vanniyakula Kshatriya", "Gavara"
]

# Crime Types with Tamil Nadu context (expanded)
CRIME_TYPES = {
    "Murder": {"severity": 3.0, "recency": 1.5, "desc": ["Honor killing", "Property dispute", "Family feud", "Political rivalry", "Dowry death"]},
    "Robbery": {"severity": 2.5, "recency": 1.3, "desc": ["Jewelry heist", "Bank robbery", "Chain snatching", "ATM theft", "Temple hundi theft"]},
    "Assault": {"severity": 1.5, "recency": 1.2, "desc": ["Road rage", "Pub brawl", "Eve teasing", "Political clash", "Caste violence"]},
    "Burglary": {"severity": 2.0, "recency": 1.1, "desc": ["House break-in", "Shop theft", "Office burglary", "Vehicle theft", "Warehouse theft"]},
    "Theft": {"severity": 1.0, "recency": 1.0, "desc": ["Pickpocketing", "Mobile snatching", "Petty theft", "Bicycle theft", "Cable theft"]},
    "Fraud": {"severity": 1.8, "recency": 1.1, "desc": ["Land scam", "Cheating", "Matrimonial fraud", "Job racket", "Lottery scam"]},
    "Cybercrime": {"severity": 2.2, "recency": 1.4, "desc": ["Online scam", "Data breach", "Social media harassment", "Credit card fraud", "Job fraud"]},
    "Sand Smuggling": {"severity": 2.2, "recency": 1.2, "desc": ["River sand theft", "Beach sand mining"]},
    "Temple Theft": {"severity": 2.3, "recency": 1.3, "desc": ["Idol theft", "Hundi breaking"]}
}

# Weapons list with Tamil Nadu context (expanded)
WEAPONS = {
    "Murder": ["Aruval (machete)", "Knife", "Iron rod", "Wooden log", "Rope", "Acid", "Poison", "Stone"],
    "Robbery": ["Country-made pistol", "Chopper", "Iron rod", "Wooden stick", "Screwdriver", "Crowbar", "Broken bottle", "Razor"],
    "Assault": ["Wooden stick", "Beer bottle", "Belt", "Stone", "Metal chain", "Slipper", "Bamboo stick", "Brick"],
    "Burglary": ["Gas cutter", "Screwdriver", "Crowbar", "Lock picks", "Wire cutter", "Hammer", "Chisel", "Pliers"],
    "Theft": ["Razor blade", "Wire cutter", "Scissors", "Knife", "Screwdriver", "Lock pick", "Crowbar", "Pliers"],
    "Fraud": ["Fake documents", "Forged signatures", "Counterfeit stamps", "Fake IDs", "Manipulated records", "Photoshopped images", "Cloned SIM cards"],
    "Cybercrime": ["Malware", "Phishing kit", "Keylogger", "Remote access tools", "SIM box", "Cloned devices", "Spoofing software"],
    "Sand Smuggling": ["Trucks", "Excavators", "Boats", "JCB machines", "Fake permits"],
    "Temple Theft": ["Duplicate keys", "Lock picks", "Crowbars", "Gas cutters", "Religious disguises"]
}

# MO Pattern Manager Class with enhanced patterns
class MOPatternManager:
    def __init__(self):
        self.patterns = {
            "Murder": [
                "Stabbed multiple times with aruval (Tamil machete)",
                "Honor killing in traditional Tamil style",
                "Political murder with local weapons",
                "Acid attack with motorcycle getaway",
                "Dowry death staged as suicide"
            ],
            "Robbery": [
                "Temple hundi theft during festival",
                "Jewelry shop heist with country-made guns",
                "Chain snatching using motorbikes",
                "ATM theft with gas cutter",
                "Bank robbery with insider help"
            ],
            "Sand Smuggling": [
                "Nighttime river sand mining with JCBs",
                "Bribing local officials for permits",
                "Using fishing boats for sand transport",
                "Fake construction company operations",
                "Threatening local activists"
            ],
            "Temple Theft": [
                "Idol theft disguised as renovation work",
                "Hundi breaking during power cuts",
                "Using duplicate keys made by local locksmiths",
                "Collaborating with temple staff",
                "Selling artifacts to international collectors"
            ],
            # ... [other crime patterns with similar enhancements]
        }

    def get_pattern(self, crime_type):
        return random.choice(self.patterns.get(crime_type, ["Standard operation"]))

# Updated ID Generator with sequential numbering
class IDGenerator:
    def __init__(self, prefix):
        self.prefix = prefix
        self.count = 1
    
    def generate_id(self):
        id_value = f"{self.prefix}{self.count:04d}"
        self.count += 1
        return id_value

# Enhanced Risk Score Calculation with exponential decay
def calculate_risk_score(crimes, age, is_one_time=False):
    """Calculate risk score based on severity, recency, frequency, and age"""
    base_score = 0
    crime_counts = defaultdict(int)
    violent_crime_count = 0
    
    for crime in crimes:
        crime_type = crime["type"]
        days_ago = (datetime.now() - crime["date"]).days
        
        # Exponential decay for recency
        recency_factor = math.exp(-days_ago / 365)
        severity = CRIME_TYPES[crime_type]["severity"]
        base_score += severity * recency_factor
        
        crime_counts[crime_type] += 1
        if crime_type in ["Murder", "Robbery", "Assault"]:
            violent_crime_count += 1

    # Repeat offender weight
    total_crimes = len(crimes)
    if total_crimes == 0 or is_one_time:
        repeat_offender_weight = 0  # One-time offenders get zero score
    else:
        repeat_offender_weight = 1 + 0.2 * (total_crimes - 1)

    # Frequency component
    frequency_component = min(2.0, total_crimes * 0.3)

    # Violent crime bonus
    violent_crime_bonus = min(1.5, violent_crime_count * 0.5)

    # Age adjustment
    age_adjustment = max(0.5, 1.0 - (age / 100))

    # Final score
    final_score = (base_score * repeat_offender_weight + frequency_component + violent_crime_bonus) * age_adjustment
    return min(10.0, round(final_score, 1))

# Generate Random Date within a range
def random_date(start_year=2020, end_year=2023):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

# Generate Locations with hotspot markers
locations = []
location_id_gen = IDGenerator("L")
for i in range(1, NUM_RECORDS//2 + 1):
    city = random.choice(list(CITIES.keys()))
    area = random.choice(CITIES[city]["areas"])
    lat = round(random.uniform(*CITIES[city]["lat_range"]), 6)
    lon = round(random.uniform(*CITIES[city]["lon_range"]), 6)
    locations.append({
        "LocationID": location_id_gen.generate_id(),
        "City": city,
        "Area": area,
        "Latitude": lat,
        "Longitude": lon,
        "IsHotspot": area in CITIES[city].get("crime_hotspots", [])
    })
df_locations = pd.DataFrame(locations)

# Generate Suspects with enhanced attributes
suspect_id_gen = IDGenerator("S")
suspects = []
suspect_crimes = defaultdict(list)

for i in range(1, NUM_RECORDS//2 + 1):
    gender = random.choice(["Male", "Female"])
    first_name = fake.first_name_male() if gender == "Male" else fake.first_name_female()
    last_name = random.choice(indian_castes)
    age = random.choices([18, 25, 35, 45, 55, 65], weights=[0.1, 0.2, 0.3, 0.2, 0.15, 0.05])[0]
    
    # More accurate age calculation
    birth_year = datetime.now().year - age
    dob = datetime(birth_year, random.randint(1, 12), random.randint(1, 28))
    
    suspect_id = suspect_id_gen.generate_id()
    is_one_time = random.random() < 0.3
    
    # Gang affiliation (20% chance)
    gang = None
    if random.random() < 0.2:
        city = random.choice(list(GANGS.keys()))
        gang = random.choice(GANGS[city])
    
    suspects.append({
        "SuspectID": suspect_id,
        "Name": f"{first_name} {last_name}",
        "Age": age,
        "DOB": dob.strftime("%Y-%m-%d"),
        "Gender": gender,
        "RiskScore": 0,  # Will be calculated
        "OffenseType": "One-time" if is_one_time else "Recurring",
        "Caste": last_name,
        "CommunityInfluenceLevel": random.choice(["Low", "Medium", "High"]),
        "GangAffiliation": gang
    })
df_suspects = pd.DataFrame(suspects)

# Generate Crime Records with all attributes
crime_id_gen = IDGenerator("C")
mo_id_gen = IDGenerator("MO")
evidence_id_gen = IDGenerator("E")
mo_manager = MOPatternManager()

crime_records = []
mo_details = []
crime_frequencies = defaultdict(lambda: defaultdict(int))
victims = []
evidence = []
crime_patterns = []

for i in range(1, NUM_RECORDS + 1):
    crime_type = random.choices(
        list(CRIME_TYPES.keys()),
        weights=[0.1, 0.15, 0.15, 0.1, 0.2, 0.1, 0.1, 0.05, 0.05]
    )[0]
    
    suspect = df_suspects.sample(1).iloc[0]
    suspect_id = suspect["SuspectID"]
    location = df_locations.sample(1).iloc[0]
    location_id = location["LocationID"]
    crime_date = random_date()
    
    # Generate crime description
    crime_desc = random.choice(CRIME_TYPES[crime_type]["desc"])
    crime_desc = f"{crime_desc} in {location['Area']}, {location['City']}"

    # Generate MO Description
    mo_desc = mo_manager.get_pattern(crime_type)

    # Generate weapon used
    weapon = random.choice(WEAPONS[crime_type])

    # Create crime record
    crime_id = crime_id_gen.generate_id()
    crime_records.append({
        "CrimeID": crime_id,
        "CrimeType": crime_type,
        "CrimeDate": crime_date.strftime("%Y-%m-%d"),
        "CrimeDescription": crime_desc,
        "SuspectID": suspect_id,
        "LocationID": location_id,
        "MODescription": mo_desc,
        "WeaponUsed": weapon,
        "SeverityScore": CRIME_TYPES[crime_type]["severity"],
        "RecencyWeight": CRIME_TYPES[crime_type]["recency"],
        "IsHotspot": location["IsHotspot"]
    })

    # Track crimes for risk calculation
    suspect_crimes[suspect_id].append({
        "type": crime_type,
        "date": crime_date
    })

    # MO Details
    mo_id = mo_id_gen.generate_id()
    mo_details.append({
        "MOID": mo_id,
        "CrimeID": crime_id,
        "MODescription": mo_desc,
        "MOCategory": crime_type,
        "WeaponUsed": weapon,
        "SeverityImpact": CRIME_TYPES[crime_type]["severity"],
        "IsGangRelated": suspect["GangAffiliation"] is not None
    })

    # Crime Frequency
    crime_frequencies[suspect_id][crime_type] += 1

    # Generate Victim
    victims.append({
        "VictimID": f"V{i:04d}",
        "CrimeID": crime_id,
        "Name": fake.name(),
        "Age": random.randint(18, 70),
        "Gender": random.choice(["Male", "Female"]),
        "InjurySeverity": random.choices(
            ["Fatal", "Major", "Minor", "No Injury"],
            weights=[0.1 if crime_type == "Murder" else 0.05, 0.3, 0.4, 0.25]
        )[0],
        "CrimeSeverity": CRIME_TYPES[crime_type]["severity"],
        "IsForeigner": random.random() < 0.1  # 10% chance victim is foreigner
    })

    # Generate Evidence
    evidence_types = {
        "Murder": ["Blood-stained clothes", "Murder weapon", "Fingerprints", "DNA samples", "CCTV footage"],
        "Robbery": ["CCTV footage", "Stolen items", "Vehicle used", "Gloves left behind"],
        # ... [other crime types with their evidence]
    }
    evidence_id = evidence_id_gen.generate_id()
    evidence.append({
        "EvidenceID": evidence_id,
        "CrimeID": crime_id,
        "Type": random.choice(["Physical", "Digital", "Biological", "Documentary"]),
        "Description": random.choice(evidence_types.get(crime_type, ["General evidence"])),
        "CrimeSeverity": CRIME_TYPES[crime_type]["severity"],
        "ForensicValue": random.choices(["High", "Medium", "Low"], weights=[0.3, 0.5, 0.2])[0]
    })

    # Crime Pattern
    crime_patterns.append({
        "PatternID": f"P{i:04d}",
        "SuspectID": suspect_id,
        "CrimeID": crime_id,
        "PatternDate": crime_date.strftime("%Y-%m-%d"),
        "CrimeType": crime_type,
        "SeverityScore": CRIME_TYPES[crime_type]["severity"],
        "RecencyImpact": CRIME_TYPES[crime_type]["recency"],
        "LocationPattern": location["Area"],
        "WeaponPattern": weapon,
        "CityPattern": location["City"],
        "IsHotspot": location["IsHotspot"]
    })

# Calculate Risk Scores with new formula
risk_scores = []
for suspect_id, crimes in suspect_crimes.items():
    suspect = df_suspects[df_suspects["SuspectID"] == suspect_id].iloc[0]
    age = suspect["Age"]
    is_one_time = suspect["OffenseType"] == "One-time"
    score = calculate_risk_score(crimes, age, is_one_time)
    
    risk_scores.append({
        "SuspectID": suspect_id,
        "RiskScore": score,
        "CalculationDate": datetime.now().strftime("%Y-%m-%d"),
        "SeverityComponent": round(sum(CRIME_TYPES[c["type"]]["severity"] for c in crimes), 1),
        "RecencyComponent": round(sum(math.exp(-(datetime.now() - c["date"]).days / 365) for c in crimes), 1),
        "CrimeCount": len(crimes),
        "ViolentCrimeCount": sum(1 for c in crimes if c["type"] in ["Murder", "Robbery", "Assault"]),
        "GangAffiliated": suspect["GangAffiliation"] is not None,
        "CommunityInfluence": suspect["CommunityInfluenceLevel"]
    })
    
    # Update suspect data
    idx = df_suspects[df_suspects["SuspectID"] == suspect_id].index[0]
    df_suspects.at[idx, "RiskScore"] = score
    df_suspects.at[idx, "CriminalHistory"] = ", ".join(
        f"{c['type']} ({CRIME_TYPES[c['type']]['severity']}S, {(datetime.now() - c['date']).days}d ago)"
        for c in crimes
    )
    df_suspects.at[idx, "TotalCrimes"] = len(crimes)

# Generate all DataFrames
df_risk_scores = pd.DataFrame(risk_scores)
df_crime_records = pd.DataFrame(crime_records)
df_mo_details = pd.DataFrame(mo_details)
df_victims = pd.DataFrame(victims)
df_evidence = pd.DataFrame(evidence)
df_crime_patterns = pd.DataFrame(crime_patterns)

# Crime Frequency with severity scores
df_crime_freq = pd.DataFrame([
    {"SuspectID": sid, "CrimeType": ct, "CrimeCount": cc, 
     "SeverityScore": CRIME_TYPES[ct]["severity"], "RecencyWeight": CRIME_TYPES[ct]["recency"]}
    for sid, crimes in crime_frequencies.items()
    for ct, cc in crimes.items()
])

# Risk Factors
df_risk_factors = pd.DataFrame([
    {
        "FactorID": f"F{i:04d}",
        "CrimeType": crime_type,
        "SeverityWeight": factors["severity"],
        "RecencyWeight": factors["recency"],
        "Description": random.choice(factors["desc"]),
        "CommonWeapons": ", ".join(WEAPONS.get(crime_type, ["Unknown"])[:50]),  # Truncate if long
        "CommonLocations": random.choice(list(CITIES.keys()))  # Example common location
    }
    for i, (crime_type, factors) in enumerate(CRIME_TYPES.items(), 1)
])

# Save all files to specified backend/data path
df_locations.to_csv(f"{DATASET_PATH}locations.csv", index=False)
df_suspects.to_csv(f"{DATASET_PATH}suspects.csv", index=False)
df_crime_records.to_csv(f"{DATASET_PATH}crime_records.csv", index=False)
df_mo_details.to_csv(f"{DATASET_PATH}mo_details.csv", index=False)
df_victims.to_csv(f"{DATASET_PATH}victims.csv", index=False)
df_evidence.to_csv(f"{DATASET_PATH}evidence.csv", index=False)
df_crime_patterns.to_csv(f"{DATASET_PATH}crime_pattern_history.csv", index=False)
df_crime_freq.to_csv(f"{DATASET_PATH}crime_frequency.csv", index=False)
df_risk_scores.to_csv(f"{DATASET_PATH}risk_scores.csv", index=False)
df_risk_factors.to_csv(f"{DATASET_PATH}risk_factors.csv", index=False)

print(f"✅ All data files generated successfully in {DATASET_PATH} with enhanced Tamil Nadu crime dataset!")