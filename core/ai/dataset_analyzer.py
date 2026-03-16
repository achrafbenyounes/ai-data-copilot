import pandas as pd

def analyze_csv(df: pd.DataFrame):
    """
    Analyze CSV dataset and return a summary dict
    """
    summary = {}

    # Basic info
    summary['num_rows'] = df.shape[0]
    summary['num_columns'] = df.shape[1]

    # Column types
    summary['columns'] = df.dtypes.to_dict()

    # Basic stats
    summary['stats'] = df.describe(include='all').to_dict()

    # Missing values
    summary['missing'] = df.isnull().sum().to_dict()

    # Optional: detect simple outliers for numeric columns
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    outliers = {}
    for col in numeric_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        outliers[col] = ((df[col] < (q1 - 1.5*iqr)) | (df[col] > (q3 + 1.5*iqr))).sum()
    summary['outliers'] = outliers

    return summary