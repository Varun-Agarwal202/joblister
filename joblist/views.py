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
from django.core.mail import send_mail
from google import genai
from django.utils.safestring import mark_safe
import markdown
from django.views.decorators.http import require_http_methods
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_exempt
import logging


client = genai.Client(api_key="AIzaSyCYq6LwXQcLhqv50VtvBoU588j1gioakK8")


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
                if applicationMentor.objects.filter(author=user).first() == None:
                    mentees = []
                else:
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
    jobs = JobListing.objects.filter(status = "approve")

    jobtypechoices = ( ("Arts", "Arts"), ("Business", "Business"), ("Communications", "Communications"), ("Education", "Education"), ("Healthcare", "Healthcare"), ("Hospitality", "Hospitality"), ("Information Technology", "Information Technology"), ("Law Enforcement", "Law Enforcement"), ("Sales and Marketing", "Sales and Marketing"), ("Science", "Science"), ("Transportation", "Transportation"), ("Other", "Other" ))
    return render(request, 'joblist/view-listings.html', {"jobs": jobs, "displayform": False, "jobtypechoices": jobtypechoices})
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
# @csrf_exempt
def updatestatus(request, app_id):
    print(f"updatestatus called with app_id: {app_id}")
    print(f"Request method: {request.method}")
    print(f"Request body: {request.body}")
    print(f"Request POST: {request.POST}")
    print(f"Request GET: {request.GET}")
    print(f"Request headers: {request.headers}")
    
    # Temporarily allow GET for testing
    if request.method == "GET":
        return JsonResponse({'success': False, 'error': 'GET request received - this is expected for testing'})
    
    if request.method == "POST":
        try: 
            # Try to get data from JSON first, then from POST
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                status = data.get('status')
            else:
                # Handle form data
                status = request.POST.get('status')
            
            print(f"Status: {status}")
            
            application = JobApply.objects.get(id = app_id)
            print(f"Found application: {application.first_name} {application.last_name}")
            print(f"Current status: {application.status}")
            
            application.status = status
            application.save()
            print(f"Status updated to: {application.status}")
            
            if status == "accepted":
                try:
                    send_mail(
                        subject = 'Congratulations, your job application has been accepted!',
                        message = f'''Hi {application.first_name},

Congratulations! You've been accepted for the position at {application.job.company_name}.

The employer was impressed with your application and is excited to have you on board. They will be reaching out to you soon with more details about the next steps, including onboarding and your start date.

In the meantime, feel free to prepare any documents or questions you might have for your new role.

We're proud of you—this is a big step forward!

Best of luck,  
The PathFinder Team''',
                        from_email = 'pathfinderrequest@gmail.com',
                        recipient_list = [application.email,],
                        fail_silently = True,  # Changed to True to prevent email errors from breaking the function
                    )
                    print("Email sent successfully")
                except Exception as email_error:
                    print(f"Email sending failed: {email_error}")
                    # Continue even if email fails
                    
            print("Returning success response")
            return JsonResponse({'success': True})
        except JobApply.DoesNotExist:
            print(f"JobApply with id {app_id} not found")
            return JsonResponse({'success': False, 'error': 'Application Not Found'})
        except Exception as e:
            print(f"Error in updatestatus: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        print(f"Invalid request method: {request.method}")
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
@csrf_exempt
def deleteapp(request, app_id):
    JobApply.objects.filter(pk = app_id).delete()
    return redirect('/')
@login_required
def mentorapply(request):
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Request method: {request.method}")
    if request.method == "POST":
        form = mentorApply(request.POST)
        logging.info(f"Form is valid: {form.is_valid()}")
        if form.is_valid():
            application = form.save(commit = False)
            application.author = request.user
            application.status = "pending"
            messages.success(request, "Mentor request pending")
            application.save()
            return redirect('/')
        else:
            logging.error(f"Form errors: {form.errors.as_json()}")
            # If form is invalid, show errors
            return render(request, "joblist/mentorapply.html", {"form": form})
    else:
        form = mentorApply()
    return render(request, "joblist/mentorapply.html", {"form": form})
def approvejob(request):
    jobs = JobListing.objects.filter(status = "pending")
    return render(request, "joblist/approvejob.html", {"jobs": jobs})
def approvementor(request):
    applications = applicationMentor.objects.filter(status = "pending")
    return render(request, "joblist/approvepending.html", {"jobs": applications})

@csrf_exempt  # TEMPORARY: Remove this after debugging if you want CSRF protection!
def updatejobstatus(request, job_id):
    print("Request method:", request.method)
    print("Request headers:", request.headers)
    print("Request body:", request.body)
    print("Request POST:", request.POST)
    try:
        if request.method == "POST":
            import json
            try:
                data = json.loads(request.body)
                status = data.get('status')
            except Exception:
                status = request.POST.get('status')
            print("Status to set:", status)
            job = JobListing.objects.get(id=job_id)
            job.status = status
            job.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request method.'})
    except Exception as e:
        print("Error:", e)
        return JsonResponse({'success': False, 'error': str(e)})
@csrf_exempt
def updatementorstatus(request, job_id):
    print("Request method (updatementorstatus):", request.method)
    print("Request body (updatementorstatus):", request.body)
    print("Request POST (updatementorstatus):", request.POST)
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            status = data.get('status')
            print("Status to set (updatementorstatus):", status)
            application = applicationMentor.objects.get(id = job_id)
            application.status = status
            application.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request method.'})
    except applicationMentor.DoesNotExist:
        print(f"applicationMentor with id {job_id} not found")
        return JsonResponse({'success': False, 'error' : 'Application Not Found'}, status=404)
    except Exception as e:
        print("Error in updatementorstatus:", e)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
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
    else:
        send_mail(
            subject = 'Congratulations, your mentor request has been approved!',
            message = '''Hi''' + student.first_name + ''',

Great news! Your request to be mentored by ''' + student.mentor.first_name + ''' has been approved.

You can now connect with your mentor and start collaborating on your career journey. Feel free to reach out, ask questions, and make the most of this opportunity!

If you have any questions or need support, we're here to help.

Best regards,  
The PathFinder Team''',
            from_email = 'pathfinderrequest@gmail.com',
            recipient_list = [student.email,],
            fail_silently = False,
    )
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
        print(f"Event API POST request received. User role: {request.user.role}")
        data = json.loads(request.body)
        print(f"Event API received data: {data}")
        if request.user.role == "Student":
            event = MeetingEvent.objects.get(id=data['event_id'])
            
            if data.get('action') == 'cancel':
                event.attendees.remove(request.user)
                event.current_people -= 1
                event.save()
                print("Student cancelled meeting.")
                return JsonResponse({'success': True})
            elif data.get('action') == 'join':
                event.attendees.add(request.user)
                event.current_people += 1
                event.save()
                print("Student joined meeting.")
                return JsonResponse({'success': True})
                
        else: # This block is for mentors creating events
            try:
                event = MeetingEvent.objects.create(
                    mentor=request.user,
                    title=data['title'],
                    start=datetime.fromisoformat(data['start'].replace('Z', '+00:00')),
                    end=datetime.fromisoformat(data['end'].replace('Z', '+00:00')),
                    description=data['description'],
                    limit_people=data['limit_people'],
                    private=data['private']
                )
                print(f"New meeting event created by mentor: {event.title} (ID: {event.id})")
            except Exception as e:
                print(f"Error creating meeting event: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
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
        student_application = JobApply.objects.get(creater = student).first()
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


@require_http_methods(["GET", "POST"])
def chatbot(request):
    # Get the chat history from the session, or initialize an empty list
    chat_history = request.session.get('chat_history', [])

    if request.method == "POST":
        user_input = request.POST.get("user_input")
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=user_input)       
        response_text = mark_safe(markdown.markdown(response.text))
        response_text = BeautifulSoup(response_text).get_text()
        # Append new messages to the chat history
        chat_history.append({"type": "user", "content": user_input})
        chat_history.append({"type": "ai", "content": response_text})
        
        # Save the updated chat history to the session
        request.session['chat_history'] = chat_history
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"response": response_text})
    
    return render(request, "joblist/chat.html", {"chat_history": chat_history})
def help(request):
    return render(request, "joblist/help.html")

def accept_application(request, app_id):
    try:
        application = JobApply.objects.get(id=app_id)
        application.status = "accepted"
        application.save()
        
        # Send email
        try:
            send_mail(
                subject = 'Congratulations, your job application has been accepted!',
                message = f'''Hi {application.first_name},

Congratulations! You've been accepted for the position at {application.job.company_name}.

The employer was impressed with your application and is excited to have you on board. They will be reaching out to you soon with more details about the next steps, including onboarding and your start date.

In the meantime, feel free to prepare any documents or questions you might have for your new role.

We're proud of you—this is a big step forward!

Best of luck,  
The PathFinder Team''',
                from_email = 'pathfinderrequest@gmail.com',
                recipient_list = [application.email,],
                fail_silently = True,
            )
        except Exception as email_error:
            print(f"Email sending failed: {email_error}")
        
        messages.success(request, f"Application for {application.first_name} {application.last_name} has been accepted!")
    except JobApply.DoesNotExist:
        messages.error(request, "Application not found!")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    return redirect('view-applications')

def reject_application(request, app_id):
    try:
        application = JobApply.objects.get(id=app_id)
        application.status = "rejected"
        application.save()
        messages.success(request, f"Application for {application.first_name} {application.last_name} has been rejected!")
    except JobApply.DoesNotExist:
        messages.error(request, "Application not found!")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    return redirect('view-applications')

def approve_job(request, job_id):
    try:
        job = JobListing.objects.get(id=job_id)
        job.status = "approve"
        job.save()
        messages.success(request, f"Job listing '{job.job_title}' has been approved!")
    except JobListing.DoesNotExist:
        messages.error(request, "Job listing not found!")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    return redirect('approve-job')

def reject_job(request, job_id):
    try:
        job = JobListing.objects.get(id=job_id)
        job.status = "reject"
        job.save()
        messages.success(request, f"Job listing '{job.job_title}' has been rejected!")
    except JobListing.DoesNotExist:
        messages.error(request, "Job listing not found!")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    return redirect('approve-job')

def approve_mentor(request, mentor_id):
    try:
        application = applicationMentor.objects.get(id=mentor_id)
        application.status = "approve"
        application.save()
        messages.success(request, f"Mentor application for {application.first_name} {application.last_name} has been approved!")
    except applicationMentor.DoesNotExist:
        messages.error(request, "Mentor application not found!")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    return redirect('approve-mentor')

def reject_mentor(request, mentor_id):
    try:
        application = applicationMentor.objects.get(id=mentor_id)
        application.status = "reject"
        application.save()
        messages.success(request, f"Mentor application for {application.first_name} {application.last_name} has been rejected!")
    except applicationMentor.DoesNotExist:
        messages.error(request, "Mentor application not found!")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    return redirect('approve-mentor')