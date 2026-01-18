from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("api/dashboard-counts/", views.dashboard_counts, name="dashboard_counts"),

    path("shortlisted/", views.shortlisted_view, name="shortlisted"),
    path("hold/", views.hold_view, name="hold"),
    path("rejected/", views.rejected_view, name="rejected"),
]
