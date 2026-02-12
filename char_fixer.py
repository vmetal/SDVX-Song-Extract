class CharFixer:
    # Character restoration map for SDVX-specific Shift-JIS encoding issues.
    # These map incorrectly decoded characters (due to custom Konami fonts or non-standard Shift-JIS)
    # back to their intended symbols or accented characters.
    REPLACEMENT_MAP = {
        '\u203E': '~',      # Overline -> Tilde
        '\u301C': '～',     # Wave Dash
        # Symbols
        '\u9F72': '♥',      # Heart
        '\u9F76': '♡',      # White Heart
        '\u9448': '♦',      # Diamond
        '\u973B': '♠',      # Spade
        '\u9F6A': '♣',      # Club
        '\u9EFB': '*',      
        '\u76E5': '⚙',      
        '\u8E94': '🐾',     
        '\u91C1': '🍄',     
        '\u9452': '₩',
        '\u9477': 'ゔ',
        # Accented / European Characters
        '\u9F63': 'Ú',      
        '\u9F67': 'Ä',      
        '\u9F77': 'é',      
        '\u983D': 'ä',      
        '\u9AAD': 'ü',      
        '\u96CD': 'Ü',      
        '\u9A2B': 'á',      
        '\u9A69': 'Ø',      
        '\u9A6A': 'ō',      
        '\u9A6B': 'ā',      
        '\u9B2F': 'ī',      
        '\u9EF7': 'ē',      
        '\u745F': 'ō',      
        '\u5F5C': 'ū',      
        '\u66E6': 'à',      
        '\u66E9': 'è',      
        '\u7011': 'À',      
        '\u7162': 'ø',      
        '\u7589': 'Ö',      
        '\u9B25': 'Ã',      
        '\u9B2E': '¡',      
        '\u9F95': '€',      
        '\u95C3': 'Ā',
        '\u96CB': 'Ǜ',
        '\u9B06': 'Ý',
        '\u9B32': 'Ý',
        '\u49FA': 'ê',
        '\u58EC': 'ê',
        '\u00D7': '×',
    }

    @classmethod
    def fix(cls, text: str) -> str:
        """Replace broken characters using the predefined mapping."""
        if not text:
            return ""
        for old, new in cls.REPLACEMENT_MAP.items():
            text = text.replace(old, new)
        return text
