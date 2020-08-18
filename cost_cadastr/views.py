from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, FileResponse
from datetime import datetime, date, time
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from cost_cadastr.models import FilesCost, Docs, Object, CadastrCosts
from django.db import models
from cost_cadastr import xmlparser
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.core.paginator import Paginator
from lxml import etree, objectify



# Create your views here.
def cost_cadastr(request):
    template = loader.get_template('cost_cadastr/index.html')
    docs_count = Docs.objects.all().count()
    docs = Docs.objects.all()
    data = {"docs":docs, "docs_count":docs_count}
    return HttpResponse(template.render(data, request))   

def cost_load_form(request):
    template = loader.get_template('cost_cadastr/load.html')
    data = {}
    return HttpResponse(template.render(data, request))   

def cost_load(request):
    """
    Парсинг XML файлов кадастровой стоимости и загрузка в БД
    """
    if request.method == 'POST':
        startdatestr = '2000-01-01'
        startdate = datetime.strptime(startdatestr, '%Y-%m-%d')
        selected_date = datetime.strptime(request.POST["doc_date"], '%Y-%m-%d')
        if selected_date.date() >= startdate.date() and selected_date.date() <= date.today():
            costdoc = Docs(doc_name=request.POST["doc_name"], doc_number=request.POST["doc_number"], 
                    doc_date=request.POST["doc_date"], doc_author=request.POST["doc_author"])
            costdoc.save()
            date_time_file_load = datetime.now()
            dir_name = xmlparser.create_folders(date_time_file_load)
            fs = FileSystemStorage(location=settings.MEDIA_ROOT + dir_name)
            for f in request.FILES.getlist('cadcost'):
                filename_on_storage = fs.save(f.name, f)
                filepath_on_storage = fs.path(filename_on_storage)
                #file_url_on_storage = fs.url(filepath_on_storage)
                file_url_on_storage = os.path.normpath('/media/' + dir_name + '/' +  filename_on_storage)
                filecost = FilesCost(filename=filename_on_storage, filepath=filepath_on_storage, 
                    urlfile=file_url_on_storage, datetime_load=date_time_file_load)
                filecost.save()
                xmlparser.parsexml(filepath_on_storage, filecost, costdoc)
            return redirect('/cost_cadastr/')
        else:
            return render(request, 'cost_cadastr/load.html', 
                    {"invalid_form_style":"is-invalid", "doc_name_value":request.POST["doc_name"],
                    "doc_number_value":request.POST["doc_number"],
                    "doc_author_value":request.POST["doc_author"]})
    else:
        return render(request, 'cost_cadastr/load.html', 
                {"errors":"Произошда какая-то неведомая херня :-(((", "doc_name_value":request.POST["doc_name"],
                "doc_number_value":request.POST["doc_number"],"doc_date_value":request.POST["doc_date"],
                "doc_author_value":request.POST["doc_author"]})
    


def doc_detail(request):
#    template = loader.get_template('cost_cadastr/docdet.html')
    if request.method == 'POST':
        doc = Docs.objects.filter(pk = request.POST['docid'])
        obj = Object.objects.filter(cost__doc_cost = request.POST['docid'])
#    return HttpResponse(template.render(data, request))   
    elif request.method == 'GET':
        doc = Docs.objects.filter(pk = request.COOKIES['docid'])
        obj = Object.objects.filter(cost__doc_cost = request.COOKIES['docid'])
    paginator = Paginator(obj, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    obj_count = obj.count()
    data = {"doc":doc, "obj":page_obj, "obj_count":obj_count}
    response = render(request, 'cost_cadastr/docdet.html', data)
    if request.method == 'POST':
        response.set_cookie('docid', request.POST['docid'])
    return response


def create_xml(request):
    """
    Формирование XML файлов по схеме interactrealty.
    Формируем XML файлы по схеме, архивируем и отдаем пользователю
    """
    obj = Object.objects.filter(cost__doc_cost = request.COOKIES['docid'])
    doc = Docs.objects.filter(pk = request.COOKIES['docid'])
    object_count = obj.count()
    iter = 1
    iter_full_list = 1
    tempObj = []
    object_count_in_file = int(request.POST['ObjCountSelect'])
    doc_xml = {"document_code":request.POST['DocType'], "document_name":doc[0].doc_name, "document_number":doc[0].doc_number,
        "document_date":doc[0].doc_date, "document_issuer":doc[0].doc_author}
    xmlparser.clearfolder(os.path.normpath(settings.MEDIA_ROOT + '/cost_cadastr/temp/')) #чистим темп, пока временное решение
    for item in obj:
        obj_cost = item.cost.cost
        obj_cost_index = item.cost.upks
        cad_num = item.cad_num
        obj_type = '002001001000'#один для всех, хз это "воля" кодеров ФГИСа
        tempObj.append({"cad_num": cad_num, "obj_type":obj_type, "obj_cost":obj_cost, "obj_cost_index":obj_cost_index, 
            "approvement_date":request.POST['approvement-date-input'], "determination_date":request.POST['determination-date-input']})
        if iter == object_count_in_file:
            xmlparser.create_xml(settings.MEDIA_ROOT + '/cost_cadastr/temp/', tempObj, doc_xml)
            iter = 1
            tempObj.clear()
        elif iter_full_list == object_count:
            xmlparser.create_xml(settings.MEDIA_ROOT + '/cost_cadastr/temp/', tempObj, doc_xml)
            break
        else:          
            iter += 1
        iter_full_list += 1
    zipfile = xmlparser.packxmltozip(os.path.normpath(settings.MEDIA_ROOT + '/cost_cadastr/temp/'))
    out_file = open(zipfile, 'rb')
    response = HttpResponse(out_file, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(zipfile)
    return response

def delete_doc(request):
    """
    удаление документа
    """
    doc = Docs.objects.filter(pk = request.COOKIES['docid'])
    doc.delete()
    return redirect('/cost_cadastr/')

