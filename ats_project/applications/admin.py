from django.contrib import admin
from .models import *


admin.site.register(ShortlistedCandidate)
admin.site.register(HoldCandidate)
admin.site.register(RejectedCandidate)
admin.site.register(ATSRule)
