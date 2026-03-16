"""
Data Router
Chooses the best engine depending on the data source and size
"""

def choose_engine(source_type, file_size_mb):

    # Streaming data
    if source_type == "stream":
        return "kafka"

    # Local small datasets
    if file_size_mb < 500:
        return "duckdb"

    # Medium big data
    if file_size_mb < 5000:
        return "spark"

    # Very large datasets
    return "spark_cluster"