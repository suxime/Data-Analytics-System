from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import os
import json
from init_db import init_db
from datetime import datetime
from models.data_processor import DataProcessor
from models.analyzer import DataAnalyzer
from models.visualizer import DataVisualizer
from models.user import User
from models.ai_explainer import AIExplainer
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
app.secret_key = os.urandom(24)  # 为session设置密钥

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化处理器
data_processor = DataProcessor()
data_analyzer = DataAnalyzer()
data_visualizer = DataVisualizer()
ai_explainer = AIExplainer(api_key=os.getenv('DASHSCOPE_API_KEY'))  # 从环境变量获取API密钥

# 存储当前数据
current_data = None

# 初始化Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        
        flash('用户名或密码错误')
    return render_template('login.html')

# 注册路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.get_by_username(username):
            flash('用户名已存在')
            return render_template('register.html')
        
        user = User.create(username, password)
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('register.html')

# 登出路由
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件被上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 读取并处理数据
        try:
            global current_data
            # 根据文件扩展名选择读取方式
            if filename.endswith('.csv'):
                df = pd.read_csv(filepath, encoding='utf-8')
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath, engine='openpyxl')
            # 保存处理后的数据
            current_data = data_processor.process_data(df)
            # 设置数据给分析器和可视化器
            data_analyzer.data = current_data
            data_visualizer.set_data(current_data)
            
            return jsonify({
                'message': '文件上传成功',
                'columns': list(current_data.columns),
                'preview': current_data.head().to_dict()
            })
        except Exception as e:
            return jsonify({'error': f'数据处理错误: {str(e)}'}), 500
    
    return jsonify({'error': '不支持的文件类型'}), 400

@app.route('/analyze', methods=['POST'])
def analyze_data():
    try:
        params = request.get_json()
        analysis_type = params.get('type')
        columns = params.get('columns', [])
        
        if not analysis_type or not columns:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 执行分析
        result = data_analyzer.analyze(analysis_type, columns)
        
        # 生成AI解释
        try:
            explanation = ai_explainer.generate_explanation(analysis_type, result, columns)
        except Exception as e:
            explanation = f"生成解释时出错: {str(e)}"
        
        return jsonify({
            'analysis_result': result,
            'explanation': explanation
        })
    except Exception as e:
        return jsonify({'error': f'分析错误: {str(e)}'}), 500

@app.route('/visualize', methods=['POST'])
@login_required
def visualize():
    if current_data is None or current_data.empty:
        return jsonify({'error': '请先上传数据'})
    
    try:
        data = json.loads(request.data)
        viz_type = data.get('type')
        columns = data.get('columns', [])
        
        if not viz_type or not columns:
            return jsonify({'error': '请选择图表类型和数据列'})
        
        # 生成可视化
        viz_result = data_visualizer.visualize(viz_type, columns)
        
        # 生成AI解释
        explanation = ai_explainer.generate_explanation(
            analysis_type=f"visualization_{viz_type}",
            analysis_result=viz_result,
            columns=columns
        )
        
        # 将解释添加到结果中
        viz_result['explanation'] = explanation
        
        return jsonify(viz_result)
    except Exception as e:
        return jsonify({'error': str(e)})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

if __name__ == '__main__':
    init_db() # 初始化数据库
    app.run(debug=True)