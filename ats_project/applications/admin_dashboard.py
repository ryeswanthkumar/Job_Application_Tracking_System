from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from .models import ShortlistedCandidate, HoldCandidate, RejectedCandidate

class ATSAdminSite(admin.AdminSite):
    site_header = "ATS Recruitment Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("dashboard/", self.admin_view(self.dashboard_view))
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        context = {
            "shortlisted": ShortlistedCandidate.objects.count(),
            "hold": HoldCandidate.objects.count(),
            "rejected": RejectedCandidate.objects.count(),
        }
        return render(request, "admin/dashboard.html", context)


ats_admin_site = ATSAdminSite(name="ats_admin")
