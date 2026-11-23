import json

with open(
    "configs/risk_rules.json",
    "r"
) as f:

    RULES = json.load(f)


def calculate_risk(
        issue_type,
        column_name,
        confidence):

    severity = (
        RULES["severity"]
        .get(issue_type, 0.5)
    )

    impact = (
        RULES["business_impact"]
        .get(column_name, 0.5)
    )

    confidence_penalty = (
        1 - confidence
    )

    # Schema alias risk

    if issue_type == "SCHEMA_ALIAS":

        risk_score = (
            severity * 0.6
            +
            confidence_penalty * 0.4
        )
        print("SCHEMA_ALIAS FORMULA USED")

    else:

        risk_score = (
            severity * 0.4
            +
            impact * 0.4
            +
            confidence_penalty * 0.2
        )
        print("DEFAULT FORMULA USED")

    return round(
        risk_score,
        3
    )


def get_risk_level(score):

    auto_fix_limit = (
        RULES["thresholds"]
        ["auto_fix"]
    )

    review_limit = (
        RULES["thresholds"]
        ["review"]
    )

    if score <= auto_fix_limit:

        return "AUTO_FIX"

    elif score <= review_limit:

        return "REVIEW"

    else:

        return "REJECT"
