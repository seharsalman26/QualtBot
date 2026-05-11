# QualtBot: A Qualtrics ChatBot

# QualtBot allows researchers to embed a chatbot into Qualtrics survey platform, with the conversation being 
# saved as part of the survey. The chatbot can be customised based on study needs. It currently uses Google 
# Gemini or OpenAI models. If there are elements that you are unable to customise that you need to, please 
# contact me (https://profiles.ucl.ac.uk/57936-mark-warner).

# If you use this tool in your research, please cite this repository using the citation instructions in the README.md

import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import json
#  import streamlit.components.v1 as components removed as depreciated
import streamlit as st

# Generate a unique timestamp so Streamlit is FORCED to re-render the HTML block
import time
refresh_key = time.time()

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
user_icon = st.query_params.get("user_icon", "👤")
bot_icon = st.query_params.get("bot_icon", "🤖")

# Theme colours sent from qualtrics
bg_color = query_params.get("theme.backgroundColor", "#FFFFFF")
user_bubble = query_params.get("theme.primaryColor", "#F0F0F0")
bot_bubble = query_params.get("theme.secondaryBackgroundColor", "#FFD6D6")
text_color = query_params.get("theme.textColor", "#000000")

# Inject CSS to force these colors into the UI
st.markdown(f"""
    <style>
    /* Main App Background */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* User Message Bubbles (Primary Color) */
    [data-testid="stChatMessage"]:nth-child(even) {{
        background-color: {user_bubble};
        color: {text_color};
    }}
    
    /* Bot Message Bubbles (Secondary Background Color) */
    [data-testid="stChatMessage"]:nth-child(odd) {{
        background-color: {bot_bubble};
        color: {text_color};
    }}
    
    /* Input box text color */
    input {{
        color: {text_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# UNIFIED CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": initial_msg}]

# Display existing chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        avatar_icon = user_icon # Uses the Qualtrics URL
    else:
        avatar_icon = bot_icon # Keep the bot as a hardcoded emoji, or make a bot_icon variable too!
        
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])


# Count how many messages the USER has sent
user_messages_count = len([m for m in st.session_state.messages if m["role"] == "user"])

# Check if limit is reached
if user_messages_count >= max_turns:
    # st.warning("This part of the convers") is you want to add a warning, we can do that here
    # We will pass 'disabled=True' to the chat_input below
    chat_input_disabled = True
else:
    chat_input_disabled = False


# THE CHAT INPUT
if prompt := st.chat_input("Type your message here...", disabled=chat_input_disabled):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Use the dynamic variable here too
    with st.chat_message("user", avatar=user_icon): 
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=bot_icon):
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
        js_payload = f"""
            <script>
                // Unique run ID: {refresh_key}
                console.log("STREAMLIT: Broadcasting chat history via st.iframe...");
                
                var payload = {history_str};
                
                try {{
                    // Fire the message up the chain to EVERY parent window
                    var currentWindow = window.parent;
                    while (currentWindow !== window.top) {{
                        currentWindow.postMessage({{ type: 'chat_export', history: payload }}, "*");
                        currentWindow = currentWindow.parent;
                    }}
                    // Hit the absolute top window just in case
                    window.top.postMessage({{ type: 'chat_export', history: payload }}, "*");
                    
                    console.log("STREAMLIT: Broadcast complete.");
                }} catch(e) {{
                    console.error("STREAMLIT: Error broadcasting:", e);
                }}
            </script>
        """

        # st.iframe executes the bridge
        # We use the 'data:text/html' prefix to make the JS string a valid URL
        st.iframe(
            src=f"data:text/html;charset=utf-8,{js_payload}",
            height=0 # Keep it invisible
        )