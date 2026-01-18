from django.core.management.base import BaseCommand
import gspread
from google.oauth2.service_account import Credentials
from applications.models import *
from applications.utils.ats_engine import calculate_score

class Command(BaseCommand):
    help = "Sync candidates from Google Sheet"

    def add_arguments(self, parser):
        parser.add_argument("--sheet", type=str, required=True)

    def handle(self, *args, **options):
        sheet_name = options["sheet"]

        credentials = Credentials.from_service_account_file(
            "applications/service-account.json",
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )

        client = gspread.authorize(credentials)
        sheet = client.open(sheet_name).get_worksheet(0)
        rows = sheet.get_all_records()

        rule = ATSRule.objects.filter(job_title=sheet_name).first()
        if not rule:
            self.stdout.write("❌ ATSRule not found")
            return

        for row in rows:
            email = row.get("Email") or row.get("email")
            if not email:
                continue

            candidate = ShortlistedCandidate.objects.create(
                first_name=row.get("First Name", ""),
                last_name=row.get("Last Name", ""),
                email=email,
                phone=row.get("Phone", ""),
                experience=float(row.get("Experience", 0)),
                skills=row.get("Skills", ""),
                location=row.get("Location", ""),
                resume_link=row.get("Resume", ""),
            )

            score = calculate_score(candidate, rule)
            candidate.score = score
            candidate.save()

            if score < rule.hold_score:
                RejectedCandidate.objects.create(**candidate.__dict__)
                candidate.delete()
            elif score < rule.shortlist_score:
                HoldCandidate.objects.create(**candidate.__dict__)
                candidate.delete()

        self.stdout.write("✅ Sync completed")
