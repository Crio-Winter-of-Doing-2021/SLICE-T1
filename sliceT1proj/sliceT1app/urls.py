from django.urls import path
from sliceT1app import views
from django.conf import settings # new

app_name='sliceT1app'
urlpatterns=[

    path('',views.index,name='selectSS'),

    path('storage_source/awsS3',views.get_s3_credentials.as_view(),name='awsS3'),
    path('ds',views.selectDataSource,name='selectDS'),
    path('google_api', views.google_api, name="g_api"),
    path('files_display', views.render_files, name="display_Files"),
    path('file_delete/<id>',views.delete_file,name='deleteFile'),
    path('local_api', views.local_api.as_view(), name="local_api"),
    path('upload_S3', views.upload_S3, name="upload_S3"),
]
