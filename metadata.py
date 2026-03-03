import logging
from pathlib import Path
from typing import Dict
from bs4 import BeautifulSoup
from config import SDVXConfig
from char_fixer import CharFixer

logger = logging.getLogger(__name__)

class MetadataManager:
    """Manages parsing and storing song metadata from music_db.xml."""
    def __init__(self, game_folder: str):
        self.game_folder = Path(game_folder)
        self.metadata: Dict[int, dict] = {}

    def load(self):
        """Parse music_db.xml and store entries in a dictionary."""
        db_path = self.game_folder / SDVXConfig.RELATIVE_MUSIC_DB
        if not db_path.exists():
            raise FileNotFoundError(f"music_db.xml not found at {db_path}")

        # Use cp932 (Shift-JIS variation) for reading Konami XML files
        with open(db_path, "r", encoding="cp932", errors="ignore") as f:
            # lxml is recommended for better performance and XML support
            soup = BeautifulSoup(f.read(), features="xml")

        for music in soup.find_all("music"):
            try:
                m_id = int(music["id"])
                info = music.find("info")
                if not info: continue
                
                self.metadata[m_id] = {
                    "title": CharFixer.fix(info.find("title_name").text),
                    "artist": CharFixer.fix(info.find("artist_name").text),
                    "genre": info.find("genre").text if info.find("genre") else "",
                    "version": int(info.find("version").text) if info.find("version") else 1,
                    "release_year": info.find("distribution_date").text[:4] if info.find("distribution_date") else "2012",
                    "bpm_max": int(info.find("bpm_max").text) / 100 if info.find("bpm_max") else 0,
                    "bpm_min": int(info.find("bpm_min").text) / 100 if info.find("bpm_min") else 0,
                    "track": m_id,
                }
            except Exception as e:
                logger.warning(f"Failed to parse music entry: {e}")

        # Add special entries that might not be in the music_db
        self.metadata[9001] = {
            "title": "SOUND VOLTEX Tutorial",
            "artist": "SOUND VOLTEX Team",
            "genre": "Tutorial",
            "version": 6,
            "release_year": "2020",
            "bpm_max": 110.0,
            "bpm_min": 110.0,
        }
