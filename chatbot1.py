import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="Qualtrics Chatbot", page_icon="💬")



# Hide Streamlit's default menu and footer
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)



# 1. READ PARAMETERS FROM THE URL
dynamic_prompt = st.query_params.get("prompt", "You are a helpful assistant.")
# Default to Google/Gemini if Qualtrics doesn't specify
provider = st.query_params.get("provider", "google").lower()
selected_model = st.query_params.get("model", "gemini-3.1-flash-lite-preview")
initial_msg = st.query_params.get("initial_msg", "Hello! How can I help you today?")
max_turns = int(st.query_params.get("max_turns", 10))

# 2. UNIFIED CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": initial_msg}]

# Display existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# 2. Count how many messages the USER has sent
user_messages_count = len([m for m in st.session_state.messages if m["role"] == "user"])

# 3. Check if limit is reached
if user_messages_count >= max_turns:
    # st.warning("This part of the convers") is you want to add a warning, we can do that here
    # We will pass 'disabled=True' to the chat_input below
    chat_input_disabled = True
else:
    chat_input_disabled = False


# 3. THE CHAT INPUT
if prompt := st.chat_input("Type your message here...", disabled=chat_input_disabled):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Add Thinking... spinnder
        with st.spinner("Thinking..."):
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

        # Convert chat history to a single string
        history_str = json.dumps(st.session_state.messages)

        # This hidden JavaScript sends the data back to Qualtrics
        components.html(
            f"""
            <script>
                window.parent.postMessage({{
                    type: 'chat_export',
                    history: {history_str}
                }}, "*");
            </script>
            """,
            height=1, # Keeps it invisible
)