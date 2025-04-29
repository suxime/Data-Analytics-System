from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from models.data_processor import DataProcessor
from models.analyzer import DataAnalyzer
from models.visualizer import DataVisualizer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化处理器
data_processor = DataProcessor()
data_analyzer = DataAnalyzer()
data_visualizer = DataVisualizer()

# 存储当前数据
current_data = None

@app.route('/')
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
            df = pd.read_csv(filepath, encoding='utf-8')
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
        
        result = data_analyzer.analyze(analysis_type, columns)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'分析错误: {str(e)}'}), 500

@app.route('/visualize', methods=['POST'])
def visualize_data():
    try:
        params = request.get_json()
        viz_type = params.get('type')
        columns = params.get('columns', [])
        
        if not viz_type or not columns:
            return jsonify({'error': '缺少必要参数'}), 400
        
        result = data_visualizer.visualize(viz_type, columns)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'可视化错误: {str(e)}'}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

if __name__ == '__main__':
    app.run(debug=True) 