import platform
from pathlib import Path

class SDVXConfig:
    RELATIVE_SONG_FOLDER = "data/music"
    RELATIVE_MUSIC_DB = "data/others/music_db.xml"
    OUTPUT_DIR = Path("SDVX Music")
    
    VERSIONS = {
        1: "SOUND VOLTEX BOOTH",
        2: "SOUND VOLTEX ii Infinite Infection",
        3: "SOUND VOLTEX III GRAVITY WARS",
        4: "SOUND VOLTEX IV HEAVENLY HAVEN",
        5: "SOUND VOLTEX V Vivid Wave",
        6: "SOUND VOLTEX EXCEED GEAR",
        7: "SOUND VOLTEX NABLA"
    }

    AUDIO_FORMATS = {
        "mp3": "MP3 V0",
        "wav": "WAV 1411kbps",
        "asf": "ASF VBR"
    }

    RANK_MAP = {1: "NOV", 2: "ADV", 3: "EXH"}
    RANK_SUFFIX = ["1n", "2a", "3e", "4i", "4g", "4h", "5m"]

    @staticmethod
    def get_ffmpeg_path() -> str:
        if platform.system() == "Windows":
            return "ffmpeg.exe"
        # Default path for macOS/Linux (e.g., Homebrew install)
        return "/opt/homebrew/bin/ffmpeg"

    @staticmethod
    def get_2dx_extract_path() -> str:
        if platform.system() == "Windows":
            return str(Path("2dx_extract/bin/2dx_extract.exe"))
        # Assumes the binary is compiled and available in the folder
        return "./2dx_extract/2dx_extract"
