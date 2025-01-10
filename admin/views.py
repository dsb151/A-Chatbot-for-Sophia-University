from flask import render_template, request, redirect, url_for, jsonify
from . import admin_bp  # 使用定义的蓝图对象
import json

def load_qa_data():
    with open('qa1.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_qa_data(data):
    with open('qa1.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 路由：显示管理界面
@admin_bp.route('/admin', methods=['GET'])
def admin_panel():
    qa_data = load_qa_data()
    return render_template('admin.html', questions_html=generate_question_html(qa_data), questions_data=json.dumps(qa_data))


# 路由：编辑问题
@admin_bp.route('/edit_question', methods=['POST'])
def edit_question():
    data = request.get_json()
    path = data['path']
    question_text = data['question']
    answer_text = data.get('answer', '')

    qa_data = load_qa_data()

    # 通过路径找到要编辑的问题
    def find_question_by_path(data, path):
        indices = list(map(int, path.replace('-', '/').split('/')))
        for index in indices:
            data = data[index]['sub_questions']
        return data

    try:
        indices = list(map(int, path.replace('-', '/').split('/')))
        target = qa_data
        for index in indices[:-1]:
            target = target[index]['sub_questions']
        target_question = target[indices[-1]]

        # 更新问题和答案
        target_question['question'] = question_text
        if 'answer' in target_question:
            target_question['answer'] = answer_text

        save_qa_data(qa_data)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 路由：添加分支问题或子问题
@admin_bp.route('/add_sub_question', methods=['POST'])
def add_sub_question():
    data = request.get_json()
    question_type = data['type']  # 判断是添加分支问题还是子问题
    path = data['path']  # 问题路径
    question = data['question']
    answer = data.get('answer', '')

    qa_data = load_qa_data()

    # 通过路径找到父问题
    def find_question_by_path(data, path):
        indices = list(map(int, path.split('-')))
        for index in indices:
            data = data[index]['sub_questions']
        return data

    try:
        target_list = find_question_by_path(qa_data, path)

        if question_type == 'branch':
            target_list.append({'question': question, 'answer': "", 'sub_questions': []})
        elif question_type == 'sub':
            target_list.append({'question': question, 'answer': answer, 'sub_questions': []})

        save_qa_data(qa_data)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 删除问题的路由
@admin_bp.route('/delete_question', methods=['POST'])
def delete_question():
    path = request.form.get('path')
    qa_data = load_qa_data()

    def delete_from_list(data_list, path):
        indices = list(map(int, path.split('/')))
        for index in indices[:-1]:
            data_list = data_list[index]['sub_questions']
        del data_list[indices[-1]]

    try:
        delete_from_list(qa_data, path)
        save_qa_data(qa_data)
        return redirect(url_for('admin.admin_panel'))
    except IndexError:
        return "Error: Invalid path", 404

# 生成现有问题的 HTML
def generate_question_html(questions, path=''):
    html = '<ul>'
    for index, question in enumerate(questions):
        current_path = f"{path}/{index}" if path else str(index)

        # 只有子问题显示答案框
        answer_html = ''
        if 'answer' in question and question['answer'] != "":  # 只显示有答案的子问题
            answer_html = f"""
                <textarea name="answer" placeholder="答案" rows="8" style="width: 800px;">{question['answer']}</textarea>
            """

        html += f"""
            <li id="question-{current_path.replace('/', '-')}">
                <form onsubmit="submitEdit(this, '{current_path}'); return false;">
                    <input type="hidden" name="path" value="{current_path}">
                    <input type="text" name="question" value="{question['question']}" style="width: 600px;">
                    {answer_html}
                    <button type="submit">編集</button>
                </form>
                <form action="/delete_question" method="POST" style="display:inline;">
                    <input type="hidden" name="path" value="{current_path}">
                    <button type="submit">削除</button>
                </form>
                <button type="button" onclick="openPopup('branch', '{current_path.replace('/', '-')}')">分岐を添加する</button>
                <button type="button" onclick="openPopup('sub', '{current_path.replace('/', '-')}')">サブ問題を添加する</button>
        """
        if question.get('sub_questions'):
            html += generate_question_html(question['sub_questions'], current_path)
        html += "</li>"
    html += '</ul>'
    return html

