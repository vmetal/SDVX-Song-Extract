import logging
from pathlib import Path
from config import SDVXConfig
from metadata import MetadataManager
from extractor import SongExtractor

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    print("=== SDVX Song Extractor (Refactored) ===")
    
    # Input path validation
    game_path_str = input("Insert path to SDVX folder > ").strip()
    game_path = Path(game_path_str)
    if not (game_path / "modules" / "soundvoltex.dll").exists():
        print("Error: soundvoltex.dll not found. The path might be incorrect.")
        return

    # Select output format
    print("\nChoose your format:")
    for k, v in SDVXConfig.AUDIO_FORMATS.items():
        print(f" {k}: {v}")
    
    fmt = input("> ").lower()
    if fmt not in SDVXConfig.AUDIO_FORMATS:
        print("Invalid format.")
        return

    try:
        # 1. Load song metadata from music_db.xml
        print("Loading metadata...")
        meta_manager = MetadataManager(str(game_path))
        meta_manager.load()

        # 2. Run extraction and conversion
        print(f"Starting extraction ({fmt})...")
        extractor = SongExtractor(str(game_path), fmt, meta_manager.metadata)
        extractor.run()

        print("\nAll tasks completed!")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")

if __name__ == "__main__":
    main()
