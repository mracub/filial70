from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

# Create your views here.

def index(request):
    template = loader.get_template('index.html')
    data = {"test":"test data"}
    return HttpResponse(template.render(data))

def ipd_xml_to_mif(request):
    template = loader.get_template('ipd_xml_to_mif\index.html')
    data = {"test":"test data"}
    return HttpResponse(template.render(data))    