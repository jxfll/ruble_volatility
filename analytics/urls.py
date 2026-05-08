from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    # The main dashboard interface
    path("", views.dashboard_view, name="dashboard"),
    # The JSON API endpoint for the chart
    path("api/chart-data/", views.api_chart_data, name="chart_api"),
]
