from django.db import models


class Candidate(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    experience = models.FloatField(default=0)
    skills = models.TextField()
    location = models.CharField(max_length=100)
    resume_link = models.TextField(blank=True)
    score = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True


class ShortlistedCandidate(Candidate):
    interview_date = models.DateTimeField(null=True, blank=True)
    is_selected = models.BooleanField(default=False)


class HoldCandidate(Candidate):
    remarks = models.TextField(blank=True)


class RejectedCandidate(Candidate):
    rejection_reason = models.TextField(blank=True)


class ATSRule(models.Model):
    job_title = models.CharField(max_length=255, unique=True)
    min_experience = models.FloatField()
    required_skills = models.TextField()
    shortlist_score = models.IntegerField(default=70)
    hold_score = models.IntegerField(default=50)

    def __str__(self):
        return self.job_title
