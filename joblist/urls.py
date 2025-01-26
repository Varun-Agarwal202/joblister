from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns= [
    path('', views.home, name="homepage"),
    path('view-listings/', views.listings, name="view-listings"),
    path('mentorapply/', views.mentorapply, name="mentor-apply"),
    path('profile/', views.profile, name="view-profile"),
    path('make-listings/', views.make_listings, name="make-listings"),
    path('view-listings/submit-application/', views.submitapp, name="submit-app" ),
    path('view-applications/', views.view_applications, name="view-applications"),
    path('updateAppStatus/<int:app_id>/', views.updatestatus, name="update-app-status"),
    path('deleteApp/<int:app_id>/', views.deleteapp, name="delete-app-status"),
    path('approvelistings/', views.approvejob, name="approve-job"),
    path('approvementor', views.approvementor, name="approve-mentor"),
    path('updateJobStatus/<int:job_id>/', views.updatejobstatus, name="update-job-status"),
    path('updateMentorStatus/<int:job_id>/', views.updatementorstatus, name="update-job-status"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
