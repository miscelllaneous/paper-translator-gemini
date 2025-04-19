import locale

def init(language=None):
    """
    Select the appropriate language module based on user input or system locale.

    Args:
        language (str, optional): Explicitly specified language. Defaults to None.

    Returns:
        module: Selected language module (ja, en, es, fr, de, zh, ko)
    """
    # Mapping of language identifiers
    lang_map = {
        "chinese": "zh",
        "french": "fr",
        "german": "de",
        "japanese": "ja",
        "korean": "ko",
        "spanish": "es",
        "de": "de",
        "es": "es",
        "fr": "fr",
        "ja": "ja",
        "ko": "ko",
        "zh": "zh",
    }

    # Use provided language or get system locale
    system_lang = language if language else locale.getlocale()[0]

    # Normalize language input
    normalized_lang = system_lang.lower()

    # Select language module
    selected_lang = "en"
    for k, v in lang_map.items():
        if normalized_lang.startswith(k):
            selected_lang = v
            break

    # Import the selected language module
    match selected_lang:
        case 'de':
            from . import de as lang_module
        case 'es':
            from . import es as lang_module
        case 'fr':
            from . import fr as lang_module
        case 'ja':
            from . import ja as lang_module
        case 'ko':
            from . import ko as lang_module
        case 'zh':
            from . import zh as lang_module
        case _:
            from . import en as lang_module

    return lang_module
