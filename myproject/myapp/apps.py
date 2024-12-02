from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        import myapp.signals  # Ensures your signals are imported when the app is ready


# class YourAppNameConfig(AppConfig):
#     name = 'your_app_name'  # Make sure this matches the name of your app
#
#     def ready(self):
#         import your_app_name.signals  # Adjust to use actual name of your app and import path
