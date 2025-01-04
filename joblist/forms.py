from django import forms
from allauth.account.forms import SignupForm
from .models import JobListing, JobApply, applicationMentor

class CustomSignupForm(SignupForm):
    choices = ( ("Student", "Student"),
               ("Employer", "Employer"))
    role = forms.ChoiceField(choices = choices, label = "Role")
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.role = self.cleaned_data['role']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user
location = forms.CharField(required = True)
company_name = forms.CharField(required=True)
job_title = forms.CharField(required = True)
description = forms.CharField(required = True)
salary = forms.IntegerField(required = True)
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
jobfield = forms.ChoiceField(choices = jobtypechoices, label = "Job Field")
class JobForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = ('company_name', 'job_title','description','salary', "jobfield", "location" )
class mentorApply(forms.ModelForm):
    choices = ( 
        ("Yes", "Yes"),
        ("No", "No")
    )
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    finishhighschool = forms.ChoiceField(choices = choices, label = "Did you finish High School?")
    birthdate = forms.DateField(label = "Date Of Birth")
    phone = forms.CharField(max_length=30, label='Phone Number')
    email = forms.CharField(max_length=30, label='Email')
    address = forms.CharField(max_length=30, label='Address')
    education_level = forms.CharField(max_length=30, label='Education Level')
    class Meta:
        model = applicationMentor
        fields = ('first_name', 'last_name', 'finishhighschool', 'birthdate', 'phone', 'email', 'address', 'education_level', )
class Application(forms.ModelForm):
    choices = ( ("male", "male"),
               ("female", "female"),
               ("prefer not to say", "prefer not to say"))
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    gender = forms.ChoiceField(choices = choices, label = "Gender")
    birthdate = forms.DateField(label = "Date Of Birth")
    phone = forms.CharField(max_length=30, label='Phone Number')
    email = forms.CharField(max_length=30, label='Email')
    address = forms.CharField(max_length=30, label='Address')
    education_level = forms.CharField(max_length=30, label='Education Level')
    qualifications = forms.CharField(max_length=30, label='Qualifications')
    class Meta:
        model = JobApply
        fields = ('first_name', 'last_name', 'gender', 'birthdate', 'phone', 'email', 'address', 'education_level', 'qualifications', )
