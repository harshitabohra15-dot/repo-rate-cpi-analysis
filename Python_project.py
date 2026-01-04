import pandas as pd

# STEP 1: Read CSV
repo = pd.read_csv(
    "repo_rate.csv",
    header=3,          # row 4 = column names
    skiprows=[4, 5]    # skip junk rows after header
)

# STEP 2: Clean column names
repo.columns = repo.columns.str.strip()

# STEP 3: Keep only required columns
repo = repo[["Date of Announcement", "Repo Rate (Per cent)"]]

# STEP 4: Rename columns
repo = repo.rename(columns={
    "Date of Announcement": "date",
    "Repo Rate (Per cent)": "repo_rate"
})

# STEP 5: FORCE date conversion (critical fix)
repo["date"] = pd.to_datetime(
    repo["date"],
    dayfirst=True,
    errors="coerce"   # invalid strings → NaT
)

# STEP 6: Drop rows where date is invalid (notes, text, blanks)
repo = repo.dropna(subset=["date"])

# STEP 7: Convert repo_rate to numeric (safe)
repo["repo_rate"] = pd.to_numeric(repo["repo_rate"], errors="coerce")

# STEP 8: Sort & set index
repo = repo.sort_values("date")
repo = repo.set_index("date")

# STEP 9: Convert to monthly series
monthly_repo = repo.resample("M").ffill()

# STEP 10: Final formatting
monthly_repo = monthly_repo.reset_index()
monthly_repo["month"] = monthly_repo["date"].dt.to_period("M")
monthly_repo = monthly_repo[["month", "repo_rate"]]


# STEP 12: Save cleaned data
monthly_repo.to_csv("monthly_repo_rate.csv", index=False)




# Load CPI data
cpi = pd.read_csv("CPI_index.csv")

# Inspect columns
print(cpi.columns)
print(cpi.head())


import pandas as pd



cpi = pd.read_csv("CPI_index.csv", skiprows=1)
cpi = cpi[["Year", "Month", "Combined"]]
cpi = cpi.rename(columns={"Combined": "cpi"})


cpi["date"] = pd.to_datetime(
    cpi["Year"].astype(str) + "-" + cpi["Month"].astype(str),
    errors="coerce"
)

cpi["Month"] = cpi["date"].dt.to_period("M")
cpi["cpi"] = pd.to_numeric(cpi["cpi"], errors="coerce")

cpi = cpi.dropna(subset=["Month", "cpi"])
cpi = cpi.sort_values("Month")

cpi = cpi[["Month", "cpi"]]

print(cpi.head(12))

cpi.to_csv("monthly_cpi_cleaned.csv", index=False)



import pandas as pd
cpi=pd.read_csv("monthly_cpi_cleaned.csv")
cpi.rename(columns={'Month': 'month'}, inplace=True)
cpi.to_csv("monthly_cpi_cleaned.csv", index=False)



import pandas as pd

repo = pd.read_csv("monthly_repo_rate.csv")
cpi = pd.read_csv("monthly_cpi_cleaned.csv")

# Convert month to Period[M]
repo["month"] = pd.PeriodIndex(repo["month"], freq="M")
cpi["month"] = pd.PeriodIndex(cpi["month"], freq="M")

# INNER merge → keeps only overlapping months
final_df = repo.merge(cpi, on="month", how="inner")

final_df = final_df.sort_values("month")

print(final_df.head())
print(final_df.tail())






import matplotlib.pyplot as plt

final_df["month_dt"] = final_df["month"].dt.to_timestamp()

plt.figure(figsize=(12,4))

# CPI
plt.subplot(1,2,1)
plt.plot(final_df["month_dt"], final_df["cpi"])
plt.title("CPI Index Over Time")
plt.xlabel("Time")
plt.ylabel("CPI Index")

# Repo rate
plt.subplot(1,2,2)
plt.plot(final_df["month_dt"], final_df["repo_rate"])
plt.title("Repo Rate Over Time")
plt.xlabel("Time")
plt.ylabel("Repo Rate (%)")

plt.tight_layout()
plt.show()
