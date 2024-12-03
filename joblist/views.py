from django.shortcuts import render, redirect, get_object_or_404
from .forms import JobForm, Application
from .models import JobListing, JobApply
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
job_id_saver = 0

def home(request): 
    user = request.user
    if user.is_authenticated:
        role = user.role
        if role == "Student":
            apps = JobApply.objects.filter(creater = user)
            return render(request, "joblist/studentview.html", {"apps": apps})
        else:
            return render(request, 'joblist/home.html')
    else:
        return render(request, 'joblist/home.html')
    
def listings(request):
    jobs = JobListing.objects.all()
    jobtypechoices = ( ("Arts", "Arts"), ("Business", "Business"), ("Communications", "Communications"), ("Education", "Education"), ("Healthcare", "Healthcare"), ("Hospitality", "Hospitality"), ("Information Technology", "Information Technology"), ("Law Enforcement", "Law Enforcement"), ("Sales and Marketing", "Sales and Marketing"), ("Science", "Science"), ("Transportation", "Transportation"), ("Other", "Other" ))
    return render(request, 'joblist/view-listings.html', {"jobs": jobs, "displayform": False, "jobtypechoices": jobtypechoices})
def profile(request):
    return
def make_listings(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            application = form.save(commit = False)
            application.author = request.user
            application.save()
            return redirect('/')
    form = JobForm()
    return render(request, "joblist/make-listings.html", {"form": form})
def submitapp(request):
    global job_id_saver
    if request.method == "POST":
        job_id = request.POST.get('job-id')
        print(job_id, type(job_id))
        if isinstance(job_id, str):
            job_id_saver = int(job_id)
        print(job_id_saver, job_id)
        job = JobListing.objects.filter(pk = int(job_id_saver)).first()      
        print(job.job_title)  
        jobform = Application(request.POST or None)
        if jobform.is_valid():
            app = jobform.save(commit=False)
            app.job = job
            app.creater = request.user
            app.save()
            messages.success(request, "form submitted successfully")
            all_objects = JobApply.objects.all()
            for obj in all_objects:
                print(obj)
            return redirect('/')

    jobform = Application()
    return render(request, 'joblist/view-listings.html', {"form": jobform, "displayform": True})
def view_applications(request):
    user = request.user
    jobs = JobListing.objects.filter(author = user)
    apps = {}
    for job in jobs:
        app = JobApply.objects.filter(job = job)
        apps[job.id] = app
    print(apps)
    return render(request, 'joblist/view-applications.html', {"jobs":jobs, "apps":apps})   
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
