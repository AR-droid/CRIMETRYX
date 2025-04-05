import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from collections import defaultdict
from datetime import datetime

# Load data
df = pd.read_pickle("../data/processed_data.pkl")

# Extract required columns
mo_patterns = df[['MODescription_x', 'CrimeType', 'WeaponUsed_x', 'LocationID', 'SeverityScore']].dropna().drop_duplicates()

# Load unique suspects
suspects = df['SuspectID'].unique()

# Function: fuzzy match score
def fuzzy_match(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Time of day binning
def time_bin(crime_date):
    try:
        hour = pd.to_datetime(crime_date).hour
        if 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 18:
            return 'Afternoon'
        elif 18 <= hour < 21:
            return 'Evening'
        else:
            return 'Night'
    except:
        return 'Unknown'

df['TimeOfDay'] = df['CrimeDate'].apply(time_bin)

# Define dangerous MO examples
high_risk_patterns = {
    'Robbery': ['ATM theft with gas cutter', 'Temple hundi theft during festival', 'Jewelry shop heist with country-made guns', 'Chain snatching using motorbikes'],
    'Assault': ['Honor killing in traditional Tamil style', 'Political murder with local weapons'],
    'Sand Smuggling': ['Fake construction company operations', 'Bribing local officials for permits', 'Threatening local activists'],
    'Theft': ['Cloned SIM cards'],
}

# Group dangerous MO per crime type
pattern_to_weapon = {
    'ATM theft with gas cutter': 'Gas cutter',
    'Temple hundi theft during festival': 'Screwdriver',
    'Jewelry shop heist with country-made guns': 'Country-made pistol',
    'Chain snatching using motorbikes': 'Broken bottle',
    'Honor killing in traditional Tamil style': 'Broken bottle',
    'Political murder with local weapons': 'Broken bottle',
    'Fake construction company operations': 'Boats',
    'Bribing local officials for permits': 'Excavators',
    'Threatening local activists': 'Excavators',
    'Idol theft disguised as renovation work': 'Bamboo stick',
    'Cloned SIM cards': 'Cloned SIM cards',
}

# Group MO by Suspect
suspect_crimes = df.groupby('SuspectID')

results = []
for suspect, group in suspect_crimes:
    descriptions = group['MODescription_x'].dropna().tolist()
    locations = group['LocationID'].dropna().tolist()
    times = group['TimeOfDay'].dropna().tolist()
    risk = group['SeverityScore'].mean() if not group['SeverityScore'].isna().all() else 1

    best_match = None
    best_score = 0
    matched_crime = 'Unknown'
    matched_weapon = 'Unknown'

    for _, pattern in mo_patterns.iterrows():
        mo_text = pattern['MODescription_x']
        loc = pattern['LocationID']
        type_ = pattern['CrimeType']
        weapon = pattern['WeaponUsed_x']
        severity = pattern['SeverityScore']

        for desc in descriptions:
            score = fuzzy_match(desc, mo_text)
            # Boost score for same location
            if loc in locations:
                score += 0.1
            # Boost for time of day matching (future use if MO has time info)
            # Score weighting by severity
            score *= (1 + (severity or 1) / 10)
            score *= (1 + (risk or 1) / 10)

            if score > best_score:
                best_score = score
                best_match = mo_text
                matched_crime = type_
                matched_weapon = weapon

    # Fallback if no match or low score
    if not best_match or best_score < 0.4:
        matched_crime = 'Unknown'
        matched_weapon = 'Unknown'
        best_match = 'No matching pattern found'
    elif best_match in pattern_to_weapon:
        matched_weapon = pattern_to_weapon[best_match]
    else:
        matched_weapon = 'Unknown'

    results.append({
        'SuspectID': suspect,
        'PredictedCrimeType': matched_crime,
        'LikelyWeapon': matched_weapon,
        'MatchedMOExamples': best_match
    })

# Save predictions
pred_df = pd.DataFrame(results)
pred_df.to_csv("../data/rule_based_predictions.csv", index=False)
print("Rule-based predictions with location/risk/time logic saved.")
