from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
from sentence_transformers import SentenceTransformer, util
import os

app = Flask(__name__, template_folder='public')
CORS(app)
app.secret_key = os.urandom(24)

def load_qa_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(f"Error loading QA data: {e}")
        return None

def embed_sentences(model, sentences):
    return model.encode(sentences)

def get_all_questions(qa_data):
    questions = []

    def recurse(data):
        for item in data:
            questions.append(item['question'])


            if 'sub_questions' in item:
                recurse(item['sub_questions'])

    recurse(qa_data)
    return questions

qa_data_path = "qa1.json"
qa_data = load_qa_data(qa_data_path)
if qa_data is None:
    print("Failed to load QA data. Exiting.")
    exit(1)

model_name = "pkshatech/simcse-ja-bert-base-clcmlp"
model = SentenceTransformer(model_name)
question_sentences = get_all_questions(qa_data)
sentences_embedding = embed_sentences(model, question_sentences)

feedback_data = {}  # 用于记录反馈信息

def find_answer_and_sub_questions(qa_data, question):
    for item in qa_data:
        if item['question'] == question:
            answer = item.get('answer', None)
            sub_questions = item.get('sub_questions', [])
            if answer is None and sub_questions:
                return find_answer_and_sub_questions(sub_questions, question)
            return answer, sub_questions
        if 'sub_questions' in item:
            answer, sub_questions = find_answer_and_sub_questions(item['sub_questions'], question)
            if answer is not None or sub_questions:
                return answer, sub_questions
    return None, []

@app.route('/qa', methods=['POST'])
def handle_qa():
    data = request.json
    question = data.get('question')
    session.modified = True

    if 'dialogue_state' not in session:
        session['dialogue_state'] = []

    dialogue_state = session['dialogue_state']
    query_embedding = embed_sentences(model, [question])
    cosine_scores = util.pytorch_cos_sim(query_embedding, sentences_embedding)[0]
    sorted_indices = cosine_scores.argsort(descending=True).tolist()

    suggested_questions = []
    threshold = 0.7
    for index in sorted_indices:
        if cosine_scores[index] >= threshold:
            suggested_questions.append(question_sentences[index])
        if len(suggested_questions) >= 3:
            break

    dialogue_state.append({'question': question})
    session['dialogue_state'] = dialogue_state

    return jsonify({
        'suggestions': suggested_questions,
        'dialogue_state': dialogue_state
    })

@app.route('/qa_answer', methods=['POST'])
def handle_qa_answer():
    data = request.json
    question = data.get('question')
    session.modified = True

    dialogue_state = session.get('dialogue_state', [])
    query_embedding = embed_sentences(model, [question])
    cosine_scores = util.pytorch_cos_sim(query_embedding, sentences_embedding)[0]
    sorted_indices = cosine_scores.argsort(descending=True).tolist()

    answer, sub_questions = find_answer_and_sub_questions(qa_data, question_sentences[sorted_indices[0]])
    if answer is None:
        answer = '申し訳ありませんが、その質問にはお答えできません。'

    dialogue_state.append({'question': question, 'answer': answer})
    session['dialogue_state'] = dialogue_state

    return jsonify({
        'answer': answer,
        'sub_questions': sub_questions,
        'dialogue_state': dialogue_state
    })

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    question = data.get('question')
    feedback = data.get('feedback')
    # 这里可以将反馈保存到数据库或文件中
    print(f"Feedback for question '{question}': {feedback}")
    return jsonify({"status": "success"})

@app.route('/main_questions', methods=['GET'])
def get_main_questions():
    main_questions = [item['question'] for item in qa_data]
    return jsonify(main_questions)

@app.route('/questions', methods=['GET'])
def get_questions():
    return jsonify(question_sentences)

@app.route('/')
def index():
    session.pop('dialogue_state', None)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)











