from django import forms
from allauth.account.forms import SignupForm
from .models import JobListing, JobApply, applicationMentor

class CustomSignupForm(SignupForm):
    choices = ( ("Student", "Student"),
               ("Employer", "Employer"),
               ("Mentor", "Mentor"))
    role = forms.ChoiceField(choices = choices, label = "Role", required=True)
    first_name = forms.CharField(max_length=30, label='First Name', required=True)
    last_name = forms.CharField(max_length=30, label='Last Name', required=True)
    choices = ( ("male", "male"),
               ("female", "female"),
               ("prefer not to say", "prefer not to say"))
    gender = forms.ChoiceField(choices = choices, label = "Gender")
    birthday = forms.DateField(widget=forms.TextInput(attrs={'class': 'form-control', 'type':'date'}))
    phone = forms.CharField(max_length=30, label='Phone Number')
    address = forms.CharField()
    recieveemails = forms.BooleanField(label='Recieve emails?', required=False,  widget=forms.CheckboxInput(attrs = {'class': 'form-check-input'}))
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.CharField(required=True)
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.role = self.cleaned_data['role']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.gender = self.cleaned_data['gender']
        user.birthday = self.cleaned_data['birthday']
        user.phone = self.cleaned_data['phone']
        user.address = self.cleaned_data['address']
        user.recieveemails = self.cleaned_data['recieveemails']
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
benefits = forms.CharField(required = False, label = "Benefits")
job_type = forms.ChoiceField(choices = (("Part-Time", "Part-Time"), ("Full-Time", "Full-Time"), ("Other", "Other")),
                              required = True, label = "Job Type")
job_requirements = forms.CharField(required = True, label = "Job Requirements")
company_info = forms.CharField(required = False, label = "Company Information (Optional)")
notes = forms.CharField(required = False, label = "Job Additional Notes (Optional)")
class JobForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = ('company_name', 'job_title','description','salary', "jobfield", "location" , "benefits", "job_type", "job_requirements", "company_info", "notes")
class mentorApply(forms.ModelForm):
    choices = ( 
        ("Yes", "Yes"),
        ("No", "No")
    )
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
                        ("Other", "Other"))
    fieldofstudy = forms.ChoiceField(choices = jobtypechoices, label = "Job Field")
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    finishhighschool = forms.ChoiceField(choices = choices, label = "Did you finish High School?")
    birthdate = forms.DateField(label = "Date Of Birth")
    phone = forms.CharField(max_length=30, label='Phone Number')
    email = forms.CharField(max_length=30, label='Email')
    address = forms.CharField(max_length=30, label='Address')
    education_level = forms.CharField(max_length=30, label='Education Level')
    essay = forms.CharField(widget=forms.Textarea(attrs={'rows': 8, 'cols': 40, 'class': 'write'}), label='Please Write a Short Paragraph on Why You Want to be a Mentor')
    class Meta:
        model = applicationMentor
        fields = ('first_name', 'last_name', 'finishhighschool', 'birthdate', 'phone', 'email', 'address', 'education_level', 'fieldofstudy', 'essay' )
class Application(forms.ModelForm):
    
    education_level = forms.CharField(max_length=30, label='Education Level')
    previousjobs = forms.CharField(max_length=30, label='Previous Jobs Worked')
    resume = forms.FileField(label = "Resume")
    class Meta:
        model = JobApply
        fields = ('education_level', 'previousjobs', 'resume')
