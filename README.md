## License
This project is licensed under the [Apache License 2.0](LICENSE).

# Sarkarly

A web application that helps Indian citizens discover government schemes they qualify for, understand their legal rights in real-life situations, and get step-by-step guidance on how to apply for available schemes.

---

## Features

### 1. Personalized Scheme Matcher
Answer a few simple questions about yourself — your occupation, land size, income, state, and category — and the app finds all government schemes you are eligible for. Results are fetched from official government portals in real time and include direct source links for verification.

### 2. Legal Rights Advisor
Describe a real-life situation you are facing — such as being stopped by a police officer, a dispute with a landlord, or a workplace issue — and the app tells you the relevant laws, your rights, and what can or cannot legally happen in that scenario. Every response includes a disclaimer and links to official legal sources.

### 3. Scheme Directory & Application Guide
Browse all available central and state government schemes in one place. Select any scheme to get a clear, step-by-step guide on how to apply, what documents are required, and where to submit your application.

---

## How It Works

1. The user enters a query or selects options describing their situation
2. A LangChain-powered AI agent analyzes the query and decides what to search for
3. The agent searches official government portals and legal databases using the Tavily API
4. Results are evaluated and summarized by the AI model
5. The final response is returned with a disclaimer and source links from where the information was retrieved

---

## Tech Stack

| Layer | Technology                                                        |
|---|-------------------------------------------------------------------|
| Frontend | React                                                             |
| Backend | Flask (Python)                                                    |
| AI Agent | LangChain                                                         |
| Web Search | Tavily API                                                        |
| Language Model | Mistral Large with Mistral Small and Gemini 3.5 flash as fallback |
---

## Project Structure

```
sarkarly/
├── main.py                  # Entry point: builds the app via the factory and runs it
├── Procfile                 # Production process command (gunicorn) for Render/Heroku
├── backend/
│   ├── __init__.py          # App factory: wires up config, CORS, logging, routes, error handlers
│   ├── config.py            # All environment-driven configuration in one place
│   ├── logging_config.py    # Structured logging setup
│   ├── routes.py            # Flask blueprint: /scheme_match, /legal_advisory, /scheme_directory
│   ├── agents.py            # Agent construction + the multi-model fallback request handler
│   ├── llm_providers.py     # Builds the Mistral -> Mistral/Gemini fallback chain
│   ├── search_tools.py      # Tavily web search tool wrapper
│   ├── schemas.py           # Pydantic response schemas (structured LLM output)
│   ├── prompts.py           # System prompts for each agent
│   └── errors.py            # JSON error handlers (400/404/405/500)
├── frontend/                 # React app (see frontend/README.md)
├── .env.example              # Backend environment variable template
└── requirements.txt          # Python dependencies
```

---

## Setup & Installation

**1. Clone the repository**
```bash
git clone https://github.com/Unbeatable-Abhay/sarkarly.git
cd sarkarly
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up environment variables**

Copy `.env.example` to `.env` and fill in your API keys (see it for the full list, including server/CORS settings):
```
GEMINI_API_KEY=your_gemini_api_key
Mistral_API_KEY=your_mistral_api_key
TAVILY_API_KEY=your_tavily_api_key
```

- Get Gemini API key: https://aistudio.google.com
- Get Mistral API key: https://console.mistral.ai
- Get Tavily API key: https://app.tavily.com

**4. Run the backend (development)**
```bash
python main.py
```

The server starts at `http://localhost:8000` by default (configurable via `PORT`).

**5. Run the backend (production)**
```bash
gunicorn main:app
```
This is what the included `Procfile` runs on Render/Heroku-style hosts. Always set `ALLOWED_ORIGINS` to your real frontend domain(s) in production — it defaults to `*` (open) for local dev convenience only.

**6. Run the frontend**
```bash
cd frontend
cp .env.example .env   # point REACT_APP_API_URL at your backend
npm install
npm start
```

---

## API Routes

| Route | Method | Description |
|---|---|---|
| `/scheme_match` | POST | Returns schemes matching the user's profile |
| `/legal_advisory` | POST | Returns relevant laws for a described situation |
| `/scheme_directory` | POST | Returns all schemes with application guidance |

---

## LLM Fallback

The app uses **Mistral large** as the primary LLM provider. If Mistral's daily token limit is reached, requests automatically fall back to  either **Gemini 3.5 flash** or **Mistral small**. This ensures the app stays available even when one provider's free tier is exhausted.

---

## Important Note

All responses from this application are for informational purposes only. Users should verify information through official government portals and consult a legal professional before taking any action. Source links are provided with every response for independent verification.
