"""
Comparison Analysis Script
Usage: python scripts/compare_analysis.py <query> <file1> [file2] ...
Compares different categories/dimensions in the data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils import load_data, get_data_context, call_ai, format_output, error_output


def run_compare_analysis(query, file_paths):
    """Compare categories using AI analysis"""
    df = load_data(file_paths)
    if df is None:
        return error_output("Could not load data files")

    context = get_data_context(df)

    prompt = f"""Based on this dataset, perform a comparison analysis:

USER QUERY: {query}

DATASET:
{context}

Please provide:
1. **Comparison Overview**: What categories/dimensions are being compared
2. **Side-by-Side Metrics**: Key metrics for each category (use markdown table)
3. **Differences**: Significant differences between categories
4. **Similarities**: What the categories have in common
5. **Winner Analysis**: Which category performs best and why
6. **Recommendations**: Based on the comparison, what actions to consider

Use actual numbers from the data. Present comparisons in clear tables."""

    system_message = "You are a data analyst expert specializing in comparative analysis. Create clear side-by-side comparisons using data tables and highlight key differences."

    result = call_ai(prompt, system_message)
    return format_output(result, "Comparison Analysis")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(error_output("Usage: python compare_analysis.py <query> <file1> [file2] ..."))
        sys.exit(1)

    query = sys.argv[1]
    file_paths = sys.argv[2:]
    print(run_compare_analysis(query, file_paths))
