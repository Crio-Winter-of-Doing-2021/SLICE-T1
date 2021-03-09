from django.urls import path
from sliceT1app import views
from django.conf import settings # new

app_name='sliceT1app'
urlpatterns=[

    path('',views.index,name='selectSS'),
    path('ds',views.selectDataSource,name='selectDS'),
    path('google_api', views.google_api, name="g_api"),
]
