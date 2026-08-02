from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# 1. Load the exact same embedding model used to build the DB
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 2. Load the existing vector database from disk
vector_store = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

print("=== 1. ALL STORED CONTENTS ===")
# .get() pulls all raw records directly from ChromaDB
all_data = vector_store.get()

for idx, (doc, meta) in enumerate(zip(all_data["documents"], all_data["metadatas"]), 1):
    print(f"\n[Record {idx}] Error Type: {meta.get('error_type')}")
    print(f"Content:\n{doc.strip()}")
    print("-" * 50)


print("\n=== 2. SEMANTIC SIMILARITY SEARCH TEST ===")
# Example: Query with a brand new phrase that isn't an exact match
user_query = "My job crashed because a field called 'user_id' was not found in the dataframe"
print(f"User Query: '{user_query}'\n")

# Retrieve the top 1 most relevant match (k=1)
results = vector_store.similarity_search(user_query, k=1)

if results:
    top_match = results[0]
    print(f"Top Match Found (Type: {top_match.metadata.get('error_type')}):")
    print(top_match.page_content.strip())