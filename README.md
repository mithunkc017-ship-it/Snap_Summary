# SnapSummary AI

SnapSummary AI summarizes text and web content with Google Gemini. The project includes a Chrome extension for summarizing the active webpage and a Streamlit desktop app for PDFs, screenshots, active-window captures, and pasted text.

## Features

- Summarize webpages directly from Chrome
- Upload PDFs and extract selectable text
- Capture text from the active desktop window
- Upload screenshots and extract text with Tesseract OCR
- Paste or enter text manually
- Choose short, detailed, or beginner-friendly summaries
- Copy or download generated summaries

## Project structure

```text
backend/
  main.py             FastAPI AI summarization API
chrome-extension/
  manifest.json       Chrome extension configuration
  popup.html          Extension popup interface
  popup.js            Webpage extraction and API calls
  style.css           Extension styles
desktop/
  app.py              Streamlit desktop application
requirements.txt      Python dependencies
```

## Requirements

- Windows
- Python 3.10 or later
- Google Gemini API key
- Google Chrome
- Tesseract OCR for screenshot and active-window text extraction

## Setup

### 1. Clone the repository

```powershell
git clone https://github.com/mithunkc017-ship-it/Snap_Summary.git
cd Snap_Summary
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Gemini

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_FALLBACK_MODEL=
```

Never commit the real API key or the `.env` file.

### 5. Install Tesseract OCR

Install Tesseract OCR for Windows and keep the executable at:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

The desktop app can summarize PDFs and pasted text without OCR. Tesseract is required for screenshots and active-window capture.

## Run the application

Start the FastAPI backend in the first terminal:

```powershell
.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The API health check is available at [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

### Desktop app

Start the Streamlit app in a second terminal:

```powershell
.venv\Scripts\Activate.ps1
streamlit run desktop/app.py
```

Open [http://localhost:8501](http://localhost:8501) and choose a PDF, screenshot, text input, or active window before generating a summary.

### Chrome extension

1. Open `chrome://extensions/`
2. Enable **Developer mode**
3. Select **Load unpacked**
4. Choose the `chrome-extension` folder
5. Keep the FastAPI backend running
6. Open a normal webpage and click the SnapSummary AI extension

The extension extracts page text only after you click **Summarize this page**.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | API status |
| `GET` | `/health` | Backend and Gemini configuration status |
| `POST` | `/summarize` | Generate a summary |
| `POST` | `/chat` | Generate a conversational response |

Example summary request:

```json
{
  "content": "Text to summarize",
  "source": "Text",
  "style": "Detailed"
}
```

Supported summary styles are `Short`, `Detailed`, and `Beginner Friendly`.

## Privacy and data handling

- Webpage text is sent to the local FastAPI backend only when summarization is requested.
- The backend sends the supplied content to Google Gemini for summarization.
- PDFs, screenshots, and captured window text remain local until their text is sent to the backend.
- Captured content is not stored by the application.
