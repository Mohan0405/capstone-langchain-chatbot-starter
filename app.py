import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from langchain.chains import RetrievalQA
from langchain.embeddings import CohereEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Cohere

# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY is not set. Please add it to your .env file.")

# Initialize Flask
app = Flask(__name__)

# Global variable for the QA chain
qa = None

def load_db():
    """
    Load the persisted Chroma vector store and return a RetrievalQA chain.
    """
    try:
        embeddings = CohereEmbeddings(cohere_api_key=COHERE_API_KEY)
        vectordb = Chroma(
            persist_directory='db',
            embedding_function=embeddings
        )
        qa_chain = RetrievalQA.from_chain_type(
            llm=Cohere(cohere_api_key=COHERE_API_KEY),
            chain_type="refine",
            retriever=vectordb.as_retriever(),
            return_source_documents=True
        )
        print("✅ Vector DB loaded successfully.")
        return qa_chain
    except Exception as e:
        print("❌ Error loading vector DB:", e)
        return None

def answer_from_knowledgebase(message: str) -> str:
    """
    Get an answer from the vector store using the QA chain.
    """
    if qa is None:
        return "Knowledgebase is not available. Please check the backend logs."

    try:
        result = qa({"query": message})
        return result['result']
    except Exception as e:
        print("❌ Error during QA:", e)
        return "An error occurred while processing your request."

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", title="Knowledgebase Chatbot")

@app.route("/kbanswer", methods=["POST"])
def kbanswer():
    """
    Endpoint to handle POST requests for knowledgebase Q&A.
    """
    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"error": "Missing 'message' in request."}), 400

    answer = answer_from_knowledgebase(message)
    return jsonify({"message": answer}), 200
@app.route("/answer", methods=["POST"])
def answer():
    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"error": "Missing 'message' in request."}), 400

    # Example simple echo or LLM call
    response = f"You asked: {message}"  # Replace with actual Cohere/LLM logic
    return jsonify({"message": response}), 200

if __name__ == "__main__":
    qa = load_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
