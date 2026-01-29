"""
Top Performers Analysis Script
Usage: python scripts/top_analysis.py <query> <file1> [file2] ...
Finds top/best/highest performers in the data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils import load_data, get_data_context, call_ai, format_output, error_output


def run_top_analysis(query, file_paths):
    """Find top performers using AI analysis"""
    df = load_data(file_paths)
    if df is None:
        return error_output("Could not load data files")

    context = get_data_context(df)

    prompt = f"""Based on this dataset, answer the user's query about top performers:

USER QUERY: {query}

DATASET:
{context}

Please provide:
1. **Top Performers**: List the top items/categories based on the query
2. **Rankings**: Show rankings with actual values and percentages
3. **Comparison**: How the top performers compare to the average
4. **Analysis**: Why these might be the top performers
5. **Visualization Suggestion**: What chart would best show this data

Use actual numbers from the data. Format with markdown tables where appropriate."""

    system_message = "You are a data analyst expert. When asked about 'top' or 'best', analyze the data to find and rank the highest performers. Always use actual numbers from the data."

    result = call_ai(prompt, system_message)
    return format_output(result, "Top Performers Analysis")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(error_output("Usage: python top_analysis.py <query> <file1> [file2] ..."))
        sys.exit(1)

    query = sys.argv[1]
    file_paths = sys.argv[2:]
    print(run_top_analysis(query, file_paths))
