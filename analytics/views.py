from django.shortcuts import render
from django.http import JsonResponse
from .services import VolatilityService


def dashboard_view(request):
    """
    Renders the main dashboard page.
    """
    return render(request, "analytics/dashboard.html")


# request is the parameter for future extensibility:
# filter by date, toggle currencies, authentication, etc
def api_chart_data(request):
    """
    API endpoint that returns the processed time-series
    and volatility analysis in JSON.
    """
    # Generate the full analysis using the service layer
    analysis = VolatilityService.run_full_analysis()

    # model_dump is chosen cause it's pydantic v2 - specific
    # method to convert the model and its nested objects into
    # a standard dictionary.
    return JsonResponse(analysis.model_dump(mode="json"))
