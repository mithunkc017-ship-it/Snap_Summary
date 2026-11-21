
import streamlit as st
import requests
import fitz
import pyautogui
import pygetwindow as gw
import subprocess
import os

from PIL import Image
from io import BytesIO

# Backend API
API_URL = "http://127.0.0.1:8000/summarize"

# Tesseract executable
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# OCR function without pytesseract or pandas
def extract_text_from_image(image):

    if not os.path.exists(TESSERACT_PATH):
        raise FileNotFoundError(
            "Tesseract not found. Please install Tesseract OCR."
        )

    image_buffer = BytesIO()

    image.convert("RGB").save(image_buffer, format="PNG")

    result = subprocess.run(
        [TESSERACT_PATH, "stdin", "stdout"],
        input=image_buffer.getvalue(),
        capture_output=True,
        check=False
    )

    if result.returncode != 0:
        error_message = result.stderr.decode(
            "utf-8", errors="replace"
        )
        raise RuntimeError(f"Tesseract OCR failed: {error_message}")

    return result.stdout.decode("utf-8", errors="replace")


# Streamlit configuration
st.set_page_config(
    page_title="SnapSummary AI",
    page_icon="✨",
    layout="wide"
)

st.title("✨ SnapSummary AI")
st.caption("Your personal AI content intelligence assistant")


# Session state
if "summary" not in st.session_state:
    st.session_state.summary = ""

if "content" not in st.session_state:
    st.session_state.content = ""


# AI summary function
def generate_summary(content, source, style):

    with st.spinner("AI is analyzing your content..."):

        try:
            response = requests.post(
                API_URL,
                json={
                    "content": content,
                    "source": source,
                    "style": style
                },
                timeout=180
            )

            response.raise_for_status()

            result = response.json()
            st.session_state.summary = result["summary"]

        except requests.RequestException as error:
            st.error(f"Backend error: {error}")

            if error.response is not None:
                st.code(
                    error.response.text,
                    language="json"
                )

        except Exception as error:
            st.error(f"Error: {error}")


# Application tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📄 PDF",
    "🖥️ Screen",
    "📝 Text",
    "📷 Screenshot"
])


# TAB 1: PDF
with tab1:

    st.subheader("Summarize PDF")

    pdf = st.file_uploader(
        "Upload your PDF",
        type=["pdf"]
    )

    if pdf:

        if st.button("Extract PDF content"):

            try:
                document = fitz.open(
                    stream=pdf.getvalue(),
                    filetype="pdf"
                )

                text = "\n".join(
                    page.get_text() for page in document
                )

                document.close()

                st.session_state.content = text

                if not text.strip():
                    st.warning(
                        "No selectable text found. "
                        "This may be a scanned PDF. "
                        "Try uploading page screenshots for OCR."
                    )
                else:
                    st.success("PDF text extracted successfully.")

            except Exception as error:
                st.error(f"PDF extraction failed: {error}")


# TAB 2: SCREEN CAPTURE
with tab2:

    st.subheader("Capture active window")

    st.warning(
        "Check the visible window for private information "
        "before capturing."
    )

    approved = st.checkbox(
        "I approve capturing this window and extracting its text."
    )

    if st.button("Capture and extract active window"):

        if not approved:
            st.warning("Please approve capture first.")

        else:

            try:
                window = gw.getActiveWindow()

                if window is None:
                    st.error("No active window found.")

                else:

                    screen_width, screen_height = pyautogui.size()

                    left = max(0, window.left)
                    top = max(0, window.top)

                    width = min(
                        window.width,
                        screen_width - left
                    )

                    height = min(
                        window.height,
                        screen_height - top
                    )

                    if width <= 0 or height <= 0:
                        st.error("Invalid window dimensions.")

                    else:

                        screenshot = pyautogui.screenshot(
                            region=(left, top, width, height)
                        )

                        st.image(
                            screenshot,
                            caption="Captured active window",
                            use_container_width=True
                        )

                        extracted_text = extract_text_from_image(
                            screenshot
                        )

                        st.session_state.content = extracted_text

                        st.success("Screen text extracted.")

            except Exception as error:
                st.error(f"Capture failed: {error}")


# TAB 3: TEXT INPUT
with tab3:

    st.subheader("Enter text manually")

    manual_text = st.text_area(
        "Paste the content you want to summarize",
        height=250,
        placeholder="Paste your text here..."
    )

    if st.button("Use this text"):

        if manual_text.strip():
            st.session_state.content = manual_text
            st.success("Text added successfully.")
        else:
            st.warning("Please enter some text first.")


# TAB 4: SCREENSHOT OCR
with tab4:

    st.subheader("Analyze screenshot")

    image_file = st.file_uploader(
        "Upload screenshot",
        type=["png", "jpg", "jpeg"]
    )

    if image_file:

        image = Image.open(
            BytesIO(image_file.getvalue())
        )

        st.image(
            image,
            use_container_width=True
        )

        if st.button("Extract screenshot text"):

            try:
                extracted_text = extract_text_from_image(image)

                st.session_state.content = extracted_text

                st.success("Screenshot text extracted.")

            except Exception as error:
                st.error(f"OCR failed: {error}")


# AI SUMMARY SETTINGS
st.divider()

st.subheader("AI Summary Settings")

style = st.selectbox(
    "Summary type",
    ["Detailed", "Short", "Beginner Friendly"]
)

if st.button("✨ Generate AI Summary", type="primary"):

    if st.session_state.content.strip():

        generate_summary(
            st.session_state.content,
            "User supplied content",
            style
        )

    else:
        st.warning("Please extract or enter content first.")


# SUMMARY OUTPUT
if st.session_state.summary:

    st.divider()

    st.subheader("📌 Your Summary")

    st.markdown(st.session_state.summary)

    st.download_button(
        "Download Summary",
        data=st.session_state.summary,
        file_name="snapsummary.txt",
        mime="text/plain"
    )
