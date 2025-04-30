from openai import OpenAI
import json
from typing import Dict, Any

class AIExplainer:
    def __init__(self, api_key: str):
        """初始化AI解释器"""
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
    
    def generate_explanation(self, analysis_type: str, analysis_result: Dict[str, Any], columns: list) -> str:
        """生成对分析结果的通俗解释"""
        prompt = self._create_prompt(analysis_type, analysis_result, columns)
        
        try:
            response = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "你是一个专业的数据分析师，擅长用通俗易懂的语言解释数据分析结果。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"生成解释时出错: {str(e)}"
    
    def _create_prompt(self, analysis_type: str, analysis_result: Dict[str, Any], columns: list) -> str:
        """创建用于生成解释的提示"""
        result_str = json.dumps(analysis_result, ensure_ascii=False, indent=2)
        
        # 从分析结果中获取列的描述信息
        column_info = ""
        if isinstance(analysis_result, dict) and "column_descriptions" in analysis_result:
            column_info = "\n".join([f"- {col}: {analysis_result['column_descriptions'].get(col, '未知含义')}" 
                                   for col in columns])
        else:
            # 如果没有列描述信息，则使用列名作为提示
            column_info = "\n".join([f"- {col}: 请根据列名推测其业务含义" for col in columns])
        
        prompts = {
            "summary_stats": f"""
            请用简洁的语言解释以下数据的描述性统计结果，字数控制在300字以内。
            
            数据列含义说明：
            {column_info}
            
            统计结果：
            {result_str}
            
            请结合数据列的实际含义，简要说明数据的基本特征、分布情况和主要发现。
            """,
            
            "correlation": f"""
            请用简洁的语言解释以下变量之间的相关性分析结果，字数控制在300字以内。
            
            数据列含义说明：
            {column_info}
            
            相关性矩阵：
            {result_str}
            
            请结合数据列的实际含义，简要说明：
            1. 哪些变量之间存在较强的相关性
            2. 这些相关性的业务含义
            3. 对实际应用的影响
            """,
            
            "distribution": f"""
            请用简洁的语言解释以下数据的分布分析结果，字数控制在300字以内。
            
            数据列含义说明：
            {column_info}
            
            分布分析结果：
            {result_str}
            
            请结合数据列的实际含义，简要说明数据的分布特征和主要发现。
            """,
            
            "pca": f"""
            请用简洁的语言解释以下主成分分析(PCA)的结果，字数控制在300字以内。
            
            数据列含义说明：
            {column_info}
            
            PCA分析结果：
            {result_str}
            
            请结合数据列的实际含义，简要说明主要发现和实际意义。
            """,
            
            "clustering": f"""
            请用简洁的语言解释以下聚类分析的结果，字数控制在300字以内。
            
            数据列含义说明：
            {column_info}
            
            聚类分析结果：
            {result_str}
            
            请结合数据列的实际含义，简要说明分类结果和实际意义。
            """
        }
        
        return prompts.get(analysis_type, f"""
        请用简洁的语言解释以下数据分析结果，字数控制在300字以内。
        
        数据列含义说明：
        {column_info}
        
        分析类型：{analysis_type}
        分析结果：
        {result_str}
        
        请结合数据列的实际含义，简要说明主要发现和实际意义。
        """) 