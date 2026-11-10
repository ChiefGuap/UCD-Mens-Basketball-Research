"""
Configuration file defining target FIBA tournaments, API endpoints,
request headers, and data paths.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"

BASE_URL = "https://www.fiba.basketball"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.fiba.basketball/",
}

RSC_HEADERS = {
    **DEFAULT_HEADERS,
    "RSC": "1",
    "Accept": "*/*",
}

# Tournaments mapping covering the past 3 years (and top youth events)
TOURNAMENTS = [
    {
        "id": "u20_eurobasket_2024_a",
        "name": "FIBA U20 EuroBasket 2024",
        "year": 2024,
        "age_category": "U20",
        "division": "A",
        "tournament_type": "European Championship",
        "teams_url": f"{BASE_URL}/en/events/fiba-u20-eurobasket-2024/teams",
        "team_url_prefix": f"{BASE_URL}/en/events/fiba-u20-eurobasket-2024/teams/",
    },
    {
        "id": "u20_eurobasket_2023_a",
        "name": "FIBA U20 EuroBasket 2023",
        "year": 2023,
        "age_category": "U20",
        "division": "A",
        "tournament_type": "European Championship",
        "teams_url": f"{BASE_URL}/en/history/281-fiba-u20-eurobasket/208566/teams",
        "team_url_prefix": f"{BASE_URL}/en/history/281-fiba-u20-eurobasket/208566/teams/",
    },
    {
        "id": "u20_eurobasket_2022_a",
        "name": "FIBA U20 EuroBasket 2022",
        "year": 2022,
        "age_category": "U20",
        "division": "A",
        "tournament_type": "European Championship",
        "teams_url": f"{BASE_URL}/en/history/281-fiba-u20-eurobasket/208466/teams",
        "team_url_prefix": f"{BASE_URL}/en/history/281-fiba-u20-eurobasket/208466/teams/",
    },
    {
        "id": "u19_world_cup_2023",
        "name": "FIBA U19 Basketball World Cup 2023",
        "year": 2023,
        "age_category": "U19",
        "division": "World",
        "tournament_type": "World Cup",
        "teams_url": f"{BASE_URL}/en/history/276-fiba-u19-basketball-world-cup/208303/teams",
        "team_url_prefix": f"{BASE_URL}/en/history/276-fiba-u19-basketball-world-cup/208303/teams/",
    },
    {
        "id": "u20_eurobasket_2024_b",
        "name": "FIBA U20 EuroBasket 2024 Division B",
        "year": 2024,
        "age_category": "U20",
        "division": "B",
        "tournament_type": "European Championship Division B",
        "teams_url": f"{BASE_URL}/en/events/fiba-u20-eurobasket-2024-division-b/teams",
        "team_url_prefix": f"{BASE_URL}/en/events/fiba-u20-eurobasket-2024-division-b/teams/",
    },
    {
        "id": "u20_eurobasket_2023_b",
        "name": "FIBA U20 EuroBasket 2023 Division B",
        "year": 2023,
        "age_category": "U20",
        "division": "B",
        "tournament_type": "European Championship Division B",
        "teams_url": f"{BASE_URL}/en/history/280-fiba-u20-eurobasket-division-b/208579/teams",
        "team_url_prefix": f"{BASE_URL}/en/history/280-fiba-u20-eurobasket-division-b/208579/teams/",
    },
    {
        "id": "u20_eurobasket_2022_b",
        "name": "FIBA U20 EuroBasket 2022 Division B",
        "year": 2022,
        "age_category": "U20",
        "division": "B",
        "tournament_type": "European Championship Division B",
        "teams_url": f"{BASE_URL}/en/history/280-fiba-u20-eurobasket-division-b/208472/teams",
        "team_url_prefix": f"{BASE_URL}/en/history/280-fiba-u20-eurobasket-division-b/208472/teams/",
    },
    {
        "id": "u19_world_cup_2021",
        "name": "FIBA U19 Basketball World Cup 2021",
        "year": 2021,
        "age_category": "U19",
        "division": "World",
        "tournament_type": "World Cup",
        "teams_url": f"{BASE_URL}/en/history/276-fiba-u19-basketball-world-cup/208299/teams",
        "team_url_prefix": f"{BASE_URL}/en/history/276-fiba-u19-basketball-world-cup/208299/teams/",
    },
]

