"""
Example script: Search for an artist in charts

This script demonstrates how to search for a specific artist in the charts.
"""

import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from mchart import MChart


def main():
    """Search for an artist in the Hot 100"""
    
    # Get artist name from command line or use default
    artist_name = sys.argv[1] if len(sys.argv) > 1 else "Taylor Swift"
    
    print(f"Searching for '{artist_name}' in Billboard Hot 100...")
    print("=" * 80)
    
    client = MChart()
    
    try:
        # Fetch chart as model for easier searching
        chart = client.get_chart("billboard", "hot-100", return_type="model")
        
        # Search for artist
        results = chart.find_by_artist(artist_name)
        
        if not results:
            print(f"\nNo songs found for '{artist_name}' on the chart.")
        else:
            print(f"\nFound {len(results)} song(s) by '{artist_name}':")
            print()
            
            for entry in results:
                print(f"  #{entry.rank} - {entry.song.title}")
                print(f"       by {entry.song.artist}")
                print(f"       {entry.weeks_on_chart} weeks on chart")
                if entry.last_week > 0:
                    change = entry.last_week - entry.rank
                    if change > 0:
                        print(f"       [+] Up {change} from last week")
                    elif change < 0:
                        print(f"       [-] Down {abs(change)} from last week")
                    else:
                        print(f"       [=] Same as last week")
                else:
                    print(f"       NEW entry!")
                print()
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        client.close()
    
    return 0


if __name__ == "__main__":
    exit(main())
