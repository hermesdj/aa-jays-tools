from django.urls import include, re_path

from allianceauth import urls

urlpatterns = [
    re_path(r"", include(urls)),
]

