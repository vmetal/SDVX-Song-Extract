import re

class CharFixer:
    """
    Handles restoration of characters in SDVX music_db.xml.
    Uses the 'Translation Table' pattern for efficient character-to-character mapping.
    """
    
    # Mapping Table: { original_codepoint: target_symbol }
    # These are specific to BEMANI/SDVX custom Shift-JIS font mappings.
    _MAP = {
        ord('\u203E'): '~',
        ord('\u301C'): '～',
        # Symbols (Commonly found in 0x9Fxx range)
        ord('\u9F72'): '♥',
        ord('\u9F76'): '♡',
        ord('\u9448'): '♦',
        ord('\u973B'): '♠',
        ord('\u9F6A'): '♣',
        ord('\u9EFB'): '*',
        ord('\u76E5'): '⚙',
        ord('\u8E94'): '🐾',
        ord('\u91C1'): '🍄',
        ord('\u9452'): '₩',
        ord('\u9477'): 'ゔ',
        # Accented / European Characters
        ord('\u9F63'): 'Ú',
        ord('\u9F67'): 'Ä',
        ord('\u9F77'): 'é',
        ord('\u983D'): 'ä',
        ord('\u9AAD'): 'ü',
        ord('\u96CD'): 'Ü',
        ord('\u9A2B'): 'á',
        ord('\u9A69'): 'Ø',
        ord('\u9A6A'): 'ō',
        ord('\u9A6B'): 'ā',
        ord('\u9B2F'): 'ī',
        ord('\u9EF7'): 'ē',
        ord('\u745F'): 'ō',
        ord('\u5F5C'): 'ū',
        ord('\u66E6'): 'à',
        ord('\u66E9'): 'è',
        ord('\u7011'): 'À',
        ord('\u7162'): 'ø',
        ord('\u7589'): 'Ö',
        ord('\u9B25'): 'Ã',
        ord('\u9B2E'): '¡',
        ord('\u9F95'): '€',
        ord('\u95C3'): 'Ā',
        ord('\u96CB'): 'Ǜ',
        ord('\u9B06'): 'Ý',
        ord('\u9B32'): 'Ý',
        ord('\u49FA'): 'ê',
        ord('\u58EC'): 'ê',
        ord('\u00D7'): '×',
    }

    # Create the translation table once
    _TRANS_TABLE = str.maketrans(_MAP)

    # Regex pattern to match characters in the "Broken" range (BEMANI extended SJIS area)
    # This helps in quickly identifying if a string needs processing.
    _TARGET_RANGE = re.compile(r'[\u4900-\u9FFF\u203E\u301C]')

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
            return text.translate(cls._TRANS_TABLE)
        
        return text
