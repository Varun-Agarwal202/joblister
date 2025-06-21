from django.urls import path, include,re_path
from . import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns= [
    path('', views.home, name="homepage"),
    path('view-listings/', views.listings, name="view-listings"),
    path('mentorapply/', views.mentorapply, name="mentor-apply"),
    path('profile/', views.profile, name="view-profile"),
    re_path(r'^make-listings/(?P<job_id>-?\d+)/$', views.make_listings, name="make-listings"),
    path('view-listings/submit-application/', views.submitapp, name="submit-app" ),
    path('view-applications/', views.view_applications, name="view-applications"),
    path('updateAppStatus/<int:app_id>/', views.updatestatus, name="update-app-status"),
    path('deleteApp/<int:app_id>/', views.deleteapp, name="delete-app-status"),
    path('approvelistings/', views.approvejob, name="approve-job"),
    path('approvementor', views.approvementor, name="approve-mentor"),
    path('updateJobStatus/<int:job_id>/', views.updatejobstatus, name="update-job-status"),
    path('updateMentorStatus/<int:job_id>/', views.updatementorstatus, name="update-job-status"),
    path('manage-listings', views.managelistings, name="manage-listings"),
    path('deleteListing/<int:job_id>/', views.deletelisting, name="delete-listing-status"),
    path('view-mentors', views.viewmentors,name="view-mentors"),
    path('students/', views.students, name="students"),
    path('submit-mentor/', views.submitmentor, name="submit-mentor"),
    path('accept-student/<int:student_id>/<str:status>/', views.accept_student, name="accept-student"),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('api/events/', views.event_api, name='event-api'),
    path('student-calendar/', views.StudentCalendarView.as_view(), name='student-calendar'),
    path('offers/', views.offers, name="offers"),
    path('jobOffer/', views.jobOffer, name="job-offer"),
    path('job-offers/', views.job_offers, name="job-offers"),
    path('edit-profile/', views.edit_profile, name="edit-profile"),
    path('sources/', views.sources, name="sources"),
    path('chatbot/', views.chatbot, name='chatbot'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
