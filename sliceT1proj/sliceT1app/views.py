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

# Create your views here.
def index(request):
    return render(request,'page1.html')

def selectDataSource(request):
    return render(request,'page2.html')


class google_api(APIView):
    def post(self, request):
        file_details = json.loads(request.body)
        serializer=DocSerializer(data=file_details,many=True)
        if serializer.is_valid():
            serializer.save()
        return JsonResponse({"status": "Success"})

def render_files(request):
    files_obj=fileDoc.objects.all().order_by('-size')
    return render(request,'page3.html',{'files':files_obj})

def delete_file(request, id):
    item = fileDoc.objects.get(pk=id)
    item.delete()
    files_obj=fileDoc.objects.all().order_by('-size')
    return render(request,'page3.html',{'files':files_obj})

class local_api(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        form = DocSerializer()
        return render(request, 'page4.html')

    def post(self, request, *args, **kwargs):
        all_local_files = []
        fs = FileSystemStorage()
        for f in request.FILES.getlist("files"):
            # file = fs.save(f.name, f)
            # the fileurl variable now contains the url to the file. This can be used to serve the file when needed. 
            # fileurl = fs.url(file)
            # print(fileurl)
            # print(fs.get_valid_name)
            temp = {}
            temp["name"] = f.name
            temp["url"] = "local_storage"
            temp["size"] = f.size
            temp["file"] = f
            all_local_files.append(temp)
        file_serializer = DocSerializer(data=all_local_files, many=True)
        if file_serializer.is_valid():
            file_serializer.save()

            files_obj=fileDoc.objects.all().order_by('-size')
            return render(request,'page3.html',{'files':files_obj})
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)