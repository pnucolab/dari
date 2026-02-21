from django.contrib import admin

from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

# Register all models from the dariauth app
app_models = apps.get_app_config('dariauth').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass