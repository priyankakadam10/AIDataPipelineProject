from pyspark.sql.functions import *

from sklearn.ensemble import (
    IsolationForest
)

def detect_anomalies(
        spark_df,
        column):

    pandas_df = (
        spark_df
        .select(column)
        .toPandas()
    )

    model = IsolationForest(
        contamination=0.05,
        random_state=42
    )

    pandas_df["anomaly"] = (
        model.fit_predict(
            pandas_df[[column]]
        )
    )

    return pandas_df