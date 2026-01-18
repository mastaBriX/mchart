"""
Example script: Fetch Billboard Hot 100 chart

This script demonstrates how to use mchart to fetch the latest Billboard Hot 100
chart and save it to a JSON file.
"""

import json
from pathlib import Path
import sys

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from mchart import MChart


def main():
    """Fetch and save Billboard Hot 100 chart"""
    
    print("Initializing MChart client...")
    client = MChart()
    
    print(f"Available providers: {client.providers}")
    print()
    
    # Fetch Billboard Hot 100
    print("Fetching Billboard Hot 100...")
    try:
        chart = client.get_chart("billboard", "hot-100")
        
        print("[OK] Successfully fetched chart!")
        print(f"  Title: {chart['metadata']['title']}")
        print(f"  Date: {chart['published_date']}")
        print(f"  Total entries: {len(chart['entries'])}")
        print()
        
        # Display top 10
        print("Top 10:")
        print("-" * 80)
        for i, entry in enumerate(chart['entries'][:10], 1):
            song = entry['song']
            rank = entry['rank']
            last_week = entry['last_week']
            weeks = entry['weeks_on_chart']
            
            # Calculate change
            if last_week == 0:
                change = "NEW"
            else:
                diff = last_week - rank
                if diff > 0:
                    change = f"+{diff}"
                elif diff < 0:
                    change = f"-{abs(diff)}"
                else:
                    change = "="
            
            print(f"{rank:>3}. {song['title']}")
            print(f"     {song['artist']}")
            print(f"     [{change:>4}] {weeks} weeks on chart")
            print()
        
        # Save to file
        output_dir = Path(__file__).parent.parent / "data"
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "billboard_hot100.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(chart, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Chart data saved to: {output_file}")
        print(f"  File size: {output_file.stat().st_size:,} bytes")
        
    except Exception as e:
        print(f"[ERROR] Error fetching chart: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        client.close()
    
    return 0


if __name__ == "__main__":
    exit(main())
