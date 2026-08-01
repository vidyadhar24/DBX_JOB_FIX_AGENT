SPARK_ERRORS = {
    "schema_mismatch": """
        org.apache.spark.sql.AnalysisException: Cannot resolve column name "customer_id" among (cust_id, name, age, signup_date). 
        To correct this, you can selectively choose the correct columns or rename the existing columns.
    """,
    
    "out_of_memory": """
        java.lang.OutOfMemoryError: Java heap space
        at org.apache.spark.util.collection.unsafe.sort.UnsafeExternalSorter.growPointerArrayIfNecessary(UnsafeExternalSorter.java:135)
        at org.apache.spark.sql.execution.UnsafeExternalRowSorter.insertRow(UnsafeExternalRowSorter.java:94)
    """,
    
    "null_value": """
        org.apache.spark.SparkException: Job aborted due to stage failure: Task 0 in stage 2.0 failed 4 times, most recent failure: 
        Lost task 0.3 in stage 2.0 (TID 15, executor 1): java.lang.NullPointerException: 
        Cannot invoke "String.length()" because the return value of "org.apache.spark.sql.Row.getString(int)" is null.
    """
}