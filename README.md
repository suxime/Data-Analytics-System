# 交互式数据分析系统

这是一个基于Python和Flask的交互式数据分析系统，提供数据上传、处理、分析和可视化功能。

## 功能特点

1. 数据管理
   - 支持CSV/Excel文件上传
   - 数据预览和基本信息显示
   - 数据存储和管理

2. 数据清洗
   - 缺失值处理
   - 异常值检测
   - 数据类型转换
   - 数据标准化

3. 数据可视化
   - 散点图
   - 直方图
   - 箱线图
   - 相关性热力图
   - 折线图
   - 柱状图
   - 饼图

4. 分析功能
   - 描述性统计
   - 相关性分析
   - 分布分析
   - 主成分分析
   - 聚类分析

5. AI 解释功能
   - 基于 DashScope API，为分析结果生成通俗易懂的解释
   - 帮助用户更好地理解数据分析的意义和结果

## 系统要求

- Python 3.7+
- 其他依赖见 requirements.txt

## 安装步骤

1. 克隆项目到本地：
```bash
git clone <repository_url>
cd interactive-data-analysis
```

2. 创建并激活虚拟环境（可选但推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 启动应用：
```bash
python app.py
```

2. 在浏览器中访问：
```
http://localhost:5000
```

3. 使用流程：
   - 上传数据文件（支持CSV、Excel格式）
   - 选择要分析的数据列
   - 选择分析类型或可视化类型
   - 查看结果

## 项目结构

```
interactive-data-analysis/
├── app.py                 # 主应用程序
├── requirements.txt       # 项目依赖
├── README.md             # 项目文档
├── models/               # 模型文件
│   ├── data_processor.py # 数据处理类
│   ├── analyzer.py       # 数据分析类
│   ├── visualizer.py     # 数据可视化类
│   ├── ai_explainer.py   # AI 解释功能类
└── templates/            # 前端模板
    └── index.html        # 主页面
```

## 环境变量配置

在项目根目录下创建一个 `.env` 文件，并添加以下内容：

```
DASHSCOPE_API_KEY="your_api_key_here"
```

将 `your_api_key_here` 替换为你的实际 API 密钥。此密钥用于支持 AI 解释功能。

## 注意事项

1. 文件大小限制为16MB
2. 支持的文件格式：CSV、Excel（.xlsx、.xls）
3. 建议使用现代浏览器（Chrome、Firefox、Edge等）以获得最佳体验

## 开发者信息

如需报告问题或贡献代码，请：
1. 提交Issue描述问题
2. 创建Pull Request提交改进
3. 遵循项目的代码规范

## 许可证

MIT License