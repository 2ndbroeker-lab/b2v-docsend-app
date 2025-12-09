
import streamlit as st
import requests
from datetime import datetime

DOCSEND_API_URL = "https://docsend2pdf.com/api/convert"


def fetch_docsend_pdf(url, email=None, passcode=None):
    payload = {
        "url": url,
        "searchable": False
    }
    if email:
        payload["email"] = email
    if passcode:
        payload["passcode"] = passcode

    resp = requests.post(DOCSEND_API_URL, json=payload, timeout=120)

    if not resp.ok:
        try:
            err_msg = resp.json().get("error", resp.text)
        except Exception:
            err_msg = resp.text
        raise RuntimeError(f"Docsend2PDF API error {resp.status_code}: {err_msg}")

    if "application/pdf" not in resp.headers.get("Content-Type", ""):
        raise RuntimeError(
            f"Unexpected content type from API: {resp.headers.get('Content-Type', '')}"
        )

    return resp.content


def main():
    st.title("DocSend PDF Downloader")

    with st.form("docsend_form"):
        url = st.text_input(
            "DocSend URL *",
            placeholder="https://docsend.com/view/....."
        )
        email = st.text_input("Email (optional, if required)")
        passcode = st.text_input("Passcode (optional, if required)")
        file_name_input = st.text_input(
            "PDF File Name (optional)",
            placeholder=""
        )

        submitted = st.form_submit_button("Fetch PDF")

    if submitted:
        if not url:
            st.error("DocSend URL is required.")
            return

        try:
            with st.spinner("Fetching PDF..."):
                pdf_bytes = fetch_docsend_pdf(
                    url.strip(),
                    email=email.strip() or None,
                    passcode=passcode.strip() or None
                )

            st.success("PDF is ready.")

            # Use custom name if provided, otherwise default pattern
            if file_name_input.strip():
                download_name = file_name_input.strip() + ".pdf"
            else:
                timestamp = datetime.now().strftime("%y%m%d_%H%M")
                download_name = f"{timestamp}_DocSend_Deck.pdf"

            st.download_button(
                "Download PDF now",
                data=pdf_bytes,
                file_name=download_name,
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
