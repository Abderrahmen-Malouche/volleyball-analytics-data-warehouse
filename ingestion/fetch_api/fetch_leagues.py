import requests
from dotenv import load_dotenv
import os
from pathlib import Path
import pandas as pd


dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)
volley_ball_api_key = os.getenv("VolleyballAPIKey")
print(volley_ball_api_key)
headers = {"x-apisports-key": volley_ball_api_key}
target_season = 2023  # set the season you want

url_leagues = "https://v1.volleyball.api-sports.io/leagues"
response = requests.get(url_leagues, headers=headers)
leagues = response.json().get("response", [])

all_leagues = []
all_games = []
all_teams=[]
fetched_team_ids = set()
for league in leagues:
    if league.get("type") != "Cup":
        continue  
    
    league_id = league.get("id")
    league_name = league.get("name")
    country_info = league.get("country", {})

    
    all_leagues.append({
        "League ID": league_id,
        "Name": league_name,
        "Type": league.get("type"),
        "Logo": league.get("logo"),
        "Country ID": country_info.get("id", ""),
        "Country Name": country_info.get("name", ""),
        "Country Code": country_info.get("code", "")
    })

    
    url_games = f"https://v1.volleyball.api-sports.io/games?league={league_id}&season={target_season}"
    response = requests.get(url_games, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch games for league {league_name} ({league_id})")
        continue

    games = response.json().get("response", [])

    
    for game in games:
        all_games.append({
            "Game ID": game.get("id"),
            "Date": game.get("date", ""),
            "Status": game.get("status", {}).get("long", ""),
            "League ID": game.get("league", {}).get("id", ""),
            "League Name": league_name,
            "Home Team": game.get("teams", {}).get("home", {}).get("name", ""),
            "Away Team": game.get("teams", {}).get("away", {}).get("name", ""),
            "Home Score": game.get("scores", {}).get("home", ""),
            "Away Score": game.get("scores", {}).get("away", ""),
            "Periods": game.get("periods", [])
        })
        teams_id=[game.get("teams", {}).get("home", {}).get("id", ""),game.get("teams", {}).get("away", {}).get("id", "")]
        for id in teams_id:
          if not id or id in fetched_team_ids:
            continue  # Skip if invalid or already fetched
          url_team = f"https://v1.volleyball.api-sports.io/teams?league={league_id}&season={target_season}&id={id}"
          response = requests.get(url_team, headers=headers)
          if response.status_code != 200:
            print(f"Failed to fetch team {id} info")
            continue

          team_data = response.json().get("response", [])
          if not team_data:
            continue


          all_teams.append({
            "Team ID": team_data.get("id", ""),
            "Team Name": team_data.get("name", ""),
            "National": team_data.get("national", False),  # boolean
            "Country": team_data.get("country", {}).get("name", "") if team_data.get("national") else "",
            "League ID": league_id  # optional, for joining later
          })

          fetched_team_ids.add(id)  # Mark as fetched
 
         

    print(f"Fetched {len(games)} games for league {league_name} ({league_id})")

pd.DataFrame(all_leagues).to_csv("../raw/volleyball_cup_leagues.csv", index=False)
pd.DataFrame(all_games).to_csv(f"../raw/volleyball_cup_games_{target_season}.csv", index=False)
pd.DataFrame(all_teams).to_csv(f"../raw/volleyball_cup_teams_{target_season}.csv", index=False)
print(f"Saved {len(all_teams)} teams for season {target_season}!")
print(f"Saved {len(all_leagues)} Cup leagues and {len(all_games)} games for season {target_season}!")
