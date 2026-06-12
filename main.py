import os
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from flask import Flask, request, jsonify
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

app = Flask(__name__)
CORS(app)


groq_llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    max_retries=0
)

gemini_llm = None
if os.getenv("GEMINI_API_KEY"):
    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        max_retries=0
    )

groq_llm_8b = ChatOpenAI(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    max_retries=0
)

cerebras_llm = ChatOpenAI(
    model="gpt-oss-120b",
    api_key=os.getenv("CEREBRAS_API_KEY"),
    base_url="https://api.cerebras.ai/v1",
    max_retries=0
)

search_tool = TavilySearch(max_results=1)
tools = [search_tool]

scheme_system_prompt = """Indian govt schemes & rights assistant. Search official websites only.
List source URLs. Do not omit info. Format output as clean plain-text (no # or * markdown).
Disclaimer: 'This information is for awareness purposes only. Please verify through official government portals and consult a legal expert before taking action.'"""

legal_system_prompt = """Indian legal advisor. Search official databases (e.g. indiankanoon.org, legislative.gov.in).
Explain citizen rights & authority limits. List source URLs. Do not omit info.
Format as plain-text sections (no # or * markdown).
Disclaimer: 'This information is for awareness purposes only. This is not legal advice. Please consult a qualified lawyer before taking any legal action.'"""

directory_system_prompt = """Indian govt scheme directory. Search & list central/state schemes.
Format each scheme exactly as:

SCHEME NAME: [Name]
--------------------------------------------------
📝 Description: [Info]
👥 Who Can Apply (Eligibility): [Eligibility criteria]
🎁 Key Benefits: [Key benefits]
🌐 Official Portal: [Portal URL]
🛠️ How to Apply (Step-by-Step):
  1. [Step 1]
  2. [Step 2...]
--------------------------------------------------

Do not use markdown (# or *). Do not omit info.
Disclaimer: 'This information is for awareness purposes only. Please verify through official government portals before applying.'"""


def make_agents(llm):
    agent_scheme = create_agent(llm, tools=tools, system_prompt=scheme_system_prompt)
    agent_legal = create_agent(llm, tools=tools, system_prompt=legal_system_prompt)
    agent_directory = create_agent(llm, tools=tools, system_prompt=directory_system_prompt)
    return agent_scheme, agent_legal, agent_directory

@app.route('/')
def home():
    return "Backend is awake!", 200

@app.route('/scheme_match', methods=['POST'])
def scheme_match():
    data = request.json
    user_query = data.get('query')
    if not user_query:
        return jsonify({'error': 'Missing query parameter'}), 400

    for llm in [groq_llm, cerebras_llm]:
        try:
            agent_scheme, _, _ = make_agents(llm)
            response = agent_scheme.invoke({"messages": [{"role": "user", "content": user_query}]})
            last_message = response['messages'][-1].content
            answer = last_message[-1]['text'] if isinstance(last_message, list) else last_message
            return jsonify({'Answer': answer})
        except Exception as e:
            print(f"Error using model {llm.model_name}: {e}")
            continue

    return jsonify({'error': 'Both models are unavailable, try again later.'}), 503

@app.route("/legal_advisory", methods=['POST'])
def legal_advisory():
    data = request.json
    user_query = data.get('query')
    if not user_query:
        return jsonify({'error': 'Missing query parameter'}), 400

    for llm in [groq_llm, cerebras_llm]:
        try:
            _, agent_legal, _ = make_agents(llm)
            response = agent_legal.invoke({"messages": [{"role": "user", "content": user_query}]})
            last_message = response['messages'][-1].content
            answer = last_message[-1]['text'] if isinstance(last_message, list) else last_message
            return jsonify({'Answer': answer})
        except Exception as e:
            print(f"Error using model {llm.model_name}: {e}")
            continue

    return jsonify({'error': 'Both models are unavailable, try again later.'}), 503

@app.route("/scheme_directory", methods=['POST'])
def scheme_directory():
    data = request.json
    user_query = data.get('query')
    if not user_query:
        return jsonify({'error': 'Missing query parameter'}), 400

    for llm in [groq_llm, cerebras_llm]:
        try:
            _, _, agent_directory = make_agents(llm)
            response = agent_directory.invoke({"messages": [{"role": "user", "content": user_query}]})
            last_message = response['messages'][-1].content
            answer = last_message[-1]['text'] if isinstance(last_message, list) else last_message
            return jsonify({'Answer': answer})
        except Exception as e:
            print(f"Error using model {llm.model_name}: {e}")
            continue

    return jsonify({'error': 'Both models are unavailable, try again later.'}), 503

if __name__ == '__main__':
    app.run(debug=True)
