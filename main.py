import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)


def get_llms():
    from langchain_openai import ChatOpenAI
    from langchain_google_genai import ChatGoogleGenerativeAI

    groq_key = os.getenv("GROQ_API_KEY")
    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    llms = []

    if groq_key:
        llms.append(ChatOpenAI(
            model="llama-3.3-70b-versatile",
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
            max_retries=0
        ))
        llms.append(ChatOpenAI(
            model="llama-3.1-8b-instant",
            api_key=groq_key,
            base_url="https://api.groq.com/openai/v1",
            max_retries=0
        ))

    if gemini_key:
        llms.append(ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            google_api_key=gemini_key,
            max_retries=0
        ))

    if cerebras_key:
        llms.append(ChatOpenAI(
            model="gpt-oss-120b",
            api_key=cerebras_key,
            base_url="https://api.cerebras.ai/v1",
            max_retries=0
        ))

    return llms


def get_search_tool():
    from langchain_tavily import TavilySearch
    return TavilySearch(max_results=3)


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
-----------------------------------------
Description: [Info]

Who Can Apply:
[Eligibility]

Benefits:
[Benefits]

Official Portal:
[URL]
make sure to make this link clickable so and not just paste it as a text

How to Apply:
1. Step 1
2. Step 2
and so on.... and after all the "How to apply" steps make sure to add the the actual working form url for that scheme and then add the separator
-----------------------------------------

Rules:
- Output clean plain text only, leave proper lines before and after links and other headings.
- Never show tool calls or XML tags.
- Do not use markdown.

Disclaimer:
This information is for awareness purposes only.
Please verify through official government portals before applying.
"""


def make_agents(llm, tools):
    from langchain.agents import create_agent

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
    from langchain_core.tools import tool as lc_tool

    search_tool = get_search_tool()

    @lc_tool
    def web_search(query: str) -> str:
        """Search the web for Indian Government information."""
        return search_tool.run(query)

    tools = [web_search]
    llms = get_llms()

    if not llms:
        return jsonify({
            "error": "No AI models configured. Please set GROQ_API_KEY, GEMINI_API_KEY, or CEREBRAS_API_KEY."
        }), 503

    for llm in llms:

        try:

            agent_scheme, agent_legal, agent_directory = make_agents(llm, tools)

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
    app.run(host='localhost', port=8000, debug=True)
