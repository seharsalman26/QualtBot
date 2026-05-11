# QualtBot: A Qualtrics Chatbot
QualtBot allows researchers to embed a chatbot into Qualtrics survey platform, with the conversation being saved as part of the survey. The chatbot can be customised based on study needs. It currently uses Google Gemini or OpenAI models. If there are elements that you are unable to customise that you need to, please contact me (https://profiles.ucl.ac.uk/57936-mark-warner). Here is a complete, step-by-step tutorial. It guides you through deploying your own secure instance of your QualBot and integrating it seamlessly into Qualtrics.

## ⚠️ Streamlit app sleep
Please note that Streamlit puts apps to sleep after inactivity for 24 hours (weekday), or 72 hours (Saturday through Monday). If you are running a study, ensure that the app is awake prior to study start. 

## 📝 Citation

If you use this tool in your research, please cite this repository using the below:

> Mark Warner. 2026. *QualtBot: A Qualtrics Chatbot*. GitHub. Retrieved from https://github.com/markjwarner/QualtBot

**BibTeX:**
```bibtex
@misc{warner2026chatbot,
  author = {Warner, Mark},
  title = {QualtBot: A Qualtrics Chatbot},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{[https://github.com/markjwarner/QualtBot](https://github.com/markjwarner/QualtBot)}}
}
```

# 🤖 How to Embed QualtBot into Your Qualtrics Survey
To ensure participant privacy and keep your API keys secure, you will create your own private copy of QualBot app using Steamlit, link your own API keys to it, and embed that private app directly into your survey. Participants will never see your keys, and all chat transcripts will be automatically saved to your Qualtrics dataset.

## Phase 1: Deploy Your Chatbot on Streamlit
Streamlit (https://streamlit.io) is a free cloud platform for hosting Python web apps. You need to use it to host your specific instance of QualBot.

### Step 1: Create a Streamlit Account

Go to https://share.streamlit.io and sign up for a free Community Cloud account.

Link your GitHub account when prompted (this is required to deploy apps).

### Step 2: Deploy the App

Once logged into Streamlit, click the New app button.

If asked how to deploy, select Use existing repo.

In the Repository URL field, paste this exact link:
https://github.com/markjwarner/QualtBot

Leave the "Branch" as main and "Main file path" as app.py.

Do not click Deploy yet! Proceed to Step 3.

### Step 3: Securely Add Your API Keys

To power the bot, you need to provide it with an API key from either OpenAI or Google Gemini.

Click on Advanced settings... at the bottom of the deployment screen.

In the Secrets text box, paste your API key using the following format:

#### Use this for OpenAI (ChatGPT) models (see: https://developers.openai.com/api/docs/quickstart)
`OPENAI_API_KEY = "your-openai-api-key-here"`

#### Use this for Google (Gemini) models (see: https://ai.google.dev/gemini-api/docs/api-key)
`GEMINI_API_KEY = "your-gemini-api-key-here"`

Click Save, then click Deploy.

Wait 1-2 minutes for the app to build. Once it loads, look at the URL bar in your browser. Copy your new app's URL (it will look something like https://your-custom-name.streamlit.app). Keep this handy for Phase 2!

## Phase 2: Add the Qualtrics Integration Code
The easiest way to setup your qualtrics integration is to use and the edit the provided template: `QualtBot_template.qsf'. If you prefer to set it up manually, you can follow the below steps.

To use the template, create a new blank survey. Then, select Tools > Import/Export > Import Survey > Choose File > `QualtBot_template.qsf'

### Step 1: Add Custom CSS (Styling)

To ensure the chatbot fits nicely on desktop and mobile screens and hides any unwanted borders, we must setup the style. 

Go to the Look and Feel menu (the paint roller icon).

Click on Style, then scroll down to Custom CSS. Paste the content of `chatbotStyle.css`

### Step 2: Add the JavaScript

Create a new 'Text Entry' question in your survey block and set the Text Type to 'Multiple lines'. This will act as the container for your chatbot and will be used to save the chat history.

Click the JavaScript icon (</>) under the question behavior menu.

Delete any default code (all of it) in the window and paste the script within `chatbot.py`.

Update the configuration variables at the top of the script (especially the baseUrl) to customise QualtBot.

### Step 3: Add the Embedded Variables

Create a set of embedded variables within the Survey Flow. Please use the configuration cheat sheet below to help you develop these. 

# ⚙️ Configuration Cheat Sheet

You can easily alter how the chatbot behaves by changing the variables in the JavaScript above. Here is exactly what each option does:

| Variable | Description | Example Inputs |
| :--- | :--- | :--- |
| `baseUrl` | Your deployed Streamlit URL. | `"https://your-app.streamlit.app"` |
| `myProvider` | The AI company you are using. Dictates which API key Streamlit uses. | `"openai"` or `"google"` |
| `myModel` | The specific AI model version. Ensure it matches your provider. | `"gpt-4o-mini"`, `"gpt-4o"`, `"gemini-1.5-flash"`, `"gemini-1.5-pro"` |
| `mySurveyPrompt` | The "System Prompt." This dictates the bot's personality, rules, and restrictions. The user never sees this. | `"You are a strict math tutor. Never give the final answer, only hints."` |
| `myInitialMsg` | The first message the bot displays on the screen to greet the participant. | `"Welcome! Please type your question below."` |
| `maxTurns` | The number of messages the *user* is allowed to send before the chat input is disabled. | `5` or `10` |
| `myUserIcon` | The avatar for the participant. Can be an emoji or an image URL. | `"🧑‍🎓"` or `"https://site.com/user.png"` |
| `myBotIcon` | The avatar for the AI. Can be an emoji or an image URL. | `"🤖"` or `"https://site.com/bot.png"` |

## 🧪 Testing Your Setup
To verify everything is working:

Publish your survey and open the Live Anonymous Link (Do not use Preview mode, as it can occasionally block cross-iframe communication).

Have a brief conversation with the bot.

Important: Click the Next or Submit button to advance to the next page. Qualtrics only commits embedded data to your database when a page is submitted.

Go to your Data & Analysis tab in Qualtrics. You will see a column named chat_history populated with a JSON array containing the full transcript of your conversation!
