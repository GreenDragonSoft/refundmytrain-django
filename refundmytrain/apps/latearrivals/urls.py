from django.conf.urls import url
from .views import (
    ListLateArrivals
)

urlpatterns = [
    url(r'^$',
        ListLateArrivals.as_view()),
]
