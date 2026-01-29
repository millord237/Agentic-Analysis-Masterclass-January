"""
Trend Analysis Script
Usage: python scripts/trend_analysis.py <query> <file1> [file2] ...
Analyzes time-based patterns and trends in the data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils import load_data, get_data_context, call_ai, format_output, error_output


def run_trend_analysis(query, file_paths):
    """Analyze trends using AI"""
    df = load_data(file_paths)
    if df is None:
        return error_output("Could not load data files")

    context = get_data_context(df)

    prompt = f"""Based on this dataset, analyze trends and time-based patterns:

USER QUERY: {query}

DATASET:
{context}

Please provide:
1. **Time Period Covered**: What date range does the data span
2. **Overall Trend**: Is the data trending up, down, or stable
3. **Seasonal Patterns**: Any monthly, weekly, or seasonal patterns
4. **Growth Analysis**: Calculate growth rates where possible
5. **Peak Periods**: When are the highs and lows
6. **Trend Breakdown**: By category if applicable
7. **Forecast Insight**: Based on trends, what might we expect next

Use actual numbers and calculate percentages where relevant. Show month-over-month or period comparisons."""

    system_message = "You are a data analyst expert in time series and trend analysis. Identify patterns, calculate growth rates, and provide actionable trend insights."

    result = call_ai(prompt, system_message)
    return format_output(result, "Trend Analysis")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(error_output("Usage: python trend_analysis.py <query> <file1> [file2] ..."))
        sys.exit(1)

    query = sys.argv[1]
    file_paths = sys.argv[2:]
    print(run_trend_analysis(query, file_paths))
