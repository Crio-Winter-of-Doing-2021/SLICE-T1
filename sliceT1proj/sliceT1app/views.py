from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from sliceT1app.serializers import DocSerializer
import json
from django.http import JsonResponse
from sliceT1app.models import fileDoc
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import FileSystemStorage
from sliceT1app.scripts import google_drive_gcs, awsS3
import requests, os
###################
'''
Parameters For Credentials for configuration
'''
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
media_dir = os.path.join(base_dir, 'media')

storage_chosen = None

bucket_received=None
object_token=None

access_id_received=None
secret_key_received=None

gcs_client_json_file_name=None
##################

def index(request):
    return render(request,'page0.html')

@csrf_exempt
def google_api(request):
    file_details = json.loads(request.body)
    print(file_details)
    google_drive_gcs.googleAPI().locally_download_files(file_details)
    serializer=DocSerializer(data=file_details,many=True)
    if serializer.is_valid():
        serializer.save()
    return JsonResponse({"status": "Success"})

def render_files(request):
    files_obj=fileDoc.objects.all().order_by('-size')
    return render(request,'page2.html',{'files':files_obj})

def delete_file(request, id):
    item = fileDoc.objects.get(pk=id)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, 'media/'+str(item))
    os.remove(path)
    item.delete()
    return redirect("/files_display")

def clear_user_data_from_app():
    files = fileDoc.objects.all()
    # Removing the files from local database
    for file in files:
        os.remove(os.path.join(media_dir,file.name))

    if(globals()['storage_chosen'] == "gcs"):
        os.remove(os.path.join(media_dir, globals()['gcs_client_json_file_name']))

    for item in os.listdir(media_dir):
        if item.endswith(".json"):
            os.remove(os.path.join(media_dir, item))
    # Removing the files from models
    files.delete()
    globals()['bucket_received'] = None
    globals()['access_id_received'] = None
    globals()['secret_key_received'] = None
    globals()['object_token'] = None
    globals()['storage_chosen'] = None
    globals()['gcs_client_json_file_name'] = None


