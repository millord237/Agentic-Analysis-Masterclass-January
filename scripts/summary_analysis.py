"""
Summary Analysis Script
Usage: python scripts/summary_analysis.py <file1> [file2] ...
Generates a comprehensive summary of the dataset using AI
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils import load_data, get_data_context, call_ai, format_output, error_output


def run_summary_analysis(file_paths):
    """Generate AI-powered summary analysis"""
    df = load_data(file_paths)
    if df is None:
        return error_output("Could not load data files")

    context = get_data_context(df)

    prompt = f"""Analyze this dataset and provide a comprehensive summary:

{context}

Please provide:
1. **Overview**: What this data represents
2. **Key Statistics**: Important numbers and metrics
3. **Data Quality**: Any missing values, anomalies, or issues
4. **Column Analysis**: Brief description of each column's purpose
5. **Initial Insights**: 3-5 interesting observations from the data

Format your response in clear markdown with headers and bullet points."""

    system_message = "You are a data analyst expert. Provide clear, actionable insights from data. Use markdown formatting."

    result = call_ai(prompt, system_message)
    return format_output(result, "Data Summary")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(error_output("Please provide at least one data file path"))
        sys.exit(1)

    file_paths = sys.argv[1:]
    print(run_summary_analysis(file_paths))
