from flask import Flask, render_template, request, redirect, url_for
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import PyPDF2

app = Flask(__name__)
os.environ['GOOGLE_API_KEY'] = "AIzaSyCWkH8hooiAuzIcoWHAYDndgw61wb0-Yrc"
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
llm = ChatGoogleGenerativeAI(model='gemini-pro')

def bot(conversation_history, user_data):
    template = """
        You are an experienced HR professional conducting a general interview round. Your goal is to assess the candidate's skills, experience, and fit for the role based on their resume. 

        Resume content:
        {resume}

        Conversation history:
        {history}

        Instructions:
        - Provide a brief suggestion to improve the candidate's previous response. Be constructive and specific.
        - Then, ask only one question at a time, focusing on the most relevant aspects of the candidate's background.
        - Maintain a professional yet engaging tone throughout the interview.

        Question types to include if mentioned in resume:
        - Skills assessment: "Can you elaborate on your experience with [specific skill mentioned in resume]?"
        - Achievement exploration: "I see you [accomplished X]. Can you walk me through how you achieved that?"
        - Project deep-dive: "Tell me more about your role in [specific project from resume]."
        - Behavioral questions: "Describe a situation where you [relevant scenario based on job requirements]."
        - Problem-solving scenarios: "How would you approach [hypothetical situation related to the role]?"

        Remember to keep your responses conversational and avoid repetitive phrasing. Tailor each question to the candidate's unique background and the information they've shared so far.
        Based on the conversation history and resume, provide your suggestion for improvement and then your next question:
    """
    
    history_text = "\n".join([f"Bot: {entry['bot']}\nUser: {entry['user']}" for entry in conversation_history])
    
    prompt = PromptTemplate(
        input_variables=['history', 'resume'],
        template=template
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(history=history_text, resume=user_data)
    
    parts = response.split('\n', 1)
    suggestion = parts[0].strip()
    question = parts[1].strip() if len(parts) > 1 else ""
    
    return f"{suggestion}\n{question}"

def extract_text_from_pdf(pdf_file):
    text = ""
    with open(pdf_file, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

conversation_history = []
initial_question = "Tell me about yourself"
conversation_history.append({'bot': initial_question, 'user': ''})

@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('home.html')

@app.route('/resume', methods=['POST', 'GET'])
def resume():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            file_path = os.path.join(file.filename)
            file.save(file_path)
            global data
            data = extract_text_from_pdf(file_path)
            return redirect('/chat')
    return render_template('upload.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    global data
    user_data = data
    if request.method == "POST":
        user = request.form.get('user')
        if user:
            bot_response = bot(conversation_history, user_data)
            conversation_history.append({'bot': bot_response, 'user': user})
        return render_template('index.html', conversation_history=conversation_history)
    return render_template('index.html', conversation_history=conversation_history)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
