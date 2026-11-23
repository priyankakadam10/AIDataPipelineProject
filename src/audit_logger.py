import pandas as pd
import os
from datetime import datetime


def log_audit(
        issue_type,
        action,
        details):

    audit_record = pd.DataFrame([{

        "timestamp":
            datetime.now(),

        "issue_type":
            issue_type,

        "action":
            action,

        "details":
            details

    }])

    audit_record.to_csv(
        "output/audit_log.csv",
        mode="a",
        header=not os.path.exists(
            "output/audit_log.csv"
        ),
        index=False
    )