from django.urls import path, re_path, include
from django.views.generic import TemplateView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


app_patterns = [path('api/', include('api.urls'))]


def get_swagger_view(patterns):
    return get_schema_view(
        openapi.Info(
                title="Music Catalog API",
                default_version='v1',
                description="Music Api Test",
            ),
        patterns=patterns,
        public=True,
        permission_classes=[permissions.IsAuthenticatedOrReadOnly]
    )


view = get_swagger_view(app_patterns)


urlpatterns = [
    path(
        'swagger-ui/',
        TemplateView.as_view(
            template_name='swaggerui/swaggerui.html',
            extra_context={'schema_url': 'openapi-schema'}
        ),
        name='swagger-ui'),
    re_path(
            r'^swagger(?P<format>\.json|\.yaml)$',
            view.without_ui(cache_timeout=0),
            name='schema-json'
            ),
    ]
