# YouTube Trend Analysis with CrewAI and Ollama

An AI-powered YouTube Trend Analysis application built with **Python, Streamlit, CrewAI, yt-dlp, YouTube Transcript API, and Ollama**.

The application collects videos from YouTube channels, extracts their transcripts, and uses CrewAI agents with a local Ollama model to identify topics, trends, sentiment, recurring keywords, and other insights.

## Features

- Collect videos from YouTube channels
- Filter videos by date range
- Extract YouTube transcripts
- Analyze key topics and themes
- Identify emerging trends and patterns
- Analyze speaker sentiment and tone
- Extract recurring keywords and phrases
- Generate structured AI-powered analysis
- Display extracted YouTube videos in the Streamlit interface
- Download the generated analysis as a Markdown file
- Run AI analysis locally using Ollama
- No OpenAI API key required
- No Bright Data API key required

## Tech Stack

- **Python** — Application development
- **Streamlit** — Web interface
- **CrewAI** — AI agent orchestration
- **Ollama** — Local LLM runtime
- **Llama 3.2:1b** — Local language model
- **yt-dlp** — YouTube video collection
- **YouTube Transcript API** — Transcript extraction
- **PyYAML** — Configuration management

## Project Structure

```text
youtube-trend-analysis/
├── app.py
├── brightdata_scrapper.py
├── config.yaml
├── requirements.txt
├── .gitignore
└── README.md
```
## Setup

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd youtube-trend-analysis

###2. Create a Virtual Environment

Windows:

python -m venv .venv
.venv\Scripts\activate

macOS/Linux:

python3 -m venv .venv
source .venv/bin/activate

###3. Install Dependencies

Make sure Python 3.11 or later is installed.

pip install -r requirements.txt

###4. Setup Ollama

Install Ollama and make sure the Ollama service is running.

Pull the model used by this project:

ollama pull llama3.2:1b

The application uses the local:

llama3.2:1b


Run the Project

Start the Streamlit application:

streamlit run app.py

The application will open in your browser.

**How It Works**
1.Enter one or more YouTube channel URLs.
2.Select the desired date range.
3.Start the analysis.
4.collects the relevant YouTube videos.
5.Video transcripts are processed and stored temporarily.
6.CrewAI agents analyze the transcripts using the local Ollama model.
7.The analysis identifies:
      -Key topics and themes
      -Emerging trends and patterns
      -Speaker sentiment and tone
      -Recurring keywords and phrases
8.A structured analysis is displayed in the Streamlit interface.
9.The generated analysis can be downloaded as a Markdown file.
**AI Agents**
**Transcript Analysis Agent**

Analyzes the collected transcripts and identifies:

-Key topics
-Emerging trends
-Speaker sentiment
-Recurring keywords and phrases
**Response Synthesizer Agent**

Combines the detailed analysis into a concise and structured report with clear findings and actionable insights.

**Configuration**

Agent roles, goals, backstories, tasks, and expected outputs are defined in:

config.yaml

This keeps the AI workflow configuration separate from the application code.

**Requirements**
Python 3.11 or later
Ollama
Llama 3.2:1b
Bright Data 
Internet connection for youtube data collection

**Contribution**

Contributions and improvements are welcome.

1.Fork the repository.
2.Create a new branch.
3.Make your changes.
4.Test the application.
5.Submit a pull request.