class local_api(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def get(self, request):
        form = DocSerializer()
        return render(request, 'page3.html')

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
            globals()["storage_chosen"] = "s3"
            return redirect("/files_display") #changed here from ds
        except Exception as e:
            print(e)

class get_gcs_credentials(APIView):

    def get(self, request):
        return render(request, "page1b.html")

    def post(self, request):
        try:
            globals()['bucket_received'] = request.POST.get('bucket')
            globals()['object_token'] = request.POST.get('object_token')
            f = request.FILES.get("files")
            fs = FileSystemStorage()
            file = fs.save(f.name, f)
            globals()["gcs_client_json_file_name"] = file
            globals()["storage_chosen"] = "gcs"
            return redirect("/files_display") #changed here from ds
        except Exception as e:
            # Error goes here
            return "error"

class login_dm(APIView):
    def get(self, request):
        return render(request,'page4.html')

    def post(self, request):
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')
        query = {'email':user_email, 'password':user_password}
        response = requests.post('https://digimocker.herokuapp.com/api/user/login', json=query)
        if response.status_code != 200:
            return HttpResponse(status=response.status_code)
        print("LOGIN: ",response.status_code)
        authToken = str(response.text)
        request.session['token'] = authToken
        request.session['email'] = user_email
        my_headers = {"auth-token": authToken}
        response = requests.get('https://digimocker.herokuapp.com/api/docs', json={"email":user_email},headers=my_headers)
        data=[]
        print("GET FILES: ",response.status_code)

        if(response.text):
            data=json.loads(response.text)
            print(data)
            for jobj in data:
                jobj['fid'] = jobj.pop('_id')

        print("files present: ",data)

        return render(request,'showDigimockerFiles.html',{'files':data})


class register_dm(APIView):
    def get(self, request):
        return render(request,'page5.html')

    def post(self, request):
        user_name=request.POST.get('name')
        user_email=request.POST.get('email')
        user_password=request.POST.get('password')
        query = {"name":user_name,"email":user_email, "password":user_password}
        print(query)
        response = requests.post('https://digimocker.herokuapp.com/api/user/register', json=query)
        print("REGISTER: ",response.status_code)
        if response.status_code != 200:
            return HttpResponse(status=response.status_code)
        return redirect("/login_digimocker")


class upload_to_dm(APIView):
    def get(self, request):
        return render(request,'uploadToDm.html')

    def post(self, request):
        #getting POST data
        my_headers = {'auth-token' : request.session['token']}
        user_email=request.POST.get('email')
        name=request.POST.get('name')
        email=request.POST.get('email')
        identifier=request.POST.get('identifier')
        url=request.POST.get('url')

        #adding file by a POST request to API
        file_data={"name":name,"email":email,"identifier":identifier,"url":url}
        response = requests.post('https://digimocker.herokuapp.com/api/docs/add', json=file_data,headers=my_headers)
        print("UPLOADED_DOC: ",response.text)

        #getting updated list of files by a GET request to API
        response = requests.get('https://digimocker.herokuapp.com/api/docs', json={"email":user_email},headers=my_headers)
        data=json.loads(response.text)
        return render(request,'showDigimockerFiles.html',{'files':data})
        

class upload_from_dm(APIView):
    def post(self, request):
        selected_files=request.POST.getlist('selected')
        data = []
        for i in range(0,len(selected_files)):
            # docType=str(f)
            # authToken=request.session['token']
            # user_email=request.session['email']
            # my_headers={"auth-token":authToken}
            # response = requests.get('https://digimocker.herokuapp.com/api/docs/'+docType, json={"email":user_email},headers=my_headers)
            # data=json.loads(response.text)
            # l=data[0]['url'].split('/')
            # fid=l[5]
            # print("FETCHED_DOC: ",data[0])
            # image_url = "https://drive.google.com/uc?export=download&id="+fid
            file_name, file_url = selected_files[i].split(", ")
            r = requests.get(file_url)
            path = os.path.join(base_dir, 'media/'+str(file_name))
            with open(path,'wb') as f:
                f.write(r.content)
            s = os.stat(path).st_size
            temp = {"name":file_name,"size":s,"url":file_url}
            data.append(temp)
        serializer=DocSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
            return redirect("/files_display")

# Uploading part goes here
def upload_S3(request):
    files_obj=fileDoc.objects.all().order_by('-size')
    if(not len(files_obj)>0):
        return "error" # Has to be proper error page stating no upload
    info = {}
    info['bucket_received'] = globals()['bucket_received']
    info['object_token'] = globals()['object_token']
    info['access_id_received'] = globals()['access_id_received']
    info['secret_key_received'] = globals()['secret_key_received']
    return awsS3.upload(files_obj, info)
    

def upload_gcs(request):
    files_obj = fileDoc.objects.all().order_by('-size')
    if(not len(files_obj)>0):
        return "error" # Has to be proper error page stating no upload
    info = {}
    info['bucket_received'] = globals()['bucket_received']
    info['object_token'] = globals()['object_token']
    info['gcs_client_json_file_name'] = globals()['gcs_client_json_file_name']
    return google_drive_gcs.upload(files_obj, info)


def upload(request):
    storage = globals()['storage_chosen']
    result=[]
    if(storage=="gcs"):
        result = upload_gcs(request)
    elif(storage=="s3"):
        result  = upload_S3(request)

    if(len(result)==0):
        clear_user_data_from_app()
        return render(request,'errors_page.html',{'error':'session out'})

    elif(result[0]==True):
        clear_user_data_from_app()
        return render(request,"page0.html",{'message':True})
    else:
        clear_user_data_from_app()
        return render(request,'errors_page.html',{'error':result[1],'credentials_error':True})