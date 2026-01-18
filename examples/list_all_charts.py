"""
Example script: List all available charts

This script demonstrates how to list all available charts from all providers.
"""

import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from mchart import MChart


def main():
    """List all available charts"""
    
    print("Initializing MChart client...")
    client = MChart()
    
    print(f"Available providers: {client.providers}")
    print()
    
    # List all charts
    all_charts = client.list_all_charts()
    
    for provider, charts in all_charts.items():
        print(f"\n{provider.upper()} Charts")
        print("=" * 80)
        
        if not charts:
            print("  No charts available")
            continue
        
        for chart in charts:
            print(f"\n  - {chart['title']}")
            print(f"    {chart['description']}")
            if chart.get('url'):
                print(f"    URL: {chart['url']}")
    
    client.close()
    
    return 0


if __name__ == "__main__":
    exit(main())
