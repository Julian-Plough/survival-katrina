# 00_config.py
# Central configuration file - all paths and constants in one place.
# Edit DATA_ROOT to match wherever your Samsung T5 is mounted.

from pathlib import Path

# ─── Root Paths ───────────────────────────────────────────────
DATA_ROOT = Path("D:/Dissertation(!)/Paper 3")
REPO_ROOT = Path("D:/Survival Analysis 2026/survival-katrina")

# ─── Input Data ───────────────────────────────────────────────
RAW_DIR        = REPO_ROOT / "data" / "raw"
EXTERNAL_DIR   = REPO_ROOT / "data" / "external"
PROCESSED_DIR  = REPO_ROOT / "data" / "processed"

# ─── Source Files ─────────────────────────────────────────────
CAUSAL_DATASET    = DATA_ROOT / "tenure_records" / "causal_dataset.dta"
TRACT_SPATIAL     = DATA_ROOT / "tract_spatial.dta"
CENSUS_1990       = DATA_ROOT / "1990_census.dta"
CENSUS_2000       = DATA_ROOT / "2000_census.dta"
CENSUS_2010       = DATA_ROOT / "2010_census.dta"
CENSUS_HO_2000    = DATA_ROOT / "2000_census_homeowner.dta"
CENSUS_HO_2010    = DATA_ROOT / "2010_census_homeowner.dta"
INFLATION         = DATA_ROOT / "inflation_6_21.dta"

# ─── Output ───────────────────────────────────────────────────
FIGURES_DIR    = REPO_ROOT / "outputs" / "figures"
TABLES_DIR     = REPO_ROOT / "outputs" / "tables"

# ─── Key Dates (Stata date format = days since Jan 1 1960) ────
KATRINA_DATE   = 16677       # August 29 2005
CENSUS_END     = 22281       # January 1 2021

# ─── Model Constants ──────────────────────────────────────────
PERCENTILE_TRIM = (1, 99)
FEMA_CATEGORIES = [0, 100, 500]
RANDOM_SEED     = 42