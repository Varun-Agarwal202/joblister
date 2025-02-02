from django.shortcuts import render, redirect, get_object_or_404
from .forms import JobForm, Application, mentorApply
from .models import JobListing, JobApply, applicationMentor, CustomUser
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import json
job_id_saver = 0

def home(request): 
    user = request.user
    if user.is_superuser:
        return render(request, "joblist/home.html", {"admin": True})
    if user.is_authenticated:
        role = user.role
        if role == "Student":
            apps = JobApply.objects.filter(creater = user)
            return render(request, "joblist/studentview.html", {"apps": apps})
        else:
            return render(request, 'joblist/home.html', {"admin": False})
    else:
        return render(request, 'joblist/home.html', {"admin": False})
    
def listings(request):
    jobs2 = []
    jobs = JobListing.objects.filter(status = "approve")
    for job in jobs:
        try:
            if (JobApply.objects.filter(job = job )).first().status != "accepted":
                jobs2.append(job)
        except:
            jobs2.append(job)
    jobtypechoices = ( ("Arts", "Arts"), ("Business", "Business"), ("Communications", "Communications"), ("Education", "Education"), ("Healthcare", "Healthcare"), ("Hospitality", "Hospitality"), ("Information Technology", "Information Technology"), ("Law Enforcement", "Law Enforcement"), ("Sales and Marketing", "Sales and Marketing"), ("Science", "Science"), ("Transportation", "Transportation"), ("Other", "Other" ))
    return render(request, 'joblist/view-listings.html', {"jobs": jobs2, "displayform": False, "jobtypechoices": jobtypechoices})
def profile(request):
    return
def make_listings(request, job_id):
    if job_id == "-1": 
        form = JobForm()
    else:
        job_id = int(job_id)
        job = get_object_or_404(JobListing, pk=job_id)
        form = JobForm(instance=job)
    if request.method == "POST":
            form = JobForm(request.POST)
            if form.is_valid():
                application = form.save(commit = False)
                application.status = "pending"
                application.author = request.user
                application.save()
                if job_id != "-1":  
                    JobListing.objects.filter(pk = job_id).delete()
                messages.success(request, "Job listing request pending")
                return redirect('/')
            else:
                if job_id == "-1": 
                    form = JobForm()
                else:
                    job_id = int(job_id)
                    job = get_object_or_404(JobListing, pk=job_id)
                    form = JobForm(instance=job)

    
    return render(request, "joblist/make-listings.html", {"form": form})    

    
def submitapp(request):
    if request.method == "POST":
        job_id = request.POST.get('job-id')
        print("Received Job ID from POST:", job_id)

        if not job_id:
            messages.error(request, "Job ID is missing.")
            return redirect('/')

        try:
            job = JobListing.objects.get(pk=int(job_id))
        except ValueError:
            messages.error(request, "Invalid Job ID format.")
            return redirect('/')
        except JobListing.DoesNotExist:
            messages.error(request, "Job listing not found.")
            return redirect('/')

        # Process the application form as usual
        existing_application = JobApply.objects.filter(job=job, creater=request.user).first()
        if existing_application:
            jobform = Application(request.POST, request.FILES, instance=existing_application)
        else:
            jobform = Application(request.POST, request.FILES)

        if jobform.is_valid():
            app = jobform.save(commit=False)
            app.job = job
            app.creater = request.user
            app.first_name = request.user.first_name
            app.last_name = request.user.last_name
            app.email = request.user.email
            app.gender = request.user.gender
            app.birthdate = request.user.birthday
            app.address = request.user.address
            app.phone = request.user.phone
            app.save()
            messages.success(request, "Application submitted successfully.")
            return redirect('/')
        else:
            if existing_application:
                jobform = Application(instance=existing_application)
            else:
                jobform = Application()

            return render(request, 'joblist/view-listings.html', {"form": jobform, "displayform": True, "job_id": job_id, "user": request.user})

    else:
        # Handle GET requests or initialize the form
        job_id = request.GET.get('job-id')
        if job_id:
            job = JobListing.objects.filter(pk=int(job_id)).first()
            if job:
                existing_application = JobApply.objects.filter(job=job, creater=request.user).first()
                jobform = Application(instance=existing_application) if existing_application else Application()
                return render(request, 'joblist/view-listings.html', {"form": jobform, "displayform": True})

    messages.error(request, "Invalid request.")
    return redirect('/')


def view_applications(request):
    user = request.user
    jobs = JobListing.objects.filter(author = user)
    apps = {}
    for job in jobs:
        app = JobApply.objects.filter(job = job)
        apps[job.id] = app
    print(apps)
    return render(request, 'joblist/view-applications.html', {"jobs":jobs, "apps":apps, 'MEDIA_URL': settings.MEDIA_URL,})   
@csrf_exempt
def updatestatus(request, app_id):
    if request.method == "POST":
        try: 
            data = json.loads(request.body)
            status = data.get('status')
            application = JobApply.objects.get(id = app_id)
            application.status = status
            application.save()
            return JsonResponse({'success': True})
        except JobApply.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Application Not Found'}, )
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, )
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
@csrf_exempt
def deleteapp(request, app_id):
    JobApply.objects.filter(pk = app_id).delete()
    return redirect('/')
def mentorapply(request):
     if request.method == "POST":
        form = mentorApply(request.POST)
        print("Hi2")
        if form.is_valid():
            print("Hi1")
            application = form.save(commit = False)
            application.author = request.user
            application.status = "pending"
            messages.success(request, "Mentor request pending")
            application.save()
            return redirect('/')
     print("Hi3")
     form = mentorApply()
     return render(request, "joblist/mentorapply.html", {"form": form})
def approvejob(request):
    jobs = JobListing.objects.filter(status = "pending")
    return render(request, "joblist/approvejob.html", {"jobs": jobs})
def approvementor(request):
    applications = applicationMentor.objects.filter(status = "pending")
    return render(request, "joblist/approvepending.html", {"jobs": applications})
def updatejobstatus(request, job_id):
    if request.method == "POST":
        try: 
            data = json.loads(request.body)
            status = data.get('status')
            application = JobListing.objects.get(id = job_id)
            application.status = status
            application.save()
            return JsonResponse({'success': True})
        except JobApply.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Application Not Found'}, )
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, )
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
def updatementorstatus(request, job_id):
    if request.method == "POST":
        try: 
            data = json.loads(request.body)
            status = data.get('status')
            application = applicationMentor.objects.get(id = job_id)
            application.status = status
            application.save()
            return JsonResponse({'success': True})
        except JobApply.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Application Not Found'}, )
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, )
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
def managelistings(request):
    jobs = JobListing.objects.filter(author = request.user)
    return render(request, "joblist/manage-listings.html", {"jobs": jobs})
def deletelisting(request, job_id):
    JobListing.objects.filter(pk = job_id).delete()
    return redirect('/')
def viewmentors(request):
    mentors = applicationMentor.objects.filter(status = "approve")
    jobtypechoices = ( ("Arts", "Arts"), ("Business", "Business"), ("Communications", "Communications"), ("Education", "Education"), ("Healthcare", "Healthcare"), ("Hospitality", "Hospitality"), ("Information Technology", "Information Technology"), ("Law Enforcement", "Law Enforcement"), ("Sales and Marketing", "Sales and Marketing"), ("Science", "Science"), ("Transportation", "Transportation"), ("Other", "Other" ))
    context = {
        "jobs": mentors, 
        "displayform": False, 
        "jobtypechoices": jobtypechoices,
        "has_mentor": request.user.mentor is not None,
        "current_mentor": request.user.mentor.author.first_name if request.user.mentor else None
    }
    
    return render(request, 'joblist/view-mentors.html', context)
def submitmentor(request):
    if request.method == "POST":
        job_id = request.POST.get("job_id")
        request.user.mentor = applicationMentor.objects.get(pk = job_id)
        request.user.save()
        return redirect('/')
    return redirect('/')
def students(request):
    print(applicationMentor.objects.filter(author = request.user).first(), 'bye')
    requests = CustomUser.objects.filter(mentor = applicationMentor.objects.filter(author = request.user).first())
    print(requests, 'hi')
    requests = requests.filter(role = "Student")
    requests = requests.filter(status_mentor = "pending")
    approved_students = CustomUser.objects.filter(mentor = applicationMentor.objects.filter(author = request.user).first())
    approved_students = approved_students.filter(role = "Student")
    approved_students = approved_students.filter(status_mentor = "accept")
    print(approved_students, 'hi2')
    return render(request, "joblist/students.html", {"requests": requests, "approved_students": approved_students})
def accept_student(request, student_id, status):
    student = CustomUser.objects.get(id = student_id)
    student.status_mentor = status
    if status == "reject":
        student.mentor = None
    print(status)
    student.save()
    return JsonResponse({'success': True})