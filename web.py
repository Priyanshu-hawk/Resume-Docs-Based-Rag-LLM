import streamlit as st
import requests
import json
import base64


def send_message(url, message, file_info=None):
    try:
        data = {
            "message": message,
            "chat_history": [
                {"human": msg["human"], "assistant": msg["assistant"]}
                for msg in st.session_state.chat_history
            ]
        }
        files = {}
        if file_info:
            files = {
                "file": (file_info["name"], file_info["content"], file_info["type"])}

        # Send JSON data as a string in the 'data' field
        response = requests.post(
            f"{url}/chat",
            data={"data": json.dumps(data)},
            files=files
        )

        # st.write(f"Status Code: {response.status_code}")
        # st.write(f"Response Content: {response.content}")

        response.raise_for_status()  # This will raise an exception for HTTP errors

        result = response.json()
        st.session_state.chat_history.append(
            {"human": message, 'assistant': str(result["response"])}
        )
        return result["response"]
    except requests.exceptions.RequestException as e:
        # print(f"Error: {str(e)}")
        st.error(f"Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            st.error(f"Response content: {e.response.content}")
        return "Sorry, there was an error processing your request."


# Streamlit app
st.title("LLM Chatbot")

# Sidebar
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    To get the ngrok URL from Google Colab:
    1. Run your FastAPI backend in Colab
    2. Set up ngrok if not alread:
        1. Go to NGrok dashboard
        2. Get the NGrok Authtoken
        3. Paste on colab
    3. Copy the URL printed and paste it in the text box bellow
    """)

    st.header("Backend Configuration")
    backend_url = st.text_input(
        "Enter ngrok URL of backend:", value="https://your-ngrok-url.ngrok.io"
    )


# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False
if "file_info" not in st.session_state:
    st.session_state.file_info = None

# File uploader (always shown until a file is uploaded)
if not st.session_state.file_uploaded:
    uploaded_file = st.file_uploader("Choose a file to upload", type=[
                                     "txt", "pdf", "doc", "docx"])
    if uploaded_file is not None:
        st.session_state.file_uploaded = True
        st.session_state.file_info = {
            "name": uploaded_file.name,
            "content": uploaded_file.getvalue(),
            "type": uploaded_file.type
        }
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
else:
    st.info(
        f"File '{st.session_state.file_info['name']}' is currently uploaded.")

# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    with st.chat_message("user" if "human" in message else "assistant"):
        st.markdown(message.get("human") or message.get("assistant"))

# Chat interface
if st.session_state.file_uploaded:
    if prompt := st.chat_input("What is your question?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)

        # Send message to backend and get response
        file_info = st.session_state.file_info if len(
            st.session_state.chat_history) == 0 else None
        response = send_message(backend_url, prompt, file_info)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
else:
    st.warning("Please upload a document before starting the chat.")

# Button to start a new chat
if st.button("Start New Chat"):
    st.session_state.chat_history = []
    st.session_state.file_uploaded = False
    st.session_state.file_info = None
    st.rerun()
