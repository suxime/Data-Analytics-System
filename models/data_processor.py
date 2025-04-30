import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class DataProcessor:
    def __init__(self):
        self.data = None
        self.scaler = StandardScaler()
    
    def process_data(self, df):
        """处理输入的数据框"""
        # 创建深拷贝以避免修改原始数据
        self.data = df.copy(deep=True)
        
        # 基础清洗
        self._remove_duplicates()
        self._handle_missing_values()
        self._convert_datatypes()
        
        return self.data
    
    def _remove_duplicates(self):
        """删除重复行，保留第一次出现的记录"""
        self.data.drop_duplicates(keep='first', inplace=True)
    
    def _handle_missing_values(self):
        """处理缺失值"""
        # 数值型列用均值填充
        numeric_columns = self.data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            # 避免链式赋值
            self.data[col] = self.data[col].fillna(self.data[col].mean())
        
        # 分类型列用众数填充
        categorical_columns = self.data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            # 避免链式赋值
            self.data[col] = self.data[col].fillna(self.data[col].mode()[0])
    
    def _convert_datatypes(self):
        """转换数据类型，保持分类列不变"""
        # 保持这些列为分类数据
        category_columns = ['产品类别', '地区']
        
        for col in self.data.columns:
            if col not in category_columns:
                try:
                    # 尝试转换为数值类型
                    numeric_values = pd.to_numeric(self.data[col])
                    self.data[col] = numeric_values
                except:
                    continue
    
    def normalize_data(self, columns):
        """标准化选定的数值列"""
        if not all(col in self.data.columns for col in columns):
            raise ValueError("某些指定的列不存在")
        
        self.data[columns] = self.scaler.fit_transform(self.data[columns])
        return self.data
    
    def get_data_info(self):
        """获取数据基本信息"""
        return {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict()
        }
    
    def get_column_stats(self, column):
        """获取指定列的统计信息"""
        if column not in self.data.columns:
            raise ValueError(f"列 {column} 不存在")
        
        stats = {
            'mean': float(self.data[column].mean()) if pd.api.types.is_numeric_dtype(self.data[column]) else None,
            'median': float(self.data[column].median()) if pd.api.types.is_numeric_dtype(self.data[column]) else None,
            'std': float(self.data[column].std()) if pd.api.types.is_numeric_dtype(self.data[column]) else None,
            'unique_values': len(self.data[column].unique()),
            'missing_values': int(self.data[column].isnull().sum())
        }
        
        return stats 