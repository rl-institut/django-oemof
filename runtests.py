"""Module to run django tests for standalone app"""

import sys

import django
import environ
from django.conf import settings
from django.core.management import call_command

env = environ.Env()

DATABASES = {"default": env.db("DATABASE_URL")}


def runtests():
    """Sets up django settings an runs tests"""

    if not settings.configured:
        # Configure test environment
        settings.configure(
            DATABASES=DATABASES,
            INSTALLED_APPS=(
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "django.contrib.sites",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django.contrib.admin.apps.SimpleAdminConfig",
                "django.contrib.staticfiles",
                "rest_framework",
                "django_oemof",
            ),
            ROOT_URLCONF="",  # tests override urlconf, but it still needs to be defined
            MIDDLEWARE=(
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.middleware.common.CommonMiddleware",
                "django.middleware.csrf.CsrfViewMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
            ),
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                    },
                },
            ],
        )

    if django.VERSION >= (1, 7):
        django.setup()
    failures = call_command("test", "django_oemof.tests", interactive=False, failfast=False, verbosity=2)

    sys.exit(bool(failures))


if __name__ == "__main__":
    runtests()
