import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json

class DataVisualizer:
    def __init__(self):
        self.data = None
    
    def visualize(self, viz_type, columns, **kwargs):
        """生成指定类型的可视化"""
        if not hasattr(self, f'_viz_{viz_type}'):
            raise ValueError(f"不支持的可视化类型: {viz_type}")
        
        method = getattr(self, f'_viz_{viz_type}')
        fig = method(columns, **kwargs)
        
        # 确保返回的是可序列化的JSON格式
        return json.loads(fig.to_json())
    
    def _viz_scatter(self, columns):
        """散点图"""
        if len(columns) != 2:
            raise ValueError("散点图需要恰好两个列")
        
        # 检查是否为数值型数据
        if not all(pd.api.types.is_numeric_dtype(self.data[col]) for col in columns):
            raise ValueError("散点图需要数值型数据")
        
        fig = px.scatter(self.data, x=columns[0], y=columns[1],
                        title=f"{columns[0]} vs {columns[1]}的散点图")
        fig.update_layout(
            xaxis_title=columns[0],
            yaxis_title=columns[1]
        )
        return fig
    
    def _viz_histogram(self, columns):
        """直方图"""
        if len(columns) != 1:
            raise ValueError("直方图需要恰好一个列")
        
        column = columns[0]
        if pd.api.types.is_numeric_dtype(self.data[column]):
            # 数值型数据使用常规直方图
            fig = px.histogram(self.data, x=column,
                             title=f"{column}的分布直方图")
            fig.update_layout(
                xaxis_title=column,
                yaxis_title="频数"
            )
        else:
            # 分类数据使用条形图显示频数
            value_counts = self.data[column].value_counts()
            fig = px.bar(x=value_counts.index, y=value_counts.values,
                        title=f"{column}的类别分布")
            fig.update_layout(
                xaxis_title=column,
                yaxis_title="频数"
            )
        return fig
    
    def _viz_box(self, columns):
        """箱线图"""
        # 只处理数值型列
        numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(self.data[col])]
        if not numeric_cols:
            raise ValueError("箱线图需要至少一个数值型列")
        
        fig = px.box(self.data, y=numeric_cols,
                     title="数值分布箱线图")
        fig.update_layout(
            xaxis_title="变量",
            yaxis_title="数值"
        )
        return fig
    
    def _viz_correlation_heatmap(self, columns):
        """相关性热力图"""
        # 只处理数值型列
        numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(self.data[col])]
        if len(numeric_cols) < 2:
            raise ValueError("相关性热力图需要至少两个数值型列")
        
        corr_matrix = self.data[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmin=-1, zmax=1
        ))
        
        fig.update_layout(
            title="相关性热力图",
            xaxis_title="变量",
            yaxis_title="变量"
        )
        return fig
    
    def _viz_line(self, columns, x_column=None):
        """折线图"""
        # 如果指定了x轴，检查是否为时间序列
        if x_column and pd.api.types.is_datetime64_any_dtype(self.data[x_column]):
            x_data = self.data[x_column]
        else:
            x_data = self.data.index
        
        # 只处理数值型列
        numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(self.data[col])]
        if not numeric_cols:
            raise ValueError("折线图需要至少一个数值型列")
        
        fig = go.Figure()
        for col in numeric_cols:
            fig.add_trace(go.Scatter(
                x=x_data,
                y=self.data[col],
                name=col,
                mode='lines+markers'
            ))
        
        fig.update_layout(
            title="时间序列分析" if pd.api.types.is_datetime64_any_dtype(x_data) else "趋势分析",
            xaxis_title=x_column if x_column else "索引",
            yaxis_title="数值"
        )
        return fig
    
    def _viz_bar(self, columns):
        """柱状图"""
        if len(columns) == 1:
            column = columns[0]
            if pd.api.types.is_numeric_dtype(self.data[column]):
                # 数值型数据，显示分布
                bins = pd.cut(self.data[column], bins=10)
                value_counts = bins.value_counts().sort_index()
                fig = px.bar(x=[str(x) for x in value_counts.index], 
                            y=value_counts.values,
                            title=f"{column}的分布柱状图")
            else:
                # 分类数据，显示频数
                # 确保使用原始数据进行计数
                value_counts = pd.DataFrame(self.data[column].value_counts()).reset_index()
                value_counts.columns = ['category', 'count']
                
                # 创建柱状图
                fig = px.bar(value_counts, 
                            x='category',
                            y='count',
                            title=f"{column}的类别分布",
                            text='count')
                
                # 更新图表显示
                fig.update_traces(
                    textposition='outside',
                    texttemplate='%{text}',  # 确保显示为正确的文本值
                    hovertemplate='%{x}<br>数量: %{y}<extra></extra>'
                )
                
                # 更新布局
                fig.update_layout(
                    xaxis_title=column,
                    yaxis_title="数量",
                    showlegend=False,
                    xaxis={'type': 'category'},
                    yaxis={
                        'range': [0, max(value_counts['count']) * 1.1],  # 设置y轴范围
                        'dtick': 1  # 设置y轴刻度间隔为1
                    },
                    margin=dict(t=50, b=50, l=50, r=50),
                    bargap=0.2  # 调整柱子间距
                )
            
        else:
            # 多列比较，只使用数值型列
            numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(self.data[col])]
            if not numeric_cols:
                raise ValueError("多列柱状图需要至少一个数值型列")
            
            # 计算每列的统计值
            summary_data = pd.DataFrame({
                'variable': numeric_cols,
                'value': [self.data[col].mean() for col in numeric_cols]
            })
            
            fig = px.bar(summary_data,
                        x='variable',
                        y='value',
                        title="多变量对比柱状图",
                        text=summary_data['value'].round(2))
            
            fig.update_traces(
                textposition='outside',
                texttemplate='%{text}',
                hovertemplate='%{x}<br>平均值: %{y:.2f}<extra></extra>'
            )
            
            fig.update_layout(
                xaxis_title="变量",
                yaxis_title="平均值",
                showlegend=False,
                xaxis={'type': 'category'},
                yaxis={'range': [0, max(summary_data['value']) * 1.1]},
                margin=dict(t=50, b=50, l=50, r=50)
            )
        return fig
    
    def _viz_pie(self, columns):
        """饼图"""
        if len(columns) != 1:
            raise ValueError("饼图需要恰好一个列")
        
        column = columns[0]
        value_counts = self.data[column].value_counts()
        
        if len(value_counts) > 10:
            # 如果类别太多，只显示前10个
            other_count = value_counts[10:].sum()
            value_counts = value_counts[:10]
            value_counts['其他'] = other_count
        
        fig = px.pie(values=value_counts.values, 
                    names=value_counts.index,
                    title=f"{column}的占比分布")
        return fig
    
    def set_data(self, data):
        """设置要可视化的数据"""
        if data is None or data.empty:
            raise ValueError("数据为空，无法设置")
        self.data = data.copy(deep=True)
        # 将日期列转换为datetime类型
        for col in self.data.columns:
            if col == '日期':  # 只处理日期列
                try:
                    self.data[col] = pd.to_datetime(self.data[col], format='%Y-%m-%d')
                except Exception as e:
                    raise ValueError(f"日期列转换失败: {str(e)}")
        return self