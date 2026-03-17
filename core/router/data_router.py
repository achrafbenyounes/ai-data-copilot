import pandas as pd
import duckdb

def choose_engine(source_type: str, file_size_mb: float, df: pd.DataFrame = None):
    """
    Chooses the best engine and executes optional transformations.
    Returns engine name and possibly transformed dataframe.

    Note : PySpark est désactivé en production cloud (Streamlit Cloud ne supporte pas Java).
    Pour des fichiers > 500MB, le moteur reste DuckDB.
    """

    engine = None
    transformed_df = df

    # -----------------------
    # Select engine
    # -----------------------
    if source_type == "stream":
        engine = "kafka"
    elif file_size_mb < 500:
        engine = "duckdb"
    elif file_size_mb < 5000:
        engine = "spark_local"
    else:
        engine = "spark_cluster"

    # -----------------------
    # Execute transformations if dataframe provided
    # -----------------------
    if df is not None:
        if engine == "duckdb":
            con = duckdb.connect(database=':memory:')
            con.register('dataset', df)
            transformed_df = con.execute("SELECT * FROM dataset").df()
        elif engine.startswith("spark"):
            # Spark non disponible en cloud — fallback sur DuckDB
            engine = "duckdb"
            con = duckdb.connect(database=':memory:')
            con.register('dataset', df)
            transformed_df = con.execute("SELECT * FROM dataset").df()

    return engine, transformed_df