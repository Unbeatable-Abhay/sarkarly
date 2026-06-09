from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
search_tool=TavilySearch(max_results=5)
tools=[search_tool]

system_prompt = """You are a helpful assistant that helps Indian citizens find government schemes and their legal rights.
Always search for information from official Indian government websites.
Always include source URLs in your final answer.
Never ever remove some important information from the results in order to shorten the output.
At the end of every response add this disclaimer: 'This information is for awareness purposes only. Please verify through official government portals and consult a legal expert before taking action.'"""

agent=create_agent(llm, tools=tools, system_prompt=system_prompt)


@app.route('/home', methods=['POST'])
def home():
    data=request.json
    user_query=data['query']

    response=agent.invoke(
        {"messages": [{"role": "user", "content": user_query}]})

    last_message=response['messages'][-1].content

    if isinstance(last_message, list):
        answer=last_message[-1]['text']
    else:
        answer=last_message

    return jsonify({'Answer': answer})


if __name__ == '__main__':
    app.run(debug=True)
