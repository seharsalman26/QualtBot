import streamlit as st
import google.generativeai as genai
from openai import OpenAI

st.set_page_config(page_title="Qualtrics Chatbot", page_icon="💬")

# 1. READ PARAMETERS FROM THE URL
dynamic_prompt = st.query_params.get("prompt", "You are a helpful assistant.")
# Default to Google/Gemini if Qualtrics doesn't specify
provider = st.query_params.get("provider", "google").lower()
selected_model = st.query_params.get("model", "gemini-3.1-flash-lite-preview")

# 2. UNIFIED CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. THE CHAT INPUT
if prompt := st.chat_input("Type your message here..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # We use a placeholder to update the text as it streams in
        response_placeholder = st.empty()
        full_response = ""
        
        # ==========================================
        # PATH A: OPENAI (with Streaming)
        # ==========================================
        if provider == "openai":
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            messages_for_api = [{"role": "system", "content": dynamic_prompt}] + st.session_state.messages
            
            stream = client.chat.completions.create(
                model=selected_model,
                messages=messages_for_api,
                stream=True, # Enables streaming
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌") # Adds a cursor

        # ==========================================
        # PATH B: GOOGLE (with Streaming)
        # ==========================================
        elif provider == "google":
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            gemini_model = genai.GenerativeModel(
                model_name=selected_model,
                system_instruction=dynamic_prompt
            )
            
            gemini_history = []
            for msg in st.session_state.messages[:-1]: 
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
            
            chat_session = gemini_model.start_chat(history=gemini_history)
            response = chat_session.send_message(prompt, stream=True) # Enables streaming
            
            for chunk in response:
                full_response += chunk.text
                response_placeholder.markdown(full_response + "▌")

        # Final update to remove the cursor
        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})