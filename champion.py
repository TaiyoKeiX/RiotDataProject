import requests
import time
from collections import defaultdict
import os

# Load API key

RIOT_API_KEY = "RGAPI-49c7609e-d626-452b-8750-20dfddfb4767"
REGION = "na1"  # Set your region (e.g., "euw1" for Europe)

# API Endpoints
SUMMONER_URL = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{{summoner_name}}"
MATCH_LIST_URL = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{{puuid}}/ids"
MATCH_DETAIL_URL = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{{match_id}}"

def get_summoner_puuid(summoner_name):
    """Get PUUID for a summoner by their name."""
    url = SUMMONER_URL.format(summoner_name=summoner_name)
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    if response.status_code == 200:
        return response.json()["puuid"]
    else:
        print("Failed to retrieve summoner PUUID.")
        return None

def get_recent_matches(puuid, count=20):
    """Retrieve recent match IDs for the given PUUID."""
    url = MATCH_LIST_URL.format(puuid=puuid)
    params = {"start": 0, "count": count}
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve matches.")
        return []

def get_match_details(match_id):
    """Retrieve match details for a specific match ID."""
    url = MATCH_DETAIL_URL.format(match_id=match_id)
    response = requests.get(url, headers={"X-Riot-Token": RIOT_API_KEY})
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve match details.")
        return None

def calculate_all_champions_winrates(sample_size=100):
    """Calculate win rates for each champion across multiple matches."""
    summoner_name = ""  # Replace with a known summoner name
    puuid = get_summoner_puuid(summoner_name)
    if not puuid:
        print("Failed to retrieve PUUID.")
        return

    matches = get_recent_matches(puuid, sample_size)
    champion_stats = defaultdict(lambda: {"wins": 0, "games": 0})

    for match_id in matches:
        match_data = get_match_details(match_id)
        if match_data:
            participants = match_data["info"]["participants"]
            for participant in participants:
                champion_id = participant["championId"]
                win = participant["win"]

                # Update win/loss stats
                champion_stats[champion_id]["games"] += 1
                if win:
                    champion_stats[champion_id]["wins"] += 1

            # Respect API rate limit
            time.sleep(1.2)

    # Calculate win rates
    winrates = {
        champion: stats["wins"] / stats["games"] * 100 for champion, stats in champion_stats.items() if stats["games"] > 0
    }
    return winrates

if __name__ == "__main__":
    winrates = calculate_all_champions_winrates(sample_size=200)  # Adjust for more accuracy
    for champion, winrate in winrates.items():
        print(f"Champion ID: {champion}, Win Rate: {winrate:.2f}%")
