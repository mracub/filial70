from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
from ipd_xml_to_mif import convertm
from django.conf import settings
from django.core.paginator import Paginator
from ipd_xml_to_mif.models import RequestDoc, Contractor, RequestAppeal


# Create your views here.

def index(request):
    template = loader.get_template('index.html')
    data = {"test":"test data"}
    return HttpResponse(template.render(data))

def index_ipd(request):
    template = loader.get_template('ipd/index.html')
    data = {"test":"test data"}
    return HttpResponse(template.render(data))

#----------------------------------------------------------
#Login
#----------------------------------------------------------
def login(request):
    """
    бэкэнд авторизации
    """

#----------------------------------------------------------
#Requests reestr
#----------------------------------------------------------
def request_list(request):
    """
    стартовая страница раздела IPD
    """
    template = loader.get_template('ipd/request_list/index.html')
    if request.method == 'GET':
        docs_count = RequestDoc.objects.all().count()#query count docs
        docs = RequestDoc.objects.all() #query docs
    elif request.method == 'POST':
        docs = RequestDoc.objects.filter(numberReg = request.POST["numberReg"]) #query docs
        docs_count = RequestDoc.objects.filter(numberReg = request.POST["numberReg"]).count()
    paginator = Paginator(docs, 10)
    page_number = request.GET.get('page')
    page_docs = paginator.get_page(page_number)
    data = {"docs":page_docs, "docs_count":docs_count}
    return HttpResponse(template.render(data, request))   

def adddoc(request):
    """
    добавление поступившего документа
    """
    template = loader.get_template('ipd/request_list/createdoc.html')
    data = {"test":"test data"}
    return HttpResponse(template.render(data, request))

#----------------------------------------------------------
#XML to MIF converter
#----------------------------------------------------------
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
        try:
            if 'checkxml' in request.POST:
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
                    outMIFMID = convertm.writeMIF(convertm.parseXML(fs.path(territorytogknfilename), fs.path(zonetogknfilename)), settings.MEDIA_ROOT)
                    return render(request, 'ipd/xml_to_mif/ok.html', 
                        {"zonetogkn_url":zonetogkn_url, "territorytogkn_url":territorytogkn_url, "mif_url":fs.url(outMIFMID[0]), "mid_url":fs.url(outMIFMID[1])})            
        except Exception as e:
                return render(request, 'ipd/xml_to_mif/index.html', 
                        {"errors":"Ошибка: {0}".format(e), "visible":True})
    else:
        return render(request, 'ipd/xml_to_mif/index.html', 
                {"errors":"Выберите файлы ZoneToGKN_*.xml и TerritoryToGKN_*.xml (или MapPlan_*.xml)", "visible":True})