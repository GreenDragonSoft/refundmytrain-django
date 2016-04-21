from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$',
    #     view.StatusIndex.as_view()),

    url(r'arrivals/$',
        views.StatusArrivals.as_view()),
]
