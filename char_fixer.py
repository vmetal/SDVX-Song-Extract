import re
import json
import os

class CharFixer:
    """
    Handles restoration of characters in SDVX music_db.xml.
    Uses the 'Translation Table' pattern for efficient character-to-character mapping.
    """
    
    _TRANS_TABLE = None
    _MAP_FILE = os.path.join(os.path.dirname(__file__), 'char_map.json')

    # Regex pattern to match characters in the "Broken" range (BEMANI extended SJIS area)
    # This helps in quickly identifying if a string needs processing.
    _TARGET_RANGE = re.compile(r'[\u4900-\u9FFF\u203E\u301C]')

    @classmethod
    def _load_map(cls):
        """Loads the character map from an external JSON file."""
        if cls._TRANS_TABLE is not None:
            return

        if not os.path.exists(cls._MAP_FILE):
            # Fallback to empty translation if file missing
            cls._TRANS_TABLE = str.maketrans({})
            return

        with open(cls._MAP_FILE, 'r', encoding='utf-8') as f:
            char_map = json.load(f)
            # Keys are hex strings (e.g., "49FA")
            cls._TRANS_TABLE = str.maketrans({int(k, 16): v for k, v in char_map.items()})

    @classmethod
    def fix(cls, text: str) -> str:
        """
        Restores broken characters using an optimized translation table.
        This follows the pattern of 'check then transform'.
        """
        if not text:
            return ""
        
        # Optimization: Only apply translation if target characters are likely present
        if cls._TARGET_RANGE.search(text):
            cls._load_map()
            return text.translate(cls._TRANS_TABLE)
        
        return text
