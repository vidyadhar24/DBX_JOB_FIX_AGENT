from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# ==========================================
# 1. THE TRANSLATOR (Embedding Model)
# ==========================================
# We use 'all-MiniLM-L6-v2'. It is a standard, lightweight, 
# open-source model that translates text into embeddings instantly on your CPU.
print("Loading embedding model (this may take a few seconds to download the first time)...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ==========================================
# 2. THE KNOWLEDGE (Our Saved Solutions)
# ==========================================
# We wrap our text in "Document" objects. This is the standard format ChromaDB expects.
# In a massive enterprise system, these would be loaded from thousands of PDFs or wikis.
print("Drafting known PySpark error solutions...")
known_errors = [
    Document(
        page_content="""Error Pattern: AnalysisException: Cannot resolve column name. 
        Cause: A column referenced in a select(), filter(), or join() does not exist in the DataFrame schema. 
        Fix: Double-check the exact spelling and capitalization of the column name. Use df.printSchema() to verify the available columns before the operation.""",
        metadata={"error_type": "schema_mismatch"}
    ),
    Document(
        page_content="""Error Pattern: java.lang.OutOfMemoryError: Java heap space. 
        Cause: Spark ran out of memory trying to process a partition that is too large, often during a massive shuffle like a join or groupBy. 
        Fix: Increase spark.executor.memory, or handle data skew by salting the keys. You can also try increasing the number of shuffle partitions using spark.sql.shuffle.partitions.""",
        metadata={"error_type": "out_of_memory"}
    ),
     Document(
        page_content="""Error Pattern: java.lang.NullPointerException when calling String methods. 
        Cause: You are applying a string function to a column that contains null values without filtering them out first. 
        Fix: Filter out nulls using df.filter(col('column_name').isNotNull()) before applying the transformation, or use na.fill() to provide a default safe value.""",
        metadata={"error_type": "null_value"}
    )
]

# ==========================================
# 3. THE DATABASE (ChromaDB)
# ==========================================
# We pass our documents and our translator into Chroma, 
# and tell it to save the resulting database to a physical folder.
print("Building and saving the local vector database...")
vector_store = Chroma.from_documents(
    documents=known_errors,
    embedding=embeddings,
    persist_directory="./chroma_db"  # This creates a folder named 'chroma_db'
)

print("\nSuccess! Knowledge base built and saved to the './chroma_db' directory.")