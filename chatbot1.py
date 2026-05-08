import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="Qualtrics Chatbot", page_icon="💬")
st.title("💬 Survey Assistant")
st.write("Hello! I am here to help answer any questions you have.")

# ==========================================
# 🌟 NEW: THE CUSTOM PROMPT (SYSTEM INSTRUCTION)
# ==========================================
# Change this text to dictate the bot's rules, tone, and knowledge.
CUSTOM_PROMPT = """
You are a helpful, polite, and professional survey assistant. 
Your job is to help participants understand how to fill out their survey.
Rules:
1. Keep your answers brief, usually 2-3 sentences.
2. If a user asks a question unrelated to the survey, politely decline to answer and guide them back to the survey.
3. Always maintain a warm, encouraging tone.
"""

# 2. Configure the Gemini API securely
# Streamlit looks for the API key in its hidden Secrets manager
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Initialize the Gemini Model WITH the custom prompt
# We pass the CUSTOM_PROMPT into the 'system_instruction' parameter
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=CUSTOM_PROMPT
)

# 4. Set up the Chat Session in Streamlit Memory
# This ensures the bot remembers the conversation history
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# 5. Display the Chat History on the screen
for message in st.session_state.chat_session.history:
    # Gemini uses 'model' and 'user' for roles, Streamlit uses 'assistant' and 'user'
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 6. The Chat Input Box
prompt = st.chat_input("Type your message here...")

if prompt:
    # Immediately show the user's message on the screen
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send the message to Gemini and get the response
    with st.chat_message("assistant"):
        # The spinner gives visual feedback while the AI is "thinking"
        with st.spinner("Thinking..."):
            response = st.session_state.chat_session.send_message(prompt)
            st.markdown(response.text)
