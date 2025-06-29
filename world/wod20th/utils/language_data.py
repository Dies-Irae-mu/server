LANGUAGE_CATEGORIES = {
    "San Diego Common Languages": {
        "english": "English",
        "spanish": "Spanish",
        "tagalog": "Tagalog",
        "vietnamese": "Vietnamese",
        "korean": "Korean",
        "japanese": "Japanese",
        "khmer": "Khmer",
        "hmong": "Hmong",
        "thai": "Thai",
        "lao": "Lao",
        "american sign language": "American Sign Language"
    },
    "African Languages": {
        "amharic": "Amharic",
        "hausa": "Hausa",
        "igbo": "Igbo",
        "lingala": "Lingala",
        "oromo": "Oromo",
        "somali": "Somali",
        "swahili": "Swahili",
        "twi": "Twi",
        "wolof": "Wolof",
        "yoruba": "Yoruba",
        "zulu": "Zulu",
        "afrikaans": "Afrikaans",
        "bambara": "Bambara",
        "bemba": "Bemba",
        "chichewa": "Chichewa",
        "ganda": "Ganda",
        "kikuyu": "Kikuyu",
        "kinyarwanda": "Kinyarwanda",
        "luganda": "Luganda",
        "luo": "Luo",
        "makonde": "Makonde",
        "maltese": "Maltese",
        "mbumba": "Mbumba",
        "ndebele": "Ndebele",
        "nyanja": "Nyanja",
        "shona": "Shona",
        "swati": "Swati",
        "tswana": "Tswana",
        "venda": "Venda",
        "xhosa": "Xhosa"
    },
    "European Languages": {
        "bosnian": "Bosnian",
        "bulgarian": "Bulgarian",
        "croatian": "Croatian",
        "czech": "Czech",
        "danish": "Danish",
        "dutch": "Dutch",
        "finnish": "Finnish",
        "greek": "Greek",
        "french": "French",
        "german": "German",
        "haitian creole": "Haitian Creole",
        "italian": "Italian",
        "hungarian": "Hungarian",
        "norwegian": "Norwegian",
        "polish": "Polish",
        "romanian": "Romanian",
        "serbian": "Serbian",
        "swedish": "Swedish",
        "ukrainian": "Ukrainian",
        "albanian": "Albanian",
        "armenian": "Armenian",  # Keep in European Languages
        "azerbaijani": "Azerbaijani",
        "belarusian": "Belarusian",
        "estonian": "Estonian",
        "icelandic": "Icelandic",
        "irish": "Irish",
        "latvian": "Latvian",
        "lithuanian": "Lithuanian",
        "macedonian": "Macedonian",
        "moldovan": "Moldovan",
        "montenegrin": "Montenegrin",
        "portuguese": "Portuguese",
        "russian": "Russian",
        "slovak": "Slovak",
        "slovenian": "Slovenian"
    },
    "Asian Languages": {
        "burmese": "Burmese",
        "bengali": "Bengali",
        "mandarin": "Mandarin",
        "cantonese": "Cantonese",
        "gujarati": "Gujarati",
        "malay": "Malay",
        "punjabi": "Punjabi",
        "tamil": "Tamil",
        "telugu": "Telugu",
        "hindi": "Hindi",
        "indonesian": "Indonesian"
    },
    "Middle Eastern Languages": {
        "arabic": "Arabic",
        "hebrew": "Hebrew",
        "kurdish": "Kurdish",
        # "armenian": "Armenian",  # Removed duplicate - kept in European Languages
        "syriac": "Syriac",
        "pashto": "Pashto",
        "turkish": "Turkish",
        "urdu": "Urdu",
        "farsi": "Farsi"
    },
    "Indigenous American Languages": {
        "navajo": "Navajo",
        "quechua": "Quechua",
        "inuit": "Inuit",
        "apache": "Apache",
        "cherokee": "Cherokee",
        "chamorro": "Chamorro",
        "chickasaw": "Chickasaw",
        "choctaw": "Choctaw",
        "comanche": "Comanche",
        "cree": "Cree",
        "haida": "Haida",
        "haudenosaunee": "Haudenosaunee",
        "iroquois": "Iroquois",
        "kiowa": "Kiowa",
        "lakota": "Lakota",
        "maya": "Maya",
        "nahuatl": "Nahuatl",
        "pueblo": "Pueblo",
        "tlingit": "Tlingit",
        "turtle": "Turtle",
        "yaqui": "Yaqui",
        "zuni": "Zuni"
    },
    "Pacific Languages": {
        "hawaiian": "Hawaiian",
        "maori": "Maori",
        "samoan": "Samoan",
        "tahitian": "Tahitian",
        "tongan": "Tongan",
        "fijian": "Fijian"
    },
    "Supernatural & Ancient Languages": {
        "animal": "Animal",
        "spirit": "Spirit",
        "enochian": "Enochian",
        "old_english": "Old English",
        "old_norse": "Old Norse",
        "latin": "Latin",
        "ancient_greek": "Ancient Greek",
        "ancient_egyptian": "Ancient Egyptian",
        "akkadian": "Akkadian",
        "sanskrit": "Sanskrit",
        "babylonian": "Babylonian",
        "sumerian": "Sumerian",
        "elamite": "Elamite",
        "hittite": "Hittite",
        "phoenician": "Phoenician",
        "minoan": "Minoan",
        "mycenaean": "Mycenaean"
    }
}

# Create a flat dictionary of all available languages for quick lookup
AVAILABLE_LANGUAGES = {}
for category in LANGUAGE_CATEGORIES.values():
    AVAILABLE_LANGUAGES.update(category)

# Create a case-insensitive lookup dictionary for validation
AVAILABLE_LANGUAGES_LOWER = {key.lower(): value for key, value in AVAILABLE_LANGUAGES.items()}

def is_valid_language(language_name):
    """
    Check if a language name is valid (case-insensitive).
    
    Args:
        language_name (str): The language name to check
        
    Returns:
        tuple: (is_valid, actual_key, display_name) or (False, None, None)
    """
    if not language_name:
        return False, None, None
    
    language_lower = language_name.lower().strip()
    
    # Check exact match first
    if language_lower in AVAILABLE_LANGUAGES_LOWER:
        actual_key = language_lower
        display_name = AVAILABLE_LANGUAGES_LOWER[language_lower]
        return True, actual_key, display_name
    
    # Check for partial matches (for user-friendly input)
    for key, display_name in AVAILABLE_LANGUAGES_LOWER.items():
        if language_lower in key or key in language_lower:
            return True, key, display_name
    
    return False, None, None

def get_language_key(language_name):
    """
    Get the standardized key for a language name.
    
    Args:
        language_name (str): The language name
        
    Returns:
        str: The standardized key or None if not found
    """
    is_valid, key, _ = is_valid_language(language_name)
    return key if is_valid else None

def get_language_display_name(language_name):
    """
    Get the display name for a language.
    
    Args:
        language_name (str): The language name
        
    Returns:
        str: The display name or None if not found
    """
    is_valid, _, display_name = is_valid_language(language_name)
    return display_name if is_valid else None
