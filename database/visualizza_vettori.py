import chromadb
client = chromadb.PersistentClient(path="data/chroma_db")

# Lista collection
print(client.list_collections())

# Ispeziona una collection
coll = client.get_collection("learnai_tutti")
print(f"Documenti: {coll.count()}")
print(coll.peek())  # primi 10 record
