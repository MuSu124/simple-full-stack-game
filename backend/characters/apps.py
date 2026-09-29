from django.apps import AppConfig


class CharactersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'characters'
    # Keep the original label so existing migration records and the
    # game_character database table continue to work after the package rename.
    label = 'game'
