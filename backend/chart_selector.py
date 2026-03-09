import pandas as pd
import numpy as np
import google.generativeai as genai
import json
import re

class ChartSelector:
    def __init__(self, api_key=None):
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
        else:
            self.model = None
    def select_chart(self, df, natural_query):
        """Select the best chart type based on data and query"""
        
        # Basic data characteristics
        num_rows, num_cols = df.shape
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Rule-based fallback selection
        if len(numeric_cols) == 0:
            chart_type = "table"
        elif len(df) == 1:
            if len(numeric_cols) >= 1:
                chart_type = "indicator"
            else:
                chart_type = "table"
        elif len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            if len(df[categorical_cols[0]].unique()) <= 5 and len(numeric_cols) == 1:
                chart_type = "bar"
            elif len(df) > 10:
                chart_type = "line"
            else:
                chart_type = "bar"
        else:
            chart_type = "bar"
        
        # Use LLM for better selection if available
        if self.model:
            chart_type = self._llm_chart_selection(df, natural_query, chart_type)
        
        # Configure chart options
        chart_config = self._get_chart_config(chart_type, df, natural_query)
        
        return chart_config
    
    def _llm_chart_selection(self, df, natural_query, fallback_type):
        """Use LLM to select the best chart type"""

        prompt = f"""
        Based on this data sample and user query, suggest the best visualization.

        User query: "{natural_query}"

        Data shape: {df.shape}
        Columns: {list(df.columns)}
        Column types: { {col: str(dt) for col, dt in zip(df.columns, df.dtypes)} }
        Sample rows:
        {df.head(3).to_dict(orient='records')}

        Available chart types: bar, line, pie, scatter, area, histogram, box, heatmap, table, indicator

        Rules:
        - Use 'bar' for comparing categories.
        - Use 'line' for time series or trends.
        - Use 'pie' for parts-of-a-whole with <= 8 categories.
        - Use 'scatter' for correlation between two numeric columns.
        - Use 'indicator' when the result is a single number.
        - Use 'table' when data has many columns or is textual.

        Return ONLY the chart type name (one word, lowercase):
        """

        try:
            response = self.model.generate_content(prompt)
            chart_type = response.text.strip().lower()
            
            # Clean up potential markdown
            chart_type = re.sub(r'[^a-z]', '', chart_type)
            
            # Validate chart type
            valid_types = ['bar', 'line', 'pie', 'scatter', 'area', 'histogram', 'box', 'heatmap', 'table', 'indicator']
            if chart_type not in valid_types:
                return fallback_type
            
            return chart_type
        except:
            return fallback_type
    
    def _get_chart_config(self, chart_type, df, natural_query):
        """Generate chart configuration"""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'datetime']).columns.tolist()
        
        config = {
            "type": chart_type,
            "title": natural_query[:50] + "..." if len(natural_query) > 50 else natural_query,
            "data": df.to_dict(orient='records')
        }
        
        # Add specific configurations based on chart type
        if chart_type == "bar":
            config.update({
                "x": categorical_cols[0] if categorical_cols else df.columns[0],
                "y": numeric_cols[0] if numeric_cols else (df.columns[1] if len(df.columns) > 1 else df.columns[0]),
                "color": categorical_cols[1] if len(categorical_cols) > 1 else None
            })
        elif chart_type == "line":
            config.update({
                "x": categorical_cols[0] if categorical_cols else df.columns[0],
                "y": numeric_cols if numeric_cols else [df.columns[1]] if len(df.columns) > 1 else [df.columns[0]],
                "color": categorical_cols[1] if len(categorical_cols) > 1 else None
            })
        elif chart_type == "pie":
            config.update({
                "names": categorical_cols[0] if categorical_cols else df.columns[0],
                "values": numeric_cols[0] if numeric_cols else (df.columns[1] if len(df.columns) > 1 else df.columns[0])
            })
        elif chart_type == "scatter":
            config.update({
                "x": numeric_cols[0] if len(numeric_cols) > 0 else df.columns[0],
                "y": numeric_cols[1] if len(numeric_cols) > 1 else (df.columns[1] if len(df.columns) > 1 else df.columns[0]),
                "color": categorical_cols[0] if categorical_cols else None,
                "size": numeric_cols[2] if len(numeric_cols) > 2 else None
            })
        
        return config
