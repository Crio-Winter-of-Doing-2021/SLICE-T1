from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from sliceT1app.serializers import DocSerializer
import json
from django.http import JsonResponse
from sliceT1app.models import fileDoc
from rest_framework.decorators import api_view
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import FileSystemStorage
from sliceT1app.scripts.google_api_getfile import *
import boto3

###################
'''
Parameters For Credentials for configuration
'''
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
media_dir = os.path.join(base_dir, 'media')

bucket_received=None
access_id_received=None
secret_key_received=None
object_token=None
##################

def index(request):
    return render(request,'page0.html')

def selectDataSource(request):
    return render(request,'page2.html')

@csrf_exempt
def google_api(request):
    file_details = json.loads(request.body)
    Auth().locally_download_files(file_details)

    serializer=DocSerializer(data=file_details,many=True)
    if serializer.is_valid():
        serializer.save()
    return JsonResponse({"status": "Success"})

def render_files(request):
    files_obj=fileDoc.objects.all().order_by('-size')
    return render(request,'page3.html',{'files':files_obj})

def delete_file(request, id):
    item = fileDoc.objects.get(pk=id)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, 'media/'+str(item))
    os.remove(path)
    item.delete()
    return redirect("/files_display")

def clear_user_data_from_app():
    files = fileDoc.objects.all()
    # Removing the files from local databse
    for file in files:
        os.remove(os.path.join(media_dir,file.name))
    # Removing the file models from db
    files.delete()
    globals()['bucket_received'] = None
    globals()['access_id_received'] = None
    globals()['secret_key_received'] = None
    globals()['object_token'] = None


class local_api(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def get(self, request):
        form = DocSerializer()
        return render(request, 'page4.html')

    def post(self, request, *args, **kwargs):
        all_local_files = []
        fs = FileSystemStorage()

        for f in request.FILES.getlist("files"):
            file = fs.save(f.name,f)
            temp = {}
            temp["name"] = file
            temp["url"] = "local_storage"
            temp["size"] = fs.size(file)
            all_local_files.append(temp)

        file_serializer = DocSerializer(data=all_local_files, many=True)
        if file_serializer.is_valid():
            file_serializer.save()
            return redirect("/files_display")
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class get_s3_credentials(APIView):

    def get(self, request):
        return render(request, "page1a.html")
    
    def post(self, request):
        try:
            globals()['bucket_received'] = request.POST.get('bucket')
            globals()['access_id_received'] = request.POST.get('access_id')
            globals()['secret_key_received'] = request.POST.get('secret_key')
            globals()['object_token'] = request.POST.get('object_token')
            print(bucket_received,access_id_received,secret_key_received)
            value='received'
            return redirect("/ds")
        except Exception as e:
            print(e)

def upload_S3(request):
    files_obj=fileDoc.objects.all().order_by('-size')

    if(not len(files_obj)>0):
        return "error" # Has to be proper error page stating no upload
    uploaded_check = False
    try:
        client = boto3.client(
            's3',
            aws_access_key_id=globals()['access_id_received'],
            aws_secret_access_key=globals()['secret_key_received']
        )
        bucket_name = globals()['bucket_received']
        object_name = globals()['object_token']

        if(object_name!=""):
            object_name += "/"

        for file in files_obj:
            client.upload_file(os.path.join(media_dir,file.name), bucket_name, object_name+file.name)
        uploaded_check = True
    except boto3.exceptions.Boto3Error as e:
        # Error Page
        print(e)
    if(uploaded_check):
        clear_user_data_from_app()
        return redirect("/")
    return "error"