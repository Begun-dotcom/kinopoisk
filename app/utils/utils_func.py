def select_func(language : str):
    real_language_for_app = ""
    if language == "Русский":
        real_language_for_app = "ru"
    else:
        real_language_for_app = "en"
    return real_language_for_app