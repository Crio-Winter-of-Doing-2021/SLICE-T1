from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
def index(request):
    return render(request,'page1.html')

def selectDataSource(request):
    return render(request,'page2.html')

def google_api(request):
    file_ids = json.loads(request.body.decode("utf-8")).get("files")
    print(file_ids)
