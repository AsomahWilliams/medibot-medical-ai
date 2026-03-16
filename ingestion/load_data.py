
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm
import pinecone
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings  # Fixed

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = "us-east-1"
PINECONE_INDEX_NAME = "medicalindex"

UPLOAD_DIR = "./uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

# Create index with dimension 384 (for HuggingFace)
if PINECONE_INDEX_NAME not in pinecone.list_indexes():
    pinecone.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=384,
        metric="cosine"
    )

index = pinecone.Index(PINECONE_INDEX_NAME)

# Load, split, embed, and upsert PDF docs content
def load_vectorstore(uploaded_files):
    embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    file_paths = []

    # Save uploaded files locally
    for file in uploaded_files:
        save_path = Path(UPLOAD_DIR) / file.filename
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        file_paths.append(str(save_path))

    # Process each file
    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [f"{Path(file_path).stem}-{i}" for i in range(len(chunks))]

        print(f" Embedding {len(texts)} chunks...")
        embeddings = embed_model.embed_documents(texts)

        print("Uploading to Pinecone...")
        vectors = list(zip(ids, embeddings, metadatas))
        with tqdm(total=len(vectors), desc="Upserting to Pinecone") as progress:
            index.upsert(vectors=vectors)
            progress.update(len(vectors))

        print(f"✅ Upload complete for {file_path}")