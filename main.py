import pandas as pd
import json
import os

review_file = "output/review_queue.csv"

if os.path.exists(review_file):
    os.remove(review_file)
    
from src.schema_validator import match_schema

from src.remediation import (
    auto_fix_schema,
    handle_nulls,
    remove_duplicates,
    validate_age
)

from src.risk_engine import (
    calculate_risk,
    get_risk_level
)

# --------------------------------------------------
# Load Canonical Schema
# --------------------------------------------------

with open(
    "configs/canonical_schema.json",
    "r"
) as f:

    schema = json.load(f)

# --------------------------------------------------
# Load Source File
# --------------------------------------------------

df = pd.read_csv(
    "data/customer.csv"
)

print("\nOriginal Columns")
print(df.columns.tolist())

# --------------------------------------------------
# Expected Schema
# --------------------------------------------------

target_cols = list(
    schema.keys()
)

# --------------------------------------------------
# Schema Matching
# --------------------------------------------------

matches = match_schema(
    df.columns.tolist(),
    target_cols
)

print("\nSchema Mapping")

for source_col, details in matches.items():

    confidence = details["confidence"]

    target_col = details["matched_column"]

    risk = calculate_risk(
        issue_type="SCHEMA_ALIAS",
        column_name=target_col,
        confidence=confidence
    )

    action = get_risk_level(
        risk
    )

    print(
        f"{source_col}"
        f" -> "
        f"{target_col}"
        f" | confidence={confidence}"
        f" | risk={risk}"
        f" | action={action}"
    )

# --------------------------------------------------
# Schema Auto Remediation
# --------------------------------------------------

df = auto_fix_schema(
    df,
    matches
)

# --------------------------------------------------
# Null Validation
# --------------------------------------------------

df, review_issues = handle_nulls(
    df,
    schema
)

if review_issues:

    print("\nReview Issues")

    for issue in review_issues:

        risk = calculate_risk(
            issue_type="NULL_MANDATORY",
            column_name="customer_email",
            confidence=0.1
        )

        action = get_risk_level(
            risk
        )

        print(
            f"{issue}"
            f" | risk={risk}"
            f" | action={action}"
        )

# --------------------------------------------------
# Duplicate Analysis
# --------------------------------------------------

print("\nBefore Dedup")
print(df)

print("\nDuplicate Count")
print(df.duplicated().sum())

df = df.drop_duplicates()

print("\nAfter Dedup")
print(df)

print("\nRow Count")
print(len(df))

# --------------------------------------------------
# Invalid Age Validation
# --------------------------------------------------

df = validate_age(df)

# --------------------------------------------------
# Final Output
# --------------------------------------------------

print("\nFinal Columns")

print(
    df.columns.tolist()
)

print(
    "\nFinal Record Count:",
    len(df)
)

print("\nFinal Dataset")

print(df)

# --------------------------------------------------
# Save Output
# --------------------------------------------------

df.to_csv(
    "data/customer_fixed.csv",
    index=False
)

print(
    "\nOutput saved successfully."
)