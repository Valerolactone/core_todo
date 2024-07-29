import importlib
import os


class LazySettings:
    def __init__(self):
        self._settings = None

    def _load_settings(self):
        if self._settings is None:
            env = os.getenv('DJANGO_ENV', 'dev')
            settings_module = f'settings.{env}'

            settings = importlib.import_module(settings_module)

            self._settings = {
                k: v for k, v in vars(settings).items() if not k.startswith('_')
            }

    def __getattr__(self, item):
        self._load_settings()
        return self._settings.get(item)


lazy_settings = LazySettings()
