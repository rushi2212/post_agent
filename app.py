from flask import Flask, render_template, request
import google.generativeai as genai
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Set your API keys
tavily_api_key = os.getenv("TAVILY_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# ✅ Configure Gemini API
genai.configure(api_key=gemini_api_key)

# Tavily Web Search
def web_search(question):
    trimmed_query = question[:400]  # Tavily's query limit
    headers = {
        "Authorization": f"Bearer {tavily_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": trimmed_query,
        "max_results": 10
    }
    response = requests.post("https://api.tavily.com/search", json=payload, headers=headers)
    results = response.json().get('results', [])
    content = ""
    for r in results:
        content += r.get('content', '')
    return content

# Summarizing with Gemini
def summarizing_agent(user_query):
    content = web_search(user_query)
    prompt = f"Summarize the research in 5 bullet points:\n{content}"
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

# Facebook Post Generator
def facebook_agent(summary):
    prompt = f"""
    You are a witty and creative Facebook caption writer.

    Based on the summary below, craft a short, catchy, and fun caption. Use emojis and 2–3 relevant hashtags where appropriate. Avoid sounding too formal.

    Summary:
    {summary}
    """
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

# LinkedIn Post Generator
def linkedin_agent(summary):
    prompt = f"""
    You are a personal branding expert and storyteller for LinkedIn.

    Based on the summary below, write a professional, insightful, and value-driven LinkedIn post.
    Make it engaging with a smooth flow, include a compelling hook, share key insights, and end with a thoughtful call to action or reflection.
    Do not make too much length and do not summarize in bullet points—write in paragraph format.

    Summary:
    {summary}
    """
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

# Twitter/X Post Generator
def twitter_agent(summary):
    prompt = f"""
    You are a witty and creative Twitter caption writer.

    Based on the summary below, craft a short, catchy, and fun tweet. Use emojis and 2–3 relevant hashtags where appropriate.

    Summary:
    {summary}
    """
    model = genai.GenerativeModel(model_name="gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

# Flask route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        summary = summarizing_agent(query)
        fb_post = facebook_agent(summary)
        linkedin_post = linkedin_agent(summary)
        twitter_post = twitter_agent(summary)

        return render_template('index.html', summary=summary, fb=fb_post, linkedin=linkedin_post, twitter=twitter_post)

    return render_template('index.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

