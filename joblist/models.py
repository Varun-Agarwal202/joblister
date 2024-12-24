from django.db import IntegrityError, models
from django.utils import timezone
from django.db import transaction

from django.conf import settings
User = settings.AUTH_USER_MODEL

# Create your models here.

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    choices = ( ("Student", "Student"),
               ("Employer", "Employer"),
               ("Mentor", "Mentor"))
    role = models.CharField(max_length=20, choices = choices)
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
    def __str__(self):
        return self.job_title
    
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
    qualifications = models.TextField()
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, null = True, blank=True) 
    status = models.CharField(
        max_length=10,
        choices=statuschoices,
        default='pending'
    )
    def __str__(self):
        return self.qualifications