from flask import Flask, request, jsonify
import sqlite3
import logging
import anthropic
import faiss
import numpy as np
import os

app = Flask(__name__)

logging.basicConfig(filename='logs/python.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Initialize FAISS index
dimension = 128  # Example dimension for embeddings
index = faiss.IndexFlatL2(dimension)
embeddings = []
metadata = []

def generate_embedding(text):
    # Mock embedding generation (replace with actual embedding model if available)
    return np.random.rand(dimension).astype('float32')

def index_data():
    conn = sqlite3.connect('faces.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, timestamp FROM faces')
    records = cursor.fetchall()
    conn.close()

    global embeddings, metadata
    embeddings = []
    metadata = []
    for name, timestamp in records:
        text = f"{name} was registered at {timestamp}"
        embedding = generate_embedding(text)
        embeddings.append(embedding)
        metadata.append(text)
    if embeddings:
        embeddings = np.array(embeddings)
        index.add(embeddings)

@app.route('/rag', methods=['POST'])
def rag_query():
    data = request.json
    query = data.get('query')

    if not query:
        logging.error('Missing query')
        return jsonify({'message': 'Missing query'}), 400

    try:
        # Generate query embedding
        query_embedding = generate_embedding(query)
        _, indices = index.search(np.array([query_embedding]), k=3)
        context = [metadata[i] for i in indices[0] if i != -1]

        # Query Claude
        prompt = f"Context: {context}\n\nQuery: {query}\nAnswer:"
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.content[0].text

        logging.info(f'Query: {query}, Response: {answer}')
        return jsonify({'response': answer})
    except Exception as e:
        logging.error(f'Error processing query: {str(e)}')
        return jsonify({'message': 'Error processing query'}), 500

if __name__ == '__main__':
    index_data()
    app.run(port=5002)