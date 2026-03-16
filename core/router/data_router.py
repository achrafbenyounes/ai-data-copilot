import pandas as pd
import duckdb
from pyspark.sql import SparkSession

def choose_engine(source_type: str, file_size_mb: float, df: pd.DataFrame = None):
    """
    Chooses the best engine and executes optional transformations
    Returns engine name and possibly transformed dataframe
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
            # DuckDB in-memory execution
            con = duckdb.connect(database=':memory:')
            con.register('dataset', df)
            # Example: simple query to test engine
            transformed_df = con.execute("SELECT * FROM dataset").df()
        elif engine.startswith("spark"):
            # Spark session execution
            spark = SparkSession.builder.master("local[*]").appName("AIDataCopilot").getOrCreate()
            transformed_df = spark.createDataFrame(df)

    return engine, transformed_df