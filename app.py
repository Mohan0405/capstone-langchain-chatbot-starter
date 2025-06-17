import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from langchain.chains import RetrievalQA, ConversationChain
from langchain.embeddings import CohereEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Cohere
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory

# Load environment variables
print("🔄 Starting app...")
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    print("❌ COHERE_API_KEY is missing!")
    raise ValueError("COHERE_API_KEY is not set. Please add it in .env or Render env vars.")

print("🔑 COHERE_API_KEY loaded.")

# Initialize Flask
app = Flask(__name__)

# Load knowledgebase vector store
def load_db():
    try:
        print("⚙️ Loading vector DB...")
        embeddings = CohereEmbeddings(cohere_api_key=COHERE_API_KEY)
        vectordb = Chroma(persist_directory='db', embedding_function=embeddings)
        qa_chain = RetrievalQA.from_chain_type(
            llm=Cohere(cohere_api_key=COHERE_API_KEY),
            chain_type="refine",
            retriever=vectordb.as_retriever(),
            return_source_documents=True
        )
        print("✅ Vector DB loaded.")
        return qa_chain
    except Exception as e:
        print("❌ Error loading vector DB:", e)
        return None

# Initialize chatbot chain
def init_chatbot():
    try:
        print("⚙️ Initializing chatbot...")
        llm = Cohere(cohere_api_key=COHERE_API_KEY)
        memory = ConversationBufferMemory()
        prompt = ChatPromptTemplate.from_template(
            "You are a helpful assistant.\n\n{history}\nHuman: {input}\nAssistant:"
        )
        chain = ConversationChain(llm=llm, memory=memory, prompt=prompt)
        print("✅ Chatbot initialized.")
        return chain
    except Exception as e:
        print("❌ Error initializing chatbot:", e)
        return None

# Global chains (must run on cold start, including on Render)
qa = load_db()
chatbot_chain = init_chatbot()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", title="Thinkbot AI")

@app.route("/answer", methods=["POST"])
def answer():
    data = request.get_json()
    message = data.get("message")
    if not message:
        return jsonify({"error": "Missing 'message'"}), 400
    if not chatbot_chain:
        return jsonify({"message": "❌ Chatbot is not available."}), 500
    try:
        response = chatbot_chain.predict(input=message)
        return jsonify({"message": response}), 200
    except Exception as e:
        print("❌ Chatbot Error:", e)
        return jsonify({"message": "Chatbot error occurred"}), 500

@app.route("/kbanswer", methods=["POST"])
def kbanswer():
    data = request.get_json()
    message = data.get("message")
    if not message:
        return jsonify({"error": "Missing 'message'"}), 400
    if not qa:
        return jsonify({"message": "❌ Knowledgebase is not available."}), 500
    try:
        result = qa({"query": message})
        return jsonify({"message": result['result']}), 200
    except Exception as e:
        print("❌ Knowledgebase Error:", e)
        return jsonify({"message": "Knowledgebase error occurred"}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "qa_ready": qa is not None,
        "chatbot_ready": chatbot_chain is not None
    })

# DO NOT include `if __name__ == "__main__"` for Render
