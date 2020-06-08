from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from datetime import datetime, date, time
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from cost_cadastr.models import FilesCost, Docs, Object, CadastrCosts
from django.db import models
from cost_cadastr import xmlparser
from django.template.loader import render_to_string
from django.shortcuts import redirect


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
    2. Нужо сделать paggination

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
                file_url_on_storage = '/media' + dir_name + filename_on_storage
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
    if request.method == 'POST':
        template = loader.get_template('cost_cadastr/docdet.html')
        doc = Docs.objects.filter(pk = request.POST['docid'])
        obj = Object.objects.filter(cost__doc_cost = request.POST['docid'])
        data = {"doc":doc, "obj":obj}
        return HttpResponse(template.render(data, request))


