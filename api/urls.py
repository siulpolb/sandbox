from django.urls import include, path
from rest_framework.routers import SimpleRouter, DefaultRouter, Route

from . import views


class CustomRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^{prefix}$',
            mapping={'get': 'list', 'patch': 'bulk_partial_update'},
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        Route(
            url=r'^{prefix}/{lookup}$',
            mapping={'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'},
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Detail'}
        ),
    ]

router = DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)
# router.register(r"questions", views.QuestionViewSet)
router.register(r"choices", views.ChoiceViewSet)

custom_router = CustomRouter()
custom_router.register(r"questions", views.QuestionViewSet)

# app_name = "api"
urlpatterns = [
    path("", include(router.urls)),
    path("", include(custom_router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework"))
]
