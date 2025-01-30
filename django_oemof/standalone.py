import django
import environ
from django.conf import settings
from django.core.management import execute_from_command_line


def init_django():
    if settings.configured:
        return

    env = environ.Env()
    env.read_env(".env")

    settings.configure(
        INSTALLED_APPS=[
            'django_oemof',
        ],
        DATABASES={
            'default': env.db("DATABASE_URL")
        },
        MEDIA_ROOT=env.path("MEDIA_ROOT", default="media"),
    )
    django.setup()


if __name__ == "__main__":
    init_django()
    execute_from_command_line()