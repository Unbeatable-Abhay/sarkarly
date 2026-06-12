import os
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from flask import Flask, request, jsonify
from langchain_tavily import TavilySearch
from langchain.agents import create_agent

load_dotenv()

app = Flask(__name__)
CORS(app)


groq_llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


cerebras_llm = ChatOpenAI(
    model="gpt-oss-120b",
    api_key=os.getenv("CEREBRAS_API_KEY"),
    base_url="https://api.cerebras.ai/v1"
)

search_tool = TavilySearch(max_results=5)
tools = [search_tool]

scheme_system_prompt = """You are a helpful assistant that helps Indian citizens find government schemes and their legal rights.
Always search for information from official Indian government websites.
Always include source URLs in your final answer.
Never ever remove some important information from the results in order to shorten the output.
At the end of every response add this disclaimer: 'This information is for awareness purposes only. Please verify through official government portals and consult a legal expert before taking action.'"""

legal_system_prompt = """You are a legal awareness assistant that helps Indian citizens understand their rights in real-life situations.
When a user describes a situation, search for relevant Indian laws, constitutional rights, and legal provisions that apply.
Explain both what the citizen can do and what authorities can and cannot legally do in that situation.
Always include source URLs from official legal databases like indiankanoon.org or legislative.gov.in.
Never give a definitive legal verdict — only explain the relevant laws and rights.
Never remove important information to shorten the output.
At the end add this disclaimer: 'This information is for awareness purposes only. This is not legal advice. Please consult a qualified lawyer before taking any legal action.'"""

directory_system_prompt = """You are a government scheme directory assistant for Indian citizens.
When given a category and state, search and list ALL available central and state government schemes in that category.
For each scheme include: scheme name, brief description, who can apply, key benefits, and step by step application process.
Always include official portal links for each scheme.
Never remove important information to shorten the output.
At the end add this disclaimer: 'This information is for awareness purposes only. Please verify through official government portals before applying.'"""


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
