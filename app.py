import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from langchain.chains import RetrievalQA, ConversationChain
from langchain.embeddings import CohereEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Cohere
from langchain.chat_models import ChatCohere
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY is not set. Please add it to your .env file.")

# Initialize Flask
app = Flask(__name__)

# Global variables
qa = None
chatbot_chain = None

# Load vector DB for knowledgebase
def load_db():
    try:
        embeddings = CohereEmbeddings(cohere_api_key=COHERE_API_KEY)
        vectordb = Chroma(persist_directory='db', embedding_function=embeddings)
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

# Initialize chatbot conversation chain
def init_chatbot():
    llm = ChatCohere(cohere_api_key=COHERE_API_KEY)
    memory = ConversationBufferMemory()
    prompt = ChatPromptTemplate.from_template(
        "You are a friendly, helpful AI assistant.\n\n{history}\nHuman: {input}\nAssistant:"
    )
    return ConversationChain(llm=llm, memory=memory, prompt=prompt)

# Answer from knowledgebase
def answer_from_knowledgebase(message: str) -> str:
    if qa is None:
        return "Knowledgebase is not available."
    try:
        result = qa({"query": message})
        return result['result']
    except Exception as e:
        print("❌ Knowledgebase Error:", e)
        return "An error occurred while processing your request."

# Answer as chatbot
def answer_as_chatbot(message: str) -> str:
    if chatbot_chain is None:
        return "Chatbot is not available."
    try:
        return chatbot_chain.predict(input=message)
    except Exception as e:
        print("❌ Chatbot Error:", e)
        return "An error occurred while chatting with the bot."

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", title="Thinkbot AI")

@app.route("/kbanswer", methods=["POST"])
def kbanswer():
    data = request.get_json()
    message = data.get("message")
    if not message:
        return jsonify({"error": "Missing 'message' in request."}), 400
    answer = answer_from_knowledgebase(message)
    return jsonify({"message": answ
