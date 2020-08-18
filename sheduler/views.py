from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from ipd_xml_to_mif import convertm
from django.conf import settings

# Create your views here.
def index(request):
    template = loader.get_template('sheduler/index.html')
    data = {"test":"test data"}
    return HttpResponse(template.render(data))