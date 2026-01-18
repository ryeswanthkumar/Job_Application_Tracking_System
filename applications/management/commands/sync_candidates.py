from django.core.management.base import BaseCommand
from applications.models import (
    ShortlistedCandidate,
    HoldCandidate,
    RejectedCandidate,
    ATSRule,
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from django.conf import settings


class Command(BaseCommand):
    help = "Sync candidates from Google Sheet"

    def add_arguments(self, parser):
        parser.add_argument("--sheet", type=str, required=True)

    def handle(self, *args, **options):
        sheet_name = options["sheet"]

        # Google API scope (DEFAULT – correct)
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        # credentials.json must be in project root
        creds_path = os.path.join(settings.BASE_DIR, "credentials.json")
        if not os.path.exists(creds_path):
            self.stderr.write("❌ credentials.json not found")
            return

        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)

        spreadsheet = client.open(sheet_name)
        worksheet = spreadsheet.sheet1
        rows = worksheet.get_all_records()

        self.stdout.write(f"Rows found: {len(rows)}")

        try:
            rule = ATSRule.objects.get(job_title=sheet_name)
        except ATSRule.DoesNotExist:
            self.stderr.write("❌ ATSRule not found")
            return

        created = 0

        for row in rows:
            print("ROW:", row)

            # --------- FORM DATA (EXACT HEADERS) ----------
            first_name = str(row.get("First Name", "")).strip()
            last_name = str(row.get("Last Name", "")).strip()
            email = str(row.get("Email Id", "")).strip()
            phone = str(row.get("Phone Number", "")).strip()
            skills = str(row.get("Skills", "")).strip()
            resume_link = str(row.get("Upload Updated Resume (PDF/DOCX)", "")).strip()

            experience_raw = row.get(
                "Total Years of Experience (Fresher Mention 0)", 0
            )
            try:
                experience = float(experience_raw)
            except (ValueError, TypeError):
                experience = 0

            if not email:
                continue

            # --------- DUPLICATE CHECK ----------
            if (
                ShortlistedCandidate.objects.filter(email=email).exists()
                or HoldCandidate.objects.filter(email=email).exists()
                or RejectedCandidate.objects.filter(email=email).exists()
            ):
                continue

            # --------- ATS SCORING ----------
            score = 0

            # Experience score
            if experience >= rule.min_experience:
                score += 40

            # Skill score (FIXED LOGIC)
            candidate_skills = skills.lower()

            for skill in rule.required_skills.lower().split(","):
                skill = skill.strip()

                if skill == "sql" and "mysql" in candidate_skills:
                    score += 20
                elif skill in candidate_skills:
                    score += 20

            # --------- CLASSIFICATION ----------
            if score >= rule.shortlist_score:
                ShortlistedCandidate.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    experience=experience,
                    skills=skills,
                    location="",
                    resume_link=resume_link,
                    score=score,
                )

            elif score >= rule.hold_score:
                HoldCandidate.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    experience=experience,
                    skills=skills,
                    location="",
                    resume_link=resume_link,
                    score=score,
                )

            else:
                RejectedCandidate.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    experience=experience,
                    skills=skills,
                    location="",
                    resume_link=resume_link,
                    score=score,
                    rejection_reason="Low ATS score",
                )

            created += 1

        self.stdout.write(f"✅ Sync completed. Created {created} candidates")
