import os
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from flask import Flask, request, jsonify
from langchain_tavily import TavilySearch
from langchain.agents import create_agent

load_dotenv()

app = Flask(__name__)
CORS(app)

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
search_tool=TavilySearch(max_results=5)
tools=[search_tool]

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

agent_scheme=create_agent(llm, tools=tools, system_prompt=scheme_system_prompt)
agent_legal=create_agent(llm, tools=tools, system_prompt=legal_system_prompt)
agent_directory=create_agent(llm, tools=tools, system_prompt=directory_system_prompt)

@app.route('/scheme_match', methods=['POST'])
def scheme_match():
    data=request.json
    user_query=data['query']

    response=agent_scheme.invoke({"messages": [{"role": "user", "content": user_query}]})

    last_message=response['messages'][-1].content

    if isinstance(last_message, list):
        answer=last_message[-1]['text']
    else:
        answer=last_message

    return jsonify({'Answer': answer})

@app.route("/legal_advisory", methods=['POST'])
def legal_advisory():
    data=request.json
    user_query=data['query']

    response=agent_legal.invoke({"messages": [{"role": "user", "content": user_query}]})

    last_message=response['messages'][-1].content
    if isinstance(last_message, list):
        answer=last_message[-1]['text']
    else:
        answer=last_message

    return jsonify({'Answer': answer})

@app.route("/scheme_directory", methods=['POST'])
def scheme_directory():
    data=request.json
    user_query=data['query']

    response=agent_directory.invoke({"messages": [{"role": "user", "content": user_query}]})

    last_message=response['messages'][-1].content
    if isinstance(last_message, list):
        answer=last_message[-1]['text']
    else:
        answer=last_message

    return jsonify({'Answer': answer})


if __name__ == '__main__':
    app.run(debug=True)
