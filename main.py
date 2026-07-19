import os
from typing import List, Optional

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

app = Flask(__name__)
CORS(app)


class HowToApply(BaseModel):
    mode: str = Field(description="One of: online, offline, both")
    steps: List[str] = Field(description="Ordered, concrete steps to apply for the scheme")


class SchemeItem(BaseModel):
    scheme_name: str
    description: str = Field(description="2-4 sentence plain-language summary of the scheme")
    category: str = Field(description="e.g. Housing, Education, Health, Agriculture, Employment")
    ministry: str = Field(description="Government ministry/department running the scheme")
    eligibility: List[str]
    benefits: List[str]
    how_to_apply: HowToApply
    documents_required: List[str]
    official_link: str = Field(description="Official government portal URL for this scheme")
    application_link: Optional[str] = Field(default="",
                                            description="Direct application/form URL if different from official_link")


class SchemeResponse(BaseModel):
    schemes: List[SchemeItem] = Field(description="One entry per relevant scheme found")
    disclaimer: str = Field(
        default="This information is for awareness purposes only. Please verify through official government portals before applying."
    )


class LegalResponse(BaseModel):
    topic: str = Field(description="Short label for what the query is about")
    explanation: str = Field(description="Plain-language explanation of the citizen's rights/situation")
    relevant_provisions: List[str] = Field(default_factory=list, description="Relevant acts/sections/laws if available")
    citizen_rights: List[str] = Field(description="Concrete rights the citizen has in this situation")
    authority_limits: List[str] = Field(default_factory=list,
                                        description="Limits on police/government authority relevant to the query")
    sources: List[str] = Field(default_factory=list, description="Official/legal source links used")
    disclaimer: str = Field(
        default="This information is for awareness purposes only. This is not legal advice. Please consult a qualified lawyer before taking legal action."
    )


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
- Find the scheme(s) that best match the user's query.
- Fill in every field accurately based on what you find. Do not guess links —
  only include a URL if you found it via search.
- Mention eligibility and benefits clearly and concisely.
- If you cannot find a working application link separate from the official
  portal, leave application_link empty rather than inventing one.
"""

legal_system_prompt = """
You are an Indian legal awareness assistant.

Rules:
- Search official/legal sources only.
- Explain citizen rights clearly and concretely.
- Explain police/government authority limits where relevant to the query.
- Mention specific legal provisions (acts/sections) only if you actually found them.
- Never give this as legal advice — awareness and information only.
"""

directory_system_prompt = """
You are an Indian government scheme directory assistant.

Rules:
- Search official government websites only.
- Return multiple relevant schemes (not just one) that match the user's
  category or query, as a directory listing.
- Fill in every field accurately based on what you find. Do not guess links —
  only include a URL if you found it via search.
- If you cannot find a working application link separate from the official
  portal, leave application_link empty rather than inventing one.
"""


def make_agents(llm, tools):
    from langchain.agents import create_agent

    agent_scheme = create_agent(
        llm,
        tools=tools,
        system_prompt=scheme_system_prompt,
        response_format=SchemeResponse
    )

    agent_legal = create_agent(
        llm,
        tools=tools,
        system_prompt=legal_system_prompt,
        response_format=LegalResponse
    )

    agent_directory = create_agent(
        llm,
        tools=tools,
        system_prompt=directory_system_prompt,
        response_format=SchemeResponse
    )

    return agent_scheme, agent_legal, agent_directory


def extract_structured_response(response):
    """
    Pulls the validated Pydantic object LangChain builds when response_format
    is set, and converts it to a plain dict ready for jsonify().
    Returns None if structuring didn't happen (e.g. model doesn't support it),
    so the caller can fall back to the next model.
    """
    structured = response.get("structured_response")

    if structured is None:
        return None

    if hasattr(structured, "model_dump"):
        return structured.model_dump()

    if isinstance(structured, dict):
        return structured

    return None


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

            data = extract_structured_response(response)

            if data is None:
                print("No structured_response present, trying fallback model...")
                continue

            return jsonify(data)

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
