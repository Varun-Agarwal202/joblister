from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(JobListing)
admin.site.register(applicationMentor)
admin.site.register(JobApply)
admin.site.register(MeetingEvent)