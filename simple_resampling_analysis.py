#!/usr/bin/env python3

"""
Simple Weekly Resampling Analysis Script
A direct analysis of the time_buffer_calculator's weekly_resampling method
without relying on the RAG system.
"""

import os
import sys
import json
import re
import inspect
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def extract_method_from_file(file_path, class_name, method_name):
    """Extract a method from a file using regex instead of importing."""
    try:
        logger.info(f"Reading file {file_path}")
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find the class definition
        class_pattern = rf"class\s+{class_name}\b"
        class_match = re.search(class_pattern, content)
        
        if not class_match:
            logger.error(f"{class_name} class not found in the file")
            return None
        
        # Find the method definition within the class
        class_start = class_match.start()
        # Look for the method definition after the class definition
        method_pattern = rf"def\s+{method_name}\s*\("
        method_matches = list(re.finditer(method_pattern, content[class_start:]))
        
        if not method_matches:
            logger.error(f"{method_name} method not found in {class_name}")
            return None
        
        # Extract the method and its body
        method_start = class_start + method_matches[0].start()
        
        # Find the end of the method by looking for the next def at the same indent level
        # First, determine indentation of the method
        method_line_end = content.find('\n', method_start)
        next_line_start = method_line_end + 1
        indentation = 0
        
        # Calculate indentation level
        while next_line_start < len(content) and content[next_line_start].isspace():
            indentation += 1
            next_line_start += 1
        
        # Find the end of the method by looking for the next def at the same or lower indentation
        method_end = len(content)
        next_method_pattern = rf"\n{' ' * (indentation - 4)}def\s+"
        next_method_match = re.search(next_method_pattern, content[method_start:])
        
        if next_method_match:
            method_end = method_start + next_method_match.start()
        
        # Extract the method code
        method_code = content[method_start:method_end].strip()
        
        return {
            "code": method_code,
            "parameters": extract_parameters(method_code),
            "docstring": extract_docstring(method_code)
        }
    
    except Exception as e:
        logger.error(f"Error extracting method: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def extract_parameters(method_code):
    """Extract parameters from method signature."""
    signature_match = re.search(r'def\s+\w+\s*\((.*?)\):', method_code, re.DOTALL)
    if not signature_match:
        return []
    
    signature = signature_match.group(1).strip()
    if not signature:
        return []
    
    # Split by comma, but handle default values
    params = []
    curr_param = ""
    paren_count = 0
    
    for char in signature:
        if char == ',' and paren_count == 0:
            params.append(curr_param.strip())
            curr_param = ""
        else:
            curr_param += char
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
    
    if curr_param:
        params.append(curr_param.strip())
    
    # Clean up parameters (remove annotations and default values)
    clean_params = []
    for p in params:
        param_name = p.split(':')[0].split('=')[0].strip()
        clean_params.append(param_name)
    
    return clean_params

def extract_docstring(method_code):
    """Extract docstring from method code."""
    docstring_match = re.search(r'"""(.*?)"""', method_code, re.DOTALL)
    if docstring_match:
        return docstring_match.group(1).strip()
    
    return None

def analyze_weekly_resampling(file_path):
    """Analyze the weekly_resampling method from the TimeBufferCalculator."""
    try:
        # Extract method code
        method_info = extract_method_from_file(file_path, "TimeBufferCalculator", "weekly_resampling")
        
        if not method_info:
            return None
        
        # Generate sample data for analysis
        sample_data = generate_sample_data()
        
        # Create simple analysis
        analysis = {
            "method_name": "weekly_resampling",
            "source_file": file_path,
            "parameters": method_info["parameters"],
            "docstring": method_info["docstring"],
            "source_code_length": len(method_info["code"].split('\n')),
            "dependencies": extract_dependencies(method_info["code"]),
            "sample_data_analysis": analyze_with_sample_data(sample_data),
            "timestamp": datetime.now().isoformat()
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing weekly_resampling: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def extract_dependencies(source_code):
    """Extract likely dependencies from the source code."""
    dependencies = []
    
    # Common patterns to look for
    patterns = [
        ("pandas", ["pd.", "pandas."]),
        ("numpy", ["np.", "numpy."]),
        ("datetime", ["datetime.", "timedelta"]),
        ("logging", ["logger.", "logging."]),
        ("SQLAlchemy", ["session.", "query(", "filter("])
    ]
    
    for lib, patterns in patterns:
        for pattern in patterns:
            if pattern in source_code:
                if lib not in dependencies:
                    dependencies.append(lib)
                    break
    
    return dependencies

def generate_sample_data():
    """Generate sample transition data for analysis."""
    # Create date range for the past 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    date_range = pd.date_range(start=start_date, end=end_date, freq='H')
    
    # Generate random transition times
    np.random.seed(42)  # For reproducibility
    
    # Create a sample dataframe
    data = []
    for date in date_range:
        if 8 <= date.hour <= 18:  # Working hours
            # Add more transitions during work hours
            if np.random.random() < 0.3:  # 30% chance of a transition
                transition_time = np.random.randint(5, 30)  # 5-30 minutes
                
                # Create more transitions on weekdays
                if date.weekday() < 5:  # 0-4 are Monday to Friday
                    data.append({
                        'user_id': 'user123',
                        'transition_timestamp': date,
                        'transition_time_minutes': transition_time,
                        'from_task_id': f'task_{np.random.randint(1, 10)}',
                        'to_task_id': f'task_{np.random.randint(1, 10)}'
                    })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    return df

def analyze_with_sample_data(sample_data):
    """Perform a simple weekly resampling analysis on sample data."""
    try:
        # Group by day of week
        sample_data['day_of_week'] = sample_data['transition_timestamp'].dt.dayofweek
        sample_data['day_name'] = sample_data['transition_timestamp'].dt.day_name()
        
        # Calculate weekly statistics
        weekly_stats = sample_data.groupby('day_name')['transition_time_minutes'].agg([
            'count', 'mean', 'std', 'min', 'max'
        ]).reset_index()
        
        # Add time of day analysis
        sample_data['hour'] = sample_data['transition_timestamp'].dt.hour
        sample_data['time_of_day'] = pd.cut(
            sample_data['hour'], 
            bins=[0, 6, 12, 18, 24], 
            labels=['Night', 'Morning', 'Afternoon', 'Evening']
        )
        
        time_of_day_stats = sample_data.groupby('time_of_day')['transition_time_minutes'].mean()
        
        return {
            "weekly_pattern": weekly_stats.to_dict('records'),
            "time_of_day_pattern": time_of_day_stats.to_dict(),
            "data_points": len(sample_data),
            "date_range": {
                "start": sample_data['transition_timestamp'].min().isoformat() if not sample_data.empty else None,
                "end": sample_data['transition_timestamp'].max().isoformat() if not sample_data.empty else None
            }
        }
    except Exception as e:
        logger.error(f"Error in sample data analysis: {str(e)}")
        return {"error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_resampling_analysis.py <path_to_time_buffer_calculator.py> [output_file]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "weekly_resampling_simple_analysis.json"
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        sys.exit(1)
    
    analysis = analyze_weekly_resampling(file_path)
    
    if analysis:
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"Analysis saved to {output_file}")
    else:
        print("Analysis failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 