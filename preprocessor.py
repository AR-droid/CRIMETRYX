import pandas as pd
import os

# Define file paths
data_folder = "backend/data"
crime_file = os.path.join(data_folder, "crime_records.csv")
mo_file = os.path.join(data_folder, "mo_details.csv")
crime_pattern_file = os.path.join(data_folder, "crime_pattern_history.csv")
crime_frequency_file = os.path.join(data_folder, "crime_frequency.csv")
processed_data_file = os.path.join(data_folder, "processed_data.pkl")

# Load datasets
crime_df = pd.read_csv(crime_file)
mo_df = pd.read_csv(mo_file)
crime_patterns = pd.read_csv(crime_pattern_file)
crime_frequency = pd.read_csv(crime_frequency_file)

# Handle missing values
crime_df.fillna("Unknown", inplace=True)
mo_df.fillna("Unknown", inplace=True)
crime_patterns.fillna("Unknown", inplace=True)
crime_frequency.fillna(0, inplace=True)

# Normalize text data
def clean_text(text):
    return text.lower().strip().replace("\n", " ") if isinstance(text, str) else "Unknown"

crime_df["CrimeType"] = crime_df["CrimeType"].apply(clean_text)
mo_df["MODescription"] = mo_df["MODescription"].apply(clean_text)

# Merge datasets
merged_df = pd.merge(crime_df, mo_df, on="CrimeID", how="left")
merged_df = pd.merge(merged_df, crime_frequency, on="SuspectID", how="left")
merged_df.fillna("Unknown", inplace=True)

# Save preprocessed data
merged_df.to_pickle(processed_data_file)
print("Data preprocessing completed and saved!")
