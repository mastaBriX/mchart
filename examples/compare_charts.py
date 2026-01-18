"""
Example script: Compare multiple Billboard charts

This script fetches multiple charts and compares them.
"""

import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from mchart import MChart


def main():
    """Compare multiple charts"""
    
    print("Initializing MChart client...")
    client = MChart()
    
    # Charts to compare
    charts_to_fetch = ["hot-100", "billboard-200", "global-200"]
    
    print(f"\nFetching {len(charts_to_fetch)} charts...")
    print("=" * 80)
    
    for chart_name in charts_to_fetch:
        try:
            print(f"\nFetching {chart_name}...")
            chart = client.get_chart("billboard", chart_name)
            
            print(f"  [OK] {chart['metadata']['title']}")
            print(f"    Date: {chart['published_date']}")
            print(f"    Entries: {len(chart['entries'])}")
            
            if chart['entries']:
                top_entry = chart['entries'][0]
                print(f"    #1: {top_entry['song']['title']} - {top_entry['song']['artist']}")
            
        except Exception as e:
            print(f"  [ERROR] Error: {e}")
    
    client.close()
    
    return 0


if __name__ == "__main__":
    exit(main())
