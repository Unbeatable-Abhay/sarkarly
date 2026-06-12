import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

app = Flask(__name__)
CORS(app)

groq_llm = ChatOpenAI(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    max_retries=0
)

groq_llm_8b = ChatOpenAI(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    max_retries=0
)

gemini_llm = None

if os.getenv("GEMINI_API_KEY"):
    gemini_llm = ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        google_api_key=os.getenv("GEMINI_API_KEY"),
        max_retries=0
    )

cerebras_llm = ChatOpenAI(
    model="gpt-oss-120b",
    api_key=os.getenv("CEREBRAS_API_KEY"),
    base_url="https://api.cerebras.ai/v1",
    max_retries=0
)

search_tool = TavilySearch(max_results=3)

@tool
def web_search(query: str) -> str:
    return search_tool.run(query)

tools = [web_search]

scheme_system_prompt = """
You are an Indian government schemes assistant.

Rules:
- Search official government websites only.
- Explain schemes clearly.
- Mention eligibility, benefits, and official links.
- Give concise but complete responses.
- Output clean plain text only.
- Never show tool calls or XML tags.

Disclaimer:
This information is for awareness purposes only.
Please verify through official government portals before applying.
"""

legal_system_prompt = """
You are an Indian legal awareness assistant.

Rules:
- Search official/legal sources only.
- Explain citizen rights clearly.
- Explain police/government authority limits.
- Mention legal provisions if available.
- Output clean plain text only.
- Never show tool calls or XML tags.

Disclaimer:
This information is for awareness purposes only.
This is not legal advice.
Please consult a qualified lawyer before taking legal action.
"""

directory_system_prompt = """
You are an Indian government scheme directory assistant.

Format EXACTLY like this:

SCHEME NAME: [Name]
--------------------------------------------------
Description: [Info]

Who Can Apply:
[Eligibility]

Benefits:
[Benefits]

Official Portal:
[URL]

How to Apply:
1. Step 1
2. Step 2
--------------------------------------------------

Rules:
- Output clean plain text only.
- Never show tool calls or XML tags.
- Do not use markdown.

Disclaimer:
This information is for awareness purposes only.
Please verify through official government portals before applying.
"""

def make_agents(llm):
    agent_scheme = create_agent(
        llm,
        tools=tools,
        system_prompt=scheme_system_prompt
    )

    agent_legal = create_agent(
        llm,
        tools=tools,
        system_prompt=legal_system_prompt
    )

    agent_directory = create_agent(
        llm,
        tools=tools,
        system_prompt=directory_system_prompt
    )

    return agent_scheme, agent_legal, agent_directory

def get_models_chain():
    chain = [groq_llm, groq_llm_8b]

    if gemini_llm:
        chain.append(gemini_llm)

    chain.append(cerebras_llm)

    return chain

def extract_final_answer(response):

    messages = response.get("messages", [])

    for msg in reversed(messages):

        if getattr(msg, "type", "") == "ai":

            content = msg.content

            if isinstance(content, str):

                if "<web_search>" in content:
                    continue

                return content

            elif isinstance(content, list):

                texts = []

                for item in content:

                    if isinstance(item, dict):

                        if item.get("type") == "text":
                            texts.append(item.get("text", ""))

                        elif "text" in item:
                            texts.append(item["text"])

                final_text = "\n".join(texts)

                if "<web_search>" in final_text:
                    continue

                return final_text

    return "Unable to generate a proper response."

def handle_request(agent_type, user_query):

    for llm in get_models_chain():

        try:

            agent_scheme, agent_legal, agent_directory = make_agents(llm)

            if agent_type == "scheme":
                agent = agent_scheme

            elif agent_type == "legal":
                agent = agent_legal

            else:
                agent = agent_directory

            response = agent.invoke({
                "messages": [
                    {
                        "role": "user",
                        "content": user_query
                    }
                ]
            })

            print("\n========== RAW RESPONSE ==========")
            print(response)
            print("==================================\n")

            answer = extract_final_answer(response)

            return jsonify({
                "Answer": answer
            })

        except Exception as e:

            model_name = getattr(
                llm,
                'model_name',
                getattr(llm, 'model', 'unknown')
            )

            print(f"\nERROR USING MODEL {model_name}")
            print(str(e))
            print("\nTrying fallback model...\n")

            continue

    return jsonify({
        "error": "All AI models are currently unavailable."
    }), 503

@app.route('/')
def home():
    return "Backend is awake!", 200

@app.route('/scheme_match', methods=['POST'])
def scheme_match():

    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({
            'error': 'Missing query parameter'
        }), 400

    return handle_request("scheme", user_query)

@app.route('/legal_advisory', methods=['POST'])
def legal_advisory():

    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({
            'error': 'Missing query parameter'
        }), 400

    return handle_request("legal", user_query)

@app.route('/scheme_directory', methods=['POST'])
def scheme_directory():

    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({
            'error': 'Missing query parameter'
        }), 400

    return handle_request("directory", user_query)

if __name__ == '__main__':
    app.run(debug=True)