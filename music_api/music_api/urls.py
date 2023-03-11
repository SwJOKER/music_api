from django.urls import include, path


urlpatterns = [
    path('', include('api.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
]
