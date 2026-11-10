"""
Scraper module for FIBA events and teams.
Retrieves team listings and team RSC (React Server Component) payloads.
"""

import time
import random
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests

from .config import DEFAULT_HEADERS, RSC_HEADERS, RAW_DATA_DIR


class FIBAScraper:
    def __init__(self, cache_dir: Optional[Path] = None, request_delay: float = 0.8):
        self.cache_dir = cache_dir or RAW_DATA_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.delay = request_delay
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _sleep_jitter(self):
        """Polite jittered delay to prevent server overload or rate limiting."""
        time.sleep(self.delay + random.uniform(0.1, 0.4))

    def get_team_slugs(self, tournament: Dict[str, Any]) -> List[str]:
        """
        Discovers all competing national team slugs for a given tournament.
        """
        teams_url = tournament["teams_url"]
        tournament_id = tournament["id"]
        cache_file = self.cache_dir / tournament_id / "_teams_page.html"
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        if cache_file.exists():
            html = cache_file.read_text(encoding="utf-8")
        else:
            print(f"[{tournament['name']}] Fetching teams page: {teams_url}")
            resp = self.session.get(teams_url, timeout=20)
            resp.raise_for_status()
            html = resp.text
            cache_file.write_text(html, encoding="utf-8")
            self._sleep_jitter()

        # Match team links: e.g. /teams/france, /teams/belgium, etc.
        # Format might be /en/events/.../teams/<slug> or /en/history/.../teams/<slug>
        pattern = r'/teams/([a-zA-Z0-9_\-]+)'
        found = re.findall(pattern, html)

        # Filter out static tabs, files, and build chunks
        excluded = {"roster", "games", "statistics", "videos", "news", "photos", "leaders", "standings"}
        slugs = []
        for s in found:
            s_clean = s.strip().lower()
            if s_clean.startswith("page-") or "." in s_clean or s_clean in excluded:
                continue
            if s_clean not in slugs:
                slugs.append(s_clean)

        print(f"[{tournament['name']}] Found {len(slugs)} teams: {', '.join(slugs)}")
        return slugs

    def get_team_rsc_payload(self, tournament: Dict[str, Any], team_slug: str) -> str:
        """
        Fetches the RSC payload for a specific national team in a tournament.
        Uses local cache if already downloaded.
        """
        tournament_id = tournament["id"]
        cache_file = self.cache_dir / tournament_id / f"{team_slug}.rsc"
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        if cache_file.exists():
            return cache_file.read_text(encoding="utf-8")

        team_url = f"{tournament['team_url_prefix']}{team_slug}"
        print(f"  -> Fetching RSC data for {team_slug.upper()} ({team_url})...")
        resp = self.session.get(team_url, headers=RSC_HEADERS, timeout=20)
        resp.raise_for_status()

        content = resp.text
        cache_file.write_text(content, encoding="utf-8")
        self._sleep_jitter()
        return content
