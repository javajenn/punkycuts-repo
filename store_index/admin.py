from django.contrib import admin
from django.apps import apps

app = apps.get_app_config('store_index')

for model_name, model in app.models.items():
    admin.site.register(model)

# Newsletter Admin Class
class NewsletterAdmin(admin.ModelAdmin):
    SubscriberList = ('Email', 'DateSubscribed')