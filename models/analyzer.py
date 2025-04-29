import pandas as pd
import numpy as np
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class DataAnalyzer:
    def __init__(self):
        self.data = None
    
    def analyze(self, analysis_type, columns, **kwargs):
        """执行指定类型的分析"""
        if not hasattr(self, f'_analyze_{analysis_type}'):
            raise ValueError(f"不支持的分析类型: {analysis_type}")
        
        method = getattr(self, f'_analyze_{analysis_type}')
        return method(columns, **kwargs)
    
    def _analyze_correlation(self, columns):
        """计算相关性分析"""
        if len(columns) < 2:
            raise ValueError("相关性分析需要至少两个列")
        
        # 只选择数值型列进行相关性分析
        numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(self.data[col])]
        if len(numeric_cols) < 2:
            raise ValueError("需要至少两个数值型列进行相关性分析")
        
        corr_matrix = self.data[numeric_cols].corr()
        return corr_matrix.to_dict()
    
    def _analyze_summary_stats(self, columns):
        """计算描述性统计"""
        results = {}
        
        for col in columns:
            col_stats = {}
            series = self.data[col]
            
            if pd.api.types.is_numeric_dtype(series):
                # 数值型数据的统计
                col_stats.update({
                    '平均值': float(series.mean()),
                    '中位数': float(series.median()),
                    '标准差': float(series.std()),
                    '最小值': float(series.min()),
                    '最大值': float(series.max()),
                    '四分位数': {
                        'Q1': float(series.quantile(0.25)),
                        'Q2': float(series.quantile(0.50)),
                        'Q3': float(series.quantile(0.75))
                    }
                })
            
            # 所有类型通用的统计
            col_stats.update({
                '非空值数量': int(series.count()),
                '空值数量': int(series.isnull().sum()),
                '唯一值数量': int(series.nunique()),
                '数据类型': str(series.dtype)
            })
            
            if pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
                # 分类数据的统计
                value_counts = series.value_counts()
                col_stats.update({
                    '最常见值': {
                        '值': str(value_counts.index[0]),
                        '计数': int(value_counts.iloc[0])
                    },
                    '类别分布': value_counts.head().to_dict()
                })
            
            results[col] = col_stats
        
        return results
    
    def _analyze_distribution(self, columns):
        """分析数据分布"""
        results = {}
        for col in columns:
            if not pd.api.types.is_numeric_dtype(self.data[col]):
                # 对于非数值型数据，返回类别分布
                value_counts = self.data[col].value_counts()
                results[col] = {
                    'type': 'categorical',
                    'distribution': value_counts.to_dict(),
                    'total_count': int(len(self.data[col])),
                    'unique_count': int(value_counts.count())
                }
            else:
                # 对于数值型数据，计算分布统计量
                clean_data = self.data[col].dropna()
                try:
                    skewness = float(stats.skew(clean_data))
                    kurtosis = float(stats.kurtosis(clean_data))
                    _, p_value = stats.normaltest(clean_data)
                    
                    results[col] = {
                        'type': 'numerical',
                        'skewness': skewness,
                        'kurtosis': kurtosis,
                        'is_normal': p_value > 0.05,
                        'p_value': float(p_value),
                        'histogram_data': {
                            'bins': np.histogram(clean_data, bins='auto')[0].tolist(),
                            'bin_edges': np.histogram(clean_data, bins='auto')[1].tolist()
                        }
                    }
                except:
                    results[col] = {
                        'type': 'numerical',
                        'error': '无法计算分布统计量'
                    }
        
        return results
    
    def _analyze_pca(self, columns):
        """主成分分析"""
        # 只选择数值型列
        numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(self.data[col])]
        if len(numeric_cols) < 2:
            raise ValueError("PCA分析需要至少两个数值型列")
        
        # 标准化数据
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(self.data[numeric_cols])
        
        # 执行PCA
        pca = PCA()
        transformed_data = pca.fit_transform(scaled_data)
        
        return {
            'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
            'components': pca.components_.tolist(),
            'feature_names': numeric_cols,
            'transformed_data': transformed_data.tolist()
        }
    
    def _analyze_clustering(self, columns, n_clusters=3):
        """K-means聚类分析"""
        # 只选择数值型列
        numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(self.data[col])]
        if len(numeric_cols) < 1:
            raise ValueError("聚类分析需要至少一个数值型列")
        
        # 标准化数据
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(self.data[numeric_cols])
        
        # 执行聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)
        
        # 计算每个簇的基本统计信息
        cluster_stats = {}
        for i in range(n_clusters):
            cluster_data = self.data[numeric_cols][clusters == i]
            cluster_stats[f'簇_{i}'] = {
                '样本数量': int(len(cluster_data)),
                '中心点': {col: float(cluster_data[col].mean()) for col in numeric_cols}
            }
        
        return {
            'clusters': clusters.tolist(),
            'cluster_stats': cluster_stats,
            'feature_names': numeric_cols,
            'centroids': kmeans.cluster_centers_.tolist(),
            'inertia': float(kmeans.inertia_)
        }
    
    def set_data(self, data):
        """设置要分析的数据"""
        self.data = data
        return self 