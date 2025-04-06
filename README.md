⸻

# Jarvis 🧠 — Agentic AI Assistant with Local + Gemini Hybrid Intelligence

**Jarvis** is a fully local, privacy-first AI assistant that mimics a **Manus-like experience** — executing terminal commands, browsing the web, managing your filesystem, and writing code — all through autonomous, multi-agent orchestration. Powered by **Llama 3.2 agents** and enhanced with **Gemini browsing**, it ensures minimal data leakage and maximum utility.


---

![Jarvis Banner](./media/jarvis.jpg)

> *Do a deep search of AI startups in Osaka and Tokyo, find at least 5, then save them in `research_japan.txt`.*

> *Can you make a tetris game in C ?*

> *I would like to set up a new project file index as mark2.*

---

## 🚀 Key Features

- **Agentic AI Architecture**: Uses multiple specialized agents for browser tasks, coding, system interaction, and planning.
- **Hybrid Intelligence**: 
  - **Gemini** handles browser and web search queries (more reliable than Selenium + searxng).
  - **Local Ollama Models** (e.g., `llama3.2:1b`) preserve privacy by reducing external API usage.
- **Modular Planning Engine**: Automatically routes tasks to appropriate agents or chains them for complex reasoning.
- **Autonomous Web Navigation**: Conducts research, fills forms, and gathers content from the internet.
- **Terminal Agent**: Execute Linux commands and scripts intelligently.
- **Filesystem Navigator**: Locate, read, write and organize files using natural language.
- **Voice Input Support**: Triggerable speech-to-text system for hands-free control.

---

## 🔐 Privacy First

Jarvis prioritizes **data privacy**. All code execution and reasoning can be done locally, with only browsing requests optionally sent to **Gemini** for superior performance.

```
graph TD
    A[User Query] --> B{Local Model (Ollama API)};
    B -- Simple Query --> C[Bash Interpreter];
    B -- Complex Query --> D[Planner Agent];
    D -- Initial Plan --> E{Proceed with this plan?};
    E -- Yes --> F[Gemini API (Web Search)];
    F -- Relevant Data --> G{Route Data};
    G -- Code Execution Required --> H[Code Interpreter];
    G -- File Processing Required --> I[File Interpreter];
    G -- Bash Command Required --> C;
    E -- No --> D;
    D -- Revised Plan --> E;
    C -- Result --> J[User Response];
    H -- Result --> J;
    I -- Result --> J;
    F -- No Relevant Data --> J;
```

```mermaid
graph TD
    A[User Query] --> B{Local Model (Ollama API)};
    B -- Simple Query --> C[Bash Interpreter];
    B -- Complex Query --> D[Planner Agent];
    D -- Initial Plan --> E{Proceed with this plan?};
    E -- Yes --> F[Gemini API (Web Search)];
    F -- Relevant Data --> G{Route Data};
    G -- Code Execution Required --> H[Code Interpreter];
    G -- File Processing Required --> I[File Interpreter];
    G -- Bash Command Required --> C;
    E -- No --> D;
    D -- Revised Plan --> E;
    C -- Result --> J[User Response];
    H -- Result --> J;
    I -- Result --> J;
    F -- No Relevant Data --> J;
```

---

## Key Architectural Decisions

* **Local Interpretation First:** All queries are initially processed locally by the Ollama-based model. This ensures that only complex queries requiring external data retrieval are sent to the `Planner Agent`.
* **Planner for Complexity:** The `Planner Agent` acts as the orchestrator for complex tasks, defining the sequence of actions and deciding when to involve external web search and specific interpreters.
* **Gemini for External Data:** The `Gemini API` is solely responsible for retrieving relevant data from the web when the `Planner Agent` deems it necessary.
* **Specialized Interpreters:** Dedicated interpreters handle specific types of tasks (code execution, file manipulation, and direct bash commands), ensuring modularity and focused processing.
* **Confirmation Step:** The user is explicitly asked for confirmation before proceeding with a plan that involves external web search, providing transparency and control.

A very basic architectural overview is provided below:
(media/First_arch.jpg)

---

## 📦 Installation

Make sure you have **Python 3.10+**, **ChromeDriver**, and **Docker** installed.

### 1️⃣ Clone and Setup

```bash
git clone https://github.com/kh-ops69/Jarvis.git
cd Jarvis
mv .env.example .env

2️⃣ Create Virtual Environment

python3 -m venv jarvis_env
source jarvis_env/bin/activate
# Windows: jarvis_env\Scripts\activate

3️⃣ Install Dependencies

Auto-install:

./install.sh

Manual:

pip install -r requirements.txt

---

🧠 Running the Assistant

Option A: Local Model via Ollama (Recommended for Privacy)
	1.	Install Ollama
	2.	Pull a lightweight model:

ollama pull llama3.2:1b

	3.	Update config.ini:

[MAIN]
is_local = True
provider_name = ollama
provider_model = llama3.2:1b
provider_server_address = 127.0.0.1:11434

Generate API Key from https://ai.google.dev/gemini-api/docs/api-key
Place your API Key's value in .env file, setting it to GEMINI_API_KEY'

	4.	Run:

ollama serve
sudo ./start_services.sh
python3 main.py

⚠️ For complex reasoning, use deepseek-r1:14b or better (if your hardware allows).

⸻

Option B: Remote Model Server
	1.	On your remote server:

ollama pull deepseek-r1:14b
python3 app.py --provider ollama --port 3333

	2.	On your laptop:

[MAIN]
is_local = False
provider_name = server
provider_model = deepseek-r1:14b
provider_server_address = x.x.x.x:3333

Then run:

sudo ./start_services.sh
python3 main.py
```
---

## 🎙️ Voice Activation
	1.	In config.ini:

listen = True
agent_name = Friday

	2.	Trigger by saying the agent name aloud, then speak your query.
	3.	End with phrases like “do it”, “please”, “run”, etc.

---

## 💻 Example Commands

Coding / Terminal
	•	Write a snake game in Python
	•	Show all processes using over 1GB RAM
	•	Compile this C file and run it

Web Browsing
	•	Find cheapest RTX 4090 online
	•	Search GitHub for trending AI projects

Filesystem
	•	Find contract.pdf and open it
	•	How much space is left on this disk?

Casual
	•	Who is the president of South Korea?
	•	Should I take creatine before or after a workout?

---

## 🌐 Providers Overview

Provider	Local?	Description
ollama	✅	Run models locally
server	✅	Use your own server
lm-studio	✅	Use LM Studio for local inference
openai	❌	GPT-3.5, GPT-4 via OpenAI API
deepseek-api	❌	Use DeepSeek’s hosted API
huggingface	❌	Hugging Face Inference API

Update config.ini accordingly.

---

#### 🧪 Known Issues


Exception: Failed to initialize browser: Message: session not created: This version of ChromeDriver only supports Chrome version 113
Current browser version is 134.0.6998.89 with binary path`

This happen if there is a mismatch between your browser and chromedriver version.

You need to navigate to download the latest version:

https://developer.chrome.com/docs/chromedriver/downloads

If you're using Chrome version 115 or newer go to':

https://googlechromelabs.github.io/chrome-for-testing/

And download the chromedriver version matching your OS.

Model Limitations:
The current system uses a smaller LLaMA 3.2 model with approximately 1 billion parameters. While this allows for faster inference, it significantly reduces accuracy and instruction-following ability. It often requires multiple prompts (trial and error) to steer the model in the right direction.
Upgrade to a larger model (≥14B parameters) if hardware permits, to improve response quality and reduce prompt iterations.


Error Handling:
Due to the smaller model, many edge cases throw unexpected errors that cause the agent or the system to fail.
Robust error handling needs to be added throughout the agent’s workflow.


Command Execution Inconsistencies:
Commands generated for terminal or file operations sometimes do not execute as expected because of inconsistencies in code generation or lack of context.
More rigorous testing and validation are required, especially when using smaller models, to ensure commands are reliable.


Missing Step-by-Step Validation:
There is no validation at intermediate steps—such as when the plan is generated, commands are executed, or intermediate outputs are received.
Add checkpoint validations throughout the agent’s reasoning and execution pipeline.


Poor Logical Flow & Redundant Code:
The codebase contains redundant files and testing modules, making the overall flow cluttered and confusing.
Refactoring required for better clarity, modularization, and readability.


Unreliable Speech-to-Text Functionality:
Speech input functionality is present but not thoroughly tested, and may not work as expected in all environments.


Cross-Platform Compatibility Not Verified:
The system has only been tested on a Mac M1 with 8GB RAM. Code exists for Windows and Linux, but platform-specific compatibility is unverified.
Thorough testing on Windows and Linux environments is necessary.

⸻

