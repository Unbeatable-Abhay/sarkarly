# Gov Awareness

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

| Layer | Technology |
|---|---|
| Frontend | React |
| Backend | Flask (Python) |
| AI Agent | LangChain |
| Web Search | Tavily API |
| Language Model | Gemini 2.5 Flash |

---

## Project Structure

```
gov_awareness/
├── main.py           # Flask backend with API routes
├── .env.example      # Environment variable template
├── .gitignore
└── requirements      # Python dependencies
```

---

## Setup & Installation

**1. Clone the repository**
```bash
git clone https://github.com/Unbeatable-Abhay/gov_awareness.git
cd gov_awareness
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up environment variables**

Copy `.env.example` to `.env` and fill in your API keys:
```
GEMINI_API_KEY=your_gemini_api_key
```

**4. Run the backend**
```bash
python main.py
```

The server will start at `http://localhost:5000`

---

## API Routes

| Route | Method | Description |
|---|---|---|
| `/home` | POST | Returns schemes matching the user's profile |
| `/legal-advisor` | POST | Returns relevant laws for a described situation |
| `/scheme-directory` | POST | Returns all schemes with application guidance |

---

## Important Note

All responses from this application are for informational purposes only. Users should verify information through official government portals and consult a legal professional before taking any action. Source links are provided with every response for independent verification.

---

## Author

[Abhay](https://github.com/Unbeatable-Abhay)
