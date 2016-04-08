"""refundmytrain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views import (
    TimetableJourneyList, TimetableJourneyDetail
)
from . import views


urlpatterns = [

    url(r'^$',
        TimetableJourneyList.as_view(),
        name='journey-list'),

    url(r'^(?P<from>[a-z]{3})/(?P<to>[a-z]{3})/$',
        views.TimetableJourneyListFromTo.as_view(),
        name='journey-list-from-to'),

    url(r'^journey/(?P<pk>\d{15})/$',
        TimetableJourneyDetail.as_view(),
        name='journey-detail'),
]
