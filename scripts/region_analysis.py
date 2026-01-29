"""
Regional/Geographic Analysis Script
Usage: python scripts/region_analysis.py <query> <file1> [file2] ...
Analyzes geographic distribution and regional performance
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils import load_data, get_data_context, call_ai, format_output, error_output


def run_region_analysis(query, file_paths):
    """Analyze regional data using AI"""
    df = load_data(file_paths)
    if df is None:
        return error_output("Could not load data files")

    context = get_data_context(df)

    prompt = f"""Based on this dataset, perform a geographic/regional analysis:

USER QUERY: {query}

DATASET:
{context}

Please provide:
1. **Geographic Coverage**: What regions/locations are in the data
2. **Regional Performance**: Metrics by region (table format)
3. **Top Regions**: Best performing geographic areas
4. **Regional Comparison**: How regions differ from each other
5. **Market Penetration**: Distribution across regions
6. **Regional Trends**: Any regional patterns or anomalies
7. **Opportunities**: Underperforming regions with potential

Use actual numbers. Show region-by-region breakdown in tables."""

    system_message = "You are a market analyst expert in geographic analysis. Provide regional breakdowns with actual data, identify geographic patterns, and highlight regional opportunities."

    result = call_ai(prompt, system_message)
    return format_output(result, "Regional Analysis")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(error_output("Usage: python region_analysis.py <query> <file1> [file2] ..."))
        sys.exit(1)

    query = sys.argv[1]
    file_paths = sys.argv[2:]
    print(run_region_analysis(query, file_paths))
