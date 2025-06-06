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
from listings.views import home, home2, aboutus, aboutus2, service, service2, add_listing, listings, listings2, property_detail, property_detail2, my_listings, edit_property, delete_property, debug_media
from django.conf import settings
from django.conf.urls.static import static

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
        path('debug-media/', debug_media, name='debug_media'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG or True:  # Always serve media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
