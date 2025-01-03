from django.urls import path, include
from . import views
from django.views.generic import TemplateView
urlpatterns= [
    path('', views.home, name="homepage"),
    path('view-listings/', views.listings, name="view-listings"),
    path('profile/', views.profile, name="view-profile"),
    path('make-listings/', views.make_listings, name="make-listings"),
    path('view-listings/submit-application/', views.submitapp, name="submit-app" ),
    path('view-applications/', views.view_applications, name="view-applications"),
    path('updateAppStatus/<int:app_id>/', views.updatestatus, name="update-app-status"),
    path('deleteApp/<int:app_id>/', views.deleteapp, name="delete-app-status"),
]
