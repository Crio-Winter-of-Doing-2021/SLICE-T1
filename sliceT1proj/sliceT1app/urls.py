from django.urls import path
from sliceT1app import views
from django.conf import settings # new

app_name='sliceT1app'
urlpatterns=[

    path('',views.index,name='selectSS'),
    path('ds',views.selectDataSource,name='selectDS'),
    path('google_api', views.google_api.as_view(), name="g_api"),
    path('files_display', views.render_files, name="display_Files"),
    path('file_delete/<id>',views.delete_file,name='deleteFile'),
    path('local_api', views.local_api.as_view(), name="local_api"),
]
