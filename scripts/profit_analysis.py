"""
Profit Analysis Script
Usage: python scripts/profit_analysis.py <query> <file1> [file2] ...
Analyzes profitability, margins, and financial metrics
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils import load_data, get_data_context, call_ai, format_output, error_output


def run_profit_analysis(query, file_paths):
    """Analyze profitability using AI"""
    df = load_data(file_paths)
    if df is None:
        return error_output("Could not load data files")

    context = get_data_context(df)

    prompt = f"""Based on this dataset, perform a profitability analysis:

USER QUERY: {query}

DATASET:
{context}

Please provide:
1. **Profit Overview**: Total profit, average profit, profit range
2. **Margin Analysis**: Profit margins by category (if available)
3. **Most Profitable**: Top profitable items/categories/segments
4. **Least Profitable**: Items with lowest profitability
5. **Profit Drivers**: What factors correlate with higher profits
6. **Profit Trends**: How profit changes over time (if date data exists)
7. **Recommendations**: How to improve profitability

Use actual numbers. Calculate totals, averages, and percentages. Present in tables where helpful."""

    system_message = "You are a financial analyst expert. Provide detailed profitability analysis with actual calculations, margins, and actionable recommendations."

    result = call_ai(prompt, system_message)
    return format_output(result, "Profit Analysis")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(error_output("Usage: python profit_analysis.py <query> <file1> [file2] ..."))
        sys.exit(1)

    query = sys.argv[1]
    file_paths = sys.argv[2:]
    print(run_profit_analysis(query, file_paths))
