import pandas as pd

def profile_data(df):
    print(df.isnull().sum())
    return df.describe(include="all")
