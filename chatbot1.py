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
# We store messages here in a generic format that both APIs can read
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. THE CHAT INPUT
prompt = st.chat_input("Type your message here...")

if prompt:
    # Immediately show the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            bot_reply = ""
            
            # ==========================================
            # PATH A: OPENAI (ChatGPT)
            # ==========================================
            if provider == "openai":
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                
                # OpenAI needs the system prompt sent as the first message
                messages_for_api = [{"role": "system", "content": dynamic_prompt}] + st.session_state.messages
                
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=messages_for_api,
                    stream=TRUE,
                )

                for response in response:
                if response.choices[0].delta.content:
                    bot_reply += response.choices[0].delta.content
                    response_placeholder.markdown(bot_reply + "▌") # Adds a cursor

            # ==========================================
            # PATH B: GOOGLE (Gemini)
            # ==========================================
            elif provider == "google":
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                gemini_model = genai.GenerativeModel(
                    model_name=selected_model,
                    system_instruction=dynamic_prompt
                )
                
                # Gemini needs history formatted specifically as 'user' and 'model'
                # We skip the very last message since we are about to send it as the prompt
                gemini_history = []
                for msg in st.session_state.messages[:-1]: 
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_history.append({"role": role, "parts": [msg["content"]]})
                
                chat_session = gemini_model.start_chat(history=gemini_history)
                response = chat_session.send_message(prompt)
                bot_reply = response.text
            
            # Display and save the final reply, regardless of which API generated it
            response_placeholder.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})