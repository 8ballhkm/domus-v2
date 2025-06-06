"""
URL configuration for domus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from chat import views
from listings.views import home, home2, aboutus, aboutus2, service, service2, add_listing, listings, listings2, property_detail, property_detail2, my_listings, edit_property, delete_property, check_files, simple_debug
from django.conf import settings
from django.conf.urls.static import static
from django.http import Http404
from django.views.static import serve
import os

def custom_media_serve(request, path, document_root=None, show_indexes=False):
    """
    Custom media serving function that checks multiple directories
    """
    # Primary location (volume mount)
    primary_path = os.path.join('/mnt/storage/images', path)
    if os.path.exists(primary_path):
        return serve(request, path, document_root='/mnt/storage/images', show_indexes=show_indexes)
    
    # Fallback location (app directory)
    fallback_path = os.path.join('/app/media', path)
    if os.path.exists(fallback_path):
        return serve(request, path, document_root='/app/media', show_indexes=show_indexes)
    
    # If neither exists, return 404
    raise Http404("Media file not found")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('home', home2, name='home2'),
    path('aboutus', aboutus, name='aboutus'),
    path('aboutus/', aboutus2, name='aboutus2'),
    path('service', service, name='service'),
    path('service/', service2, name='service2'),
    path('users/', include('users.urls')),
    path('add-listing/', add_listing, name='add_listing'),
    path('listings/', listings, name='listings'),   
    path('listings2/', listings2, name='listings2'),
    path('property/<uuid:pk>/', property_detail, name='property_detail'),
    path('property2/<uuid:pk>/', property_detail2, name='property_detail2'),
    path('my-listings/', my_listings, name='my_listings'),
    #path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
    path('chat/with/<str:username>/', views.chat_with_user, name='chat_with_user'),
    path('api/chat/rooms/', views.chat_rooms_api, name='chat_rooms_api'),
    path('api/chat/history/<int:partner_id>/', views.chat_history_api, name='chat_history_api'),
    path('edit_property/<uuid:id>/', edit_property, name='edit_property'),
    path('delete_property/<uuid:id>/', delete_property, name='delete_property'),
    path('check-files/', check_files, name='check_files'),
    path('simple-debug/', simple_debug, name='simple_debug'),
    path('media/<path:path>', custom_media_serve, name='media'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
