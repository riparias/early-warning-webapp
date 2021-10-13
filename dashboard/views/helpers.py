import datetime
from typing import Tuple, List

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet

from dashboard.models import Occurrence


def extract_int_array_request(request, param_name):
    """Like extract_array_request, but elements are converted to integers"""
    return list(map(lambda e: int(e), extract_array_request(request, param_name)))


def extract_array_request(request, param_name):
    # Return an array of strings
    # Example:
    #   in: ?speciesIds[]=10&speciesIds[]=12 (params in URL string)
    #   out: ['10', '12']
    # empty params: output is []
    return request.GET.getlist(param_name)


def extract_int_request(request, param_name):
    """Returns an integer, or None if the parameter doesn't exist or is 'null'"""
    val = request.GET.get(param_name, None)
    if val == "" or val == "null" or val is None:
        return None
    else:
        return int(val)


def extract_date_request(request, param_name, date_format="%Y-%m-%d"):
    """Return a datetime.date object (or None is the param doesn't exist or is empty)

    format: see https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    """
    val = request.GET.get(param_name, None)

    if val is not None and val != "" and val != "null":
        return datetime.datetime.strptime(val, date_format).date()

    return None


def filtered_occurrences_from_request(request: WSGIRequest) -> QuerySet[Occurrence]:
    """Takes a request, extract common parameters used to filter occurrences and return a corresponding QuerySet"""
    qs = Occurrence.objects.all()

    species_ids, datasets_ids, start_date, end_date = filters_from_request(request)

    # !! IMPORTANT !! Make sure the occurrence filtering here is equivalent to what's done in
    # views.maps.JINJASQL_FRAGMENT_FILTER_OCCURRENCES. Otherwise, occurrences returned on the map and on other
    # components (table, ...) will be inconsistent.
    # !! If adding new filters, make also sure they are properly documented in the docstrings of "api.py"

    if species_ids:
        qs = qs.filter(species_id__in=species_ids)
    if datasets_ids:
        qs = qs.filter(source_dataset_id__in=datasets_ids)
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)

    return qs


def filters_from_request(
    request: WSGIRequest,
) -> Tuple[List[int], List[int], datetime.date, datetime.date]:
    species_ids = extract_int_array_request(request, "speciesIds[]")
    datasets_ids = extract_int_array_request(request, "datasetsIds[]")
    start_date = extract_date_request(request, "startDate")
    end_date = extract_date_request(request, "endDate")

    return species_ids, datasets_ids, start_date, end_date
