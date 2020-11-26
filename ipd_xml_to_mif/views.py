from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from ipd_xml_to_mif import convertm
from django.conf import settings


# Create your views here.

def index(request):
    template = loader.get_template('index.html')
    data = {"test":"test data"}
    return HttpResponse(template.render(data))

def index_ipd(request):
    template = loader.get_template('ipd/index.html')
    data = {"test":"test data"}
    return HttpResponse(template.render(data))

def request_list(request):
    template = loader.get_template('ipd/request_list/index.html')
    data = {"test":"test data"}
    return HttpResponse(template.render(data, request))  

def ipd_xml_to_mif(request):
    template = loader.get_template('ipd/xml_to_mif/index.html')
    data = {"test":"test data"}
    return HttpResponse(template.render(data, request))    

def ok(request):
    template = loader.get_template('ipd/xml_to_mif/ok.html')
    data = {"test":"test data"}
    return HttpResponse(template.render(data, request))   

def convert(request):
    if request.method == 'POST' and len(request.FILES) == 2:
#    if request.method == 'POST' and request.FILES["zonetogkn"] and request.FILES["territorytogkn"]:
        
        zonetogkn = request.FILES["zonetogkn"]
        territorytogkn = request.FILES["territorytogkn"]
        fs = FileSystemStorage()
        zonetogknfilename = fs.save(zonetogkn.name, zonetogkn)
        territorytogknfilename = fs.save(territorytogkn.name, territorytogkn)
        zonetogkn_url = fs.url(zonetogknfilename)
        territorytogkn_url = fs.url(territorytogknfilename)
        if convertm.checkXML(fs.path(territorytogknfilename), True) and convertm.checkXML(fs.path(zonetogknfilename), False):
            outMIFMID = convertm.writeMIF(convertm.parseXML(fs.path(territorytogknfilename), fs.path(zonetogknfilename)), settings.MEDIA_ROOT)
            return render(request, 'ipd/xml_to_mif/ok.html', 
                {"zonetogkn_url":zonetogkn_url, "territorytogkn_url":territorytogkn_url, "mif_url":fs.url(outMIFMID[0]), "mid_url":fs.url(outMIFMID[1])})
        elif not convertm.checkXML(fs.path(territorytogknfilename), True) and convertm.checkXML(fs.path(zonetogknfilename), False):
            return render(request, 'ipd/xml_to_mif/index.html', 
                {"errors":"Файл TerritoryToGKN_*.xml/MapPlan_*.xml не соответствует XML схеме", "visible":True})
        elif convertm.checkXML(fs.path(territorytogknfilename), True) and not convertm.checkXML(fs.path(zonetogknfilename), False):
            return render(request, 'ipd/xml_to_mif/index.html', 
                {"errors":"Файл ZoneToGKN_*.xml/BoundToGKN_*.xml не соответствует XML схеме", "visible":True})
        else:
            return render(request, 'ipd/xml_to_mif/index.html', 
                {"errors":"Файлы ZoneToGKN_*.xml/BoundToGKN_*.xml и TerritoryToGKN_*.xml/MapPlan_*.xml не соответствуют XML схеме", "visible":True})
    else:
        return render(request, 'ipd/xml_to_mif/index.html', 
                {"errors":"Выберите файлы ZoneToGKN_*.xml и TerritoryToGKN_*.xml (или MapPlan_*.xml)", "visible":True})