"""
Example script: Fetch Billboard 200 chart (Album Chart)

This script demonstrates how to use mchart to fetch the latest Billboard 200
album chart and verify that the album chart support is working correctly.
"""

import json
from pathlib import Path
import sys

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from mchart import MChart


def main():
    """Fetch and verify Billboard 200 chart"""
    
    print("Initializing MChart client...")
    client = MChart()
    
    print(f"Available providers: {client.providers}")
    print()
    
    # Fetch Billboard 200
    print("Fetching Billboard 200 (Album Chart)...")
    try:
        chart = client.get_chart("billboard", "billboard-200")
        
        print("[OK] Successfully fetched chart!")
        print(f"  Title: {chart['metadata']['title']}")
        print(f"  Type: {chart['metadata']['type']}")
        print(f"  Date: {chart['published_date']}")
        print(f"  Total entries: {len(chart['entries'])}")
        print()
        
        # Verify chart type
        if chart['metadata']['type'] != 'album':
            print(f"[WARNING] Expected chart type 'album', got '{chart['metadata']['type']}'")
        else:
            print("[OK] Chart type correctly set to 'album'")
        print()
        
        # Display top 10
        print("Top 10 Albums:")
        print("-" * 80)
        for i, entry in enumerate(chart['entries'][:10], 1):
            # For album charts, use 'album' field instead of 'song'
            album = entry.get('album') or entry.get('song')  # Fallback for compatibility
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
            
            print(f"{rank:>3}. {album['title']}")  # Album name
            print(f"     {album['artist']}")  # Artist name
            print(f"     [{change:>4}] {weeks} weeks on chart")
            if album.get('image'):
                print(f"     Image: {album['image'][:60]}...")
            print()
        
        # Save to file
        output_dir = Path(__file__).parent.parent / "data"
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "billboard_200.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(chart, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Chart data saved to: {output_file}")
        print(f"  File size: {output_file.stat().st_size:,} bytes")
        
        # Verify backward compatibility - test that single charts still work
        print()
        print("Testing backward compatibility with Hot 100...")
        hot100 = client.get_chart("billboard", "hot-100")
        if hot100['metadata']['type'] == 'single':
            print("[OK] Hot 100 correctly identified as 'single' chart")
        else:
            print(f"[WARNING] Hot 100 type is '{hot100['metadata']['type']}', expected 'single'")
        
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
