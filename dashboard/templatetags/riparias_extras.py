import json

from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.templatetags.static import static

register = template.Library()


@register.simple_tag(takes_context=True)
def js_config_object(context):
    # When adding stuff here, don't forget to update the corresponding TypeScript interface in assets/ts/interfaces.ts
    conf = {
        "currentLanguageCode": context.request.LANGUAGE_CODE,  # for the example (not used yet, delete later?)
        "targetCountryCode": settings.RIPARIAS[
            "TARGET_COUNTRY_CODE"
        ],  # for the example (not used yet, delete later?)
        "ripariasAreaGeojsonUrl": static("geojson/Riparias_Official_StudyArea.geojson"),
        "apiEndpoints": {
            "speciesListUrl": reverse("dashboard:api-species-list-json"),
            "datasetsListUrl": reverse("dashboard:api-datasets-list-json"),
            "occurrencesCounterUrl": reverse(
                "dashboard:api-filtered-occurrences-counter"
            ),
            "occurrencesJsonUrl": reverse(
                "dashboard:api-filtered-occurrences-data-page"
            ),
            "tileServerUrlTemplate": reverse(
                "dashboard:api-mvt-tiles-hexagon-grid-aggregated",
                kwargs={"zoom": 1, "x": 2, "y": 3},
            )
            .replace("1", "{z}")
            .replace("2", "{x}")
            .replace("3", "{y}"),
            "occurrenceDetailsUrlTemplate": reverse(
                "dashboard:page-occurrence-details", kwargs={"pk": 1}
            ).replace("1", "{pk}"),
            "minMaxOccPerHexagonUrl": reverse("dashboard:api-mvt-min-max-per-hexagon"),
            "occurrencesHistogramDataUrl": reverse(
                "dashboard:api-filtered-occurrences-monthly-histogram"
            ),
        },
    }
    return mark_safe(json.dumps(conf))


@register.filter
def gbif_download_url(value):
    return f"https://www.gbif.org/occurrence/download/{value}"


@register.filter
def gbif_occurrence_url(value):
    return f"https://www.gbif.org/occurrence/{value}"
