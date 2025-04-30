from django.db import IntegrityError, models
from django.utils import timezone
from django.db import transaction

from django.conf import settings
User = settings.AUTH_USER_MODEL

# Create your models here.

from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


class applicationMentor(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    choices = ( ("Yes", "Yes"),
               ("No", "No"))
    finishhighschool = models.CharField(choices = choices, max_length=20)
    birthdate = models.DateField()
    phone = models.TextField()              
    email = models.TextField()
    address = models.TextField()
    education_level = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.TextField()
    fieldofstudy = models.TextField()
    essay = models.TextField(max_length=1000)
    def __str__(self):
        return (self.first_name + self.last_name)
    def save(self, *args, **kwargs):
        with transaction.atomic():
            try:
                super().save(*args, **kwargs)
            except IntegrityError:
                return False
        return True
class JobListing(models.Model):
    jobtypechoices = ( ("Arts", "Arts"),
                      ("Business", "Business"),
                        ("Communications", "Communications"),
                        ("Education", "Education"),
                        ("Healthcare", "Healthcare"),
                        ("Hospitality", "Hospitality"),
                        ("Information Technology", "Information Technology"),
                        ("Law Enforcement", "Law Enforcement"),
                        ("Sales and Marketing", "Sales and Marketing"),
                        ("Science", "Science"),
                        ("Transportation", "Transportation"),
                        ("Other", "Other"
                        ))
    jobfield = models.CharField(
        choices=jobtypechoices,
        max_length=100,
        null=True,
        blank=True,
        default='other')
    job_title = models.CharField(max_length=100)
    description = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    salary = models.IntegerField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, default='Unknown Company')
    location = models.CharField(max_length=100)
    benefits = models.TextField(max_length=1000)
    job_type = models.CharField(choices = (("Part-Time", "Part-Time"), ("Full-Time", "Full-Time"), ("Other", "Other")), max_length=100)
    job_requirements = models.TextField(max_length=100)
    company_info = models.TextField(max_length=1000)
    notes = models.TextField(max_length=1000)
    status = models.TextField()
    def __str__(self):
        return self.job_title
class CustomUser(AbstractUser):
    choices = ( ("Student", "Student"),
               ("Employer", "Employer"),
               ("Mentor", "Mentor"))
    role = models.CharField(max_length=20, choices = choices)
    first_name = models.TextField()
    last_name = models.TextField()
    choices = ( ("male", "male"),
               ("female", "female"),
               ("prefer not to say", "prefer not to say"))
    
    gender = models.CharField(choices=choices, max_length=20)
    birthday = models.DateField(null=True, blank=True)
    phone = models.TextField()              
    email = models.TextField()
    status_mentor = models.TextField(default="pending")
    mentor = models.ForeignKey(applicationMentor, on_delete=models.CASCADE, null = True, blank=True)
    address = models.TextField()
    offers = models.ManyToManyField(JobListing, related_name='offers', blank=True)
    recieveemails = models.BooleanField(default=False)
    REQUIRED_FIELDS = ["phone","birthday","gender", "email", "address", "first_name", "last_name", "role"]

    
class JobApply(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()
    choices = ( ("male", "male"),
               ("female", "female"),
               ("prefer not to say", "prefer not to say"))
    statuschoices = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    gender = models.CharField(choices=choices, max_length=20)
    birthdate = models.DateField()
    phone = models.TextField()              
    email = models.TextField()
    address = models.TextField()
    education_level = models.TextField()
    creater = models.ForeignKey(User, on_delete=models.CASCADE)
    previousjobs = models.TextField()
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, null = True, blank=True) 
    
    resume = models.FileField(upload_to='resumes/')
    status = models.CharField(
        max_length=10,
        choices=statuschoices,
        default='pending'
    )
    def __str__(self):
        return self.first_name

class MeetingEvent(models.Model):
    mentor = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='hosted_meetings')
    attendees = models.ManyToManyField(get_user_model(), related_name='joined_meetings', blank=True)
    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    limit_people = models.IntegerField(default=30)
    current_people = models.IntegerField(default=0)
    private = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.title} - {self.mentor.username}"