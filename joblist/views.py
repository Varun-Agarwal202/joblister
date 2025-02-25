from django.shortcuts import render, redirect, get_object_or_404
from .forms import JobForm, Application, mentorApply
from .models import JobListing, JobApply, applicationMentor, CustomUser, MeetingEvent
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from datetime import datetime
from django.db.models import Count
from django.contrib.auth.decorators import login_required

import json
job_id_saver = 0

def home(request): 
    user = request.user
    context = {'user': user}
    
    if user.is_authenticated:
        if user.is_superuser:
            context['admin'] = True
            # Add admin dashboard stats
            context['total_users'] = CustomUser.objects.count()
            context['total_jobs'] = JobListing.objects.count()
            context['total_applications'] = JobApply.objects.count()
            
            # Add job categories chart data
            job_categories = JobListing.objects.values('job_type').annotate(count=Count('job_type'))
            context['job_categories'] = {item['job_type']: item['count'] for item in job_categories}
            
        else:
            context['admin'] = False
            if user.role == "Student":
                apps = JobApply.objects.filter(creater=user)
                context['apps'] = apps
                
                # Create status counts dictionary
                status_counts = apps.values('status').annotate(count=Count('status'))
                
                # Create separate lists for labels and values
                status_chart = {
                    'labels': [],
                    'values': []
                }
                
                for item in status_counts:
                    status_chart['labels'].append(item['status'])
                    status_chart['values'].append(item['count'])
                
                context['status_chart'] = status_chart
                
                if user.mentor and user.status_mentor == "accept":
                    context['mentor'] = user.mentor.author
                    
            if user.role == "Employer":
                job_listings = JobListing.objects.filter(author=user)
                context['job_listings'] = job_listings
                
                # Add applications per job chart data
                apps_per_job = {}
                for job in job_listings:
                    apps_per_job[job.job_title] = JobApply.objects.filter(job=job).count()
                context['apps_per_job'] = apps_per_job
                
            if user.role == "Mentor":
                mentees = CustomUser.objects.filter(mentor=applicationMentor.objects.filter(author=user).first())
                context['mentees'] = mentees
                context['meetings'] = MeetingEvent.objects.filter(mentor=user).order_by('-created_at').first()
                
                # Add mentee progress tracking
                mentee_progress = {}
                for mentee in mentees:
                    completed_meetings = MeetingEvent.objects.filter(
                        mentor=user,
                        attendees=mentee
                    ).count()
                    mentee_progress[mentee.email] = completed_meetings
                context['mentee_progress'] = mentee_progress
    
    return render(request, 'joblist/home.html', context)
@login_required   
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
@login_required   

def profile(request):
    return render(request, 'joblist/profile.html', {"user": request.user})
@login_required   

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
        request.user.status_mentor = "pending"
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

class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'joblist/calendar.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_student'] = False
        return context

@require_http_methods(["GET", "POST"])
def event_api(request):
    if request.method == "GET":
        if request.user.role == "Student":
            # Get all public meetings
            public_meetings = MeetingEvent.objects.filter(private=False)
            
            # If student has a mentor, also get their private meetings
            if request.user.mentor:
                mentor_private_meetings = MeetingEvent.objects.filter(
                    mentor=request.user.mentor.author,
                    private=True
                )
                # Combine querysets
                events = public_meetings | mentor_private_meetings
            else:
                events = public_meetings

        else:
            # If user is a mentor, get their own events
            events = MeetingEvent.objects.filter(mentor=request.user)

        return JsonResponse([{
            'event_id': event.id,
            'title': event.title,
            'start': event.start.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': event.end.strftime('%Y-%m-%dT%H:%M:%S'),
            'description': event.description,
            'limit_people': event.limit_people,
            'private': event.private,
            'current_people': event.current_people,
            'mentor_fname': event.mentor.first_name,
            'mentor_lname': event.mentor.last_name,
            'mentor_email': event.mentor.email,
            'mentor_phone': event.mentor.phone,
            'has_joined': event.attendees.filter(id=request.user.id).exists()
        } for event in events], safe=False)
    
    elif request.method == "POST":
        data = json.loads(request.body)
        if request.user.role == "Student":
            event = MeetingEvent.objects.get(id=data['event_id'])
            
            if data.get('action') == 'cancel':
                event.attendees.remove(request.user)
                event.current_people -= 1
                event.save()
                return JsonResponse({'success': True})
            elif data.get('action') == 'join':
                event.attendees.add(request.user)
                event.current_people += 1
                event.save()
                return JsonResponse({'success': True})
                
        else:
            event = MeetingEvent.objects.create(
                mentor=request.user,
                title=data['title'],
                start=datetime.fromisoformat(data['start'].replace('Z', '+00:00')),
                end=datetime.fromisoformat(data['end'].replace('Z', '+00:00')),
                description=data['description'],
                limit_people=data['limit_people'],
                private=data['private']
            )
            
        return JsonResponse({
            'event_id': event.id,
            'title': event.title,
            'start': event.start.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': event.end.strftime('%Y-%m-%dT%H:%M:%S'),
            'description': event.description,
            'limit_people': event.limit_people,
            'private': event.private
        })
class StudentCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'joblist/calendar.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = MeetingEvent.objects.filter(mentor=self.request.user)
        context['is_student'] = True
        return context
def offers(request):
    students = JobApply.objects.filter(creater__role = "Student")
    students = students.filter(resume__isnull = False)
    students = students.exclude(status = "accepted")
    
    job = JobListing.objects.filter(author = request.user)
    print(job, 'job')
    print(job, 'JOB')
    if job.count() == 1:
        return render(request, "joblist/offers.html", {"students": students, "ask": False, "job": job.first()})
    elif job.count() > 1:
        return render(request, "joblist/offers.html", {"students": students, "ask": True, "job": job})
    else:
        return render(request, "joblist/offers.html", {"students": students, "ask": False, "job": None})
def jobOffer(request):
    data = json.loads(request.body)
    if data.get('status') == "":
        student = CustomUser.objects.get(id = data.get('student_id'))
        student.offers.add(JobListing.objects.get(id = data.get('job_id')))
        student.save()
    elif data.get('status') == 'accept':
        student = CustomUser.objects.get(id = data.get('student_id'))
        student.offers.remove(JobListing.objects.get(id = data.get('job_id')))
        student_application = JobApply.objects.get(creater = student)
        student_application.job = JobListing.objects.get(id = data.get('job_id'))
        student_application.status = 'accepted'
        student.save()
        student_application.save()
    elif data.get('status') == 'reject':
        student = CustomUser.objects.get(id = data.get('student_id'))
        student.offers.remove(JobListing.objects.get(id = data.get('job_id')))
        student.save()
    
    return JsonResponse({'success': True})

def job_offers(request):
    offers = request.user.offers.all()
    student_id = request.user.id
    return render(request, "joblist/job-offers.html", {"offers": offers, "student_id": student_id})
def edit_profile(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Split the full name into first_name and last_name
            full_name = data.get('first_name', '').split()
            if len(full_name) >= 2:
                first_name = full_name[0]
                last_name = ' '.join(full_name[1:])
            else:
                first_name = full_name[0] if full_name else ''
                last_name = ''  # or some default value
            
            # Update user information
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = data.get('email')
            user.phone = data.get('phone')
            user.address = data.get('address')
            user.gender = data.get('gender')
            user.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Profile updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)
def sources(request):
    return render(request, "joblist/sources.html")