from typing import Optional

from django.conf import settings as django_settings
from django.http import HttpRequest

from dashboard.models import DataImport
from dashboard.utils import human_readable_git_version_number


def latest_data_import_processor(_: HttpRequest):
    try:
        data_import: Optional[DataImport] = DataImport.objects.latest("id")
    except DataImport.DoesNotExist:
        data_import = None
    return {
        "latest_data_import": data_import,
        "git_version_number": human_readable_git_version_number,
    }


def riparias_settings(_: HttpRequest):
    return {
        "riparias_settings": django_settings.RIPARIAS,
    }
