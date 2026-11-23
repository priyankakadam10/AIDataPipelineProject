import pandas as pd
import os


from src.risk_engine import (
    calculate_risk,
    get_risk_level
)

from src.audit_logger import log_audit

def auto_fix_schema(df, matches):

    review_queue = []

    print("\nSchema Remediation")

    for source_col, details in matches.items():

        target_col = details["matched_column"]

        confidence = details["confidence"]

        # Column already correct
        if source_col == target_col:
            continue

        risk = calculate_risk(
            issue_type="SCHEMA_ALIAS",
            column_name=target_col,
            confidence=confidence
        )

        action = get_risk_level(risk)

        print(
            f"{source_col} -> {target_col}"
            f" | confidence={confidence}"
            f" | risk={risk}"
            f" | action={action}"
        )

        if confidence >= 0.60:

            df.rename(
                columns={
                    source_col: target_col
                },
                inplace=True
            )
            log_audit(
            issue_type="SCHEMA_ALIAS",
            action="AUTO_FIX",
            details=f"{source_col} -> {target_col}"
)

            print(
                f"Renamed: "
                f"{source_col} -> {target_col}"
            )

        elif action == "REVIEW":

            review_queue.append({
                "source_column":
                    source_col,

                "target_column":
                    target_col,

                "confidence":
                    confidence,

                "risk":
                    risk,

                "action":
                    action
            })

            print(
                f"Review Required: "
                f"{source_col}"
            )

        else:

            print(
                f"Rejected Mapping: "
                f"{source_col}"
            )

    if review_queue:

        pd.DataFrame(
            review_queue
        ).to_csv(
            "output/review_queue.csv",
            index=False
        )

    return df


def handle_nulls(df, schema):

    review_issues = []

    review_rows = []

    for col, rules in schema.items():

        if col not in df.columns:
            continue

        null_rows = df[
            df[col].isna()
        ]

        if null_rows.empty:
            continue

        if rules["mandatory"]:
            log_audit(
                issue_type="NULL_MANDATORY",
                action="REVIEW",
                details=f"{col} contains {len(null_rows)} null values"
            )

            for _, row in null_rows.iterrows():

                review_rows.append({
                    "issue_type":
                        "NULL_MANDATORY",

                    "column_name":
                        col,

                    "value":
                        "NULL",

                    "action":
                        "REVIEW"
                })

            review_issues.append(
                f"{col} contains "
                f"{len(null_rows)} null values"
            )

    if review_rows:

        pd.DataFrame(
            review_rows
        ).to_csv(
            "output/review_queue.csv",
            mode="a",
            header=not os.path.exists(
                "output/review_queue.csv"
            ),
            index=False
        )

    return df, review_issues


def remove_duplicates(df):

    print(
        "INSIDE remove_duplicates()"
    )

    before = len(df)

    duplicate_count = (
        df.duplicated().sum()
    )

    print(
        f"Rows Before: {before}"
    )

    print(
        f"Duplicates Found: "
        f"{duplicate_count}"
    )

    if duplicate_count > 0:

        df = df.drop_duplicates()

        log_audit(
            issue_type="DUPLICATE_ROW",
            action="AUTO_FIX",
            details=f"{duplicate_count} duplicate rows removed"
        )

    after = len(df)

    print(
        f"Rows After: {after}"
    )

    print(
        f"Removed: "
        f"{before-after}"
    )

    return df


def validate_age(df):

    if "customer_age" not in df.columns:
        return df

    invalid_age = df[
        (df["customer_age"] < 0)
        |
        (df["customer_age"] > 120)
    ]

    if not invalid_age.empty:

        print(
            "\nReview Required:"
        )

        print(
            f"{len(invalid_age)} invalid "
            f"age value(s) found"
        )

        log_audit(
            issue_type="INVALID_AGE",
            action="REVIEW",
            details=f"{len(invalid_age)} invalid age records"
        )

        review_df = invalid_age.copy()

        review_df["issue_type"] = (
            "INVALID_AGE"
        )

        review_df["action"] = (
            "REVIEW"
        )

        review_df.to_csv(
            "output/review_queue.csv",
            mode="a",
            header=False,
            index=False
        )

    return df