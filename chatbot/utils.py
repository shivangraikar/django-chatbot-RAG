import faiss
import numpy as np
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import pdfplumber
import os
from dotenv import load_dotenv

load_dotenv()

# Set up the API key
genai.configure(api_key=os.getenv("SECRET_KEY"))

# Load the model for embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize the FAISS index
d = 384  # Dimensionality of the embeddings (depends on your model)
index = faiss.IndexFlatL2(d)  # Using L2 distance (Euclidean)

def extract_text_from_pdf(pdf_file):
    extracted_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() or ""
    return extracted_text

def generate_embeddings(extracted_text):
    chunks = extracted_text.split('\n\n')  # Chunk text by paragraph
    embeddings = [embedding_model.encode(chunk) for chunk in chunks]
    return embeddings

def index_embeddings(embeddings):
    global index
    embeddings_np = np.array(embeddings).astype('float32')
    print(f"Indexing {len(embeddings_np)} embeddings")  # Debug print
    if len(embeddings_np) > 0:
        index.add(embeddings_np)
    else:
        print("No embeddings to index")

def query_embeddings(user_message):
    if not isinstance(user_message, str):
        raise ValueError("Input should be a string")

    user_message_vec = embedding_model.encode([user_message])  # Pass as a list
    user_message_vec = np.array(user_message_vec).astype('float32')
    print(f"Querying with embedding: {user_message_vec}")  # Debug print
    distances, indices = index.search(user_message_vec, k=1)  # k=1 for nearest neighbor
    print(f"Distances: {distances}, Indices: {indices}")  # Debug print
    if indices.size > 0 and indices[0][0] >= 0:
        return indices[0][0]
    return None  # Return None if no valid index is found

def generate_response_from_llm(user_message):
    data = {
        'parts': [{'text': user_message}]
    }
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(data)
        return str(response.text)
    except Exception as e:
        return f'Error retrieving response from LLM: {e}'

def generate_response_based_on_pdf(user_message):
    try:
        query_embedding = embedding_model.encode([user_message])  # Pass as a list
        closest_index = query_embeddings(user_message)

        if closest_index is not None:
            response_text = "Retrieved relevant text based on the query."
        else:
            response_text = "No relevant information found."

        data = {
            'parts': [{'text': response_text}]
        }
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(data)
        return str(response.text)
    except Exception as e:
        return f'Error retrieving response from LLM: {e}'
