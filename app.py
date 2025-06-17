import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from langchain.chat_models import ChatCohere
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise ValueError("Missing COHERE_API_KEY in .env file")

# Initialize Flask
app = Flask(__name__)

# Set up LangChain components
llm = ChatCohere(cohere_api_key=COHERE_API_KEY)
memory = ConversationBufferMemory()
chat_prompt = ChatPromptTemplate.from_template(
    "You are a helpful assistant.\n\nConversation history:\n{history}\nHuman: {input}\nAssistant:"
)
chat_chain = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=chat_prompt
)

# --- Core Logic ---

def answer_as_chatbot(message: str) -> str:
    try:
        return chat_chain.predict(input=message)
    except Exception as e:
        return f"An error occurred while generating the response: {str(e)}"

def answer_from_knowledgebase(message: str) -> str:
    # Placeholder for knowledgebase Q&A logic
    return "Knowledgebase answering is not implemented yet."

def search_knowledgebase(message: str) -> str:
    # Placeholder for knowledgebase search logic
    return "Knowledgebase search is not implemented yet."

# --- Routes ---

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", title="Cohere Chatbot")

@app.route("/answer", methods=["POST"])
def answer():
    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"error": "Missing 'message' in request"}), 400

    response = answer_as_chatbot(message)
    return jsonify({"message": response}), 200

@app.route("/kbanswer", methods=["POST"])
def kbanswer():
    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"error": "Missing 'message' in request"}), 400

    response = answer_from_knowledgebase(message)
    return jsonify({"message": response}), 200

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"error": "Missing 'message' in request"}), 400

    sources = search_knowledgebase(message)
    return jsonify({"sources": sources}), 200

# --- Run Server ---
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

