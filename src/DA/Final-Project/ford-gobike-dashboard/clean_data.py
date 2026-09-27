"""
Step 1 - Data cleaning for Ford GoBike (Feb 2019).
Run:  python clean_data.py
Input : fordgobike-tripdataFor201902.csv
Output: fordgobike_clean.csv
"""
import pandas as pd

RAW = "fordgobike-tripdataFor201902.csv"
OUT = "fordgobike_clean.csv"

df = pd.read_csv(RAW)
print("Raw shape:", df.shape)

# 1) Missing values -> drop rows (same approach as the notebook)
df = df.dropna(subset=["start_station_id", "start_station_name",
                       "end_station_id", "end_station_name"])
df = df.dropna(subset=["member_birth_year", "member_gender"])

# 2) Duplicates
print("Duplicate rows:", df.duplicated().sum())
df = df.drop_duplicates()

# 3) Data types
for col in ["start_station_id", "end_station_id", "member_birth_year"]:
    df[col] = df[col].astype(int)
for col in ["user_type", "member_gender", "bike_share_for_all_trip"]:
    df[col] = df[col].astype("category")

# 4) New columns
df["age"] = 2019 - df["member_birth_year"]
df["duration_min"] = df["duration_sec"] / 60
df["duration_hour"] = df["duration_sec"] / 3600

# 5) Outliers: implausible ages (birth years back to 1878 -> ages up to 141)
before = len(df)
df = df[df["age"] <= 80]
print("Removed age outliers (>80):", before - len(df))

# 6) start_time / end_time: in the uploaded file they are corrupted (only
#    'mm:ss.f' survived, date and hour were lost - typical Excel damage).
#    If your copy has full timestamps they are kept and the dashboard unlocks
#    the time features (daily trend, peak hour, day filter, heatmap).
if df["start_time"].astype(str).str.len().median() <= 12:
    print("start_time is corrupted -> dropping time columns")
    df = df.drop(columns=["start_time", "end_time"])
else:
    print("start_time looks valid -> keeping it")

df.to_csv(OUT, index=False)
print("Clean shape:", df.shape)
print(df.isna().sum().sum(), "missing values left")
