from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, FileResponse
from datetime import datetime, date, time
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from cost_cadastr.models import FilesCost, Docs, Object, CadastrCosts, FileDocs
from cost_cadastr.models import ClDataList, ClObject, ClElementConstr, ClCadCost, ClKeyParam, ClCadNumNum, ClLocation, ClListRatingReady
from django.db import models
from cost_cadastr import xmlparser
from cost_cadastr import xmlfirload
from cost_cadastr import xmllistcreate
from cost_cadastr import pskoload
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.core.paginator import Paginator
from lxml import etree, objectify
import dateutil.parser


# Create your views here.
def psko_index(request):
    """
    view для раздела загрузки перечня сформированного в ПСКО
    """
    template = loader.get_template('cost_cadastr/psko/index.html')
    data = {}
    return HttpResponse(template.render(data, request))  
#-----------------------------
def psko_load_file(request):
    """
    обработка файла перечня ПСКО
    """
    template = loader.get_template('cost_cadastr/psko/index.html')
    data = {}
    if request.method == 'POST':
        dir_name = xmlfirload.createDir(os.path.normpath(settings.MEDIA_ROOT + '/cost_cadastr/temp/'))
        if dir_name:
            fs = FileSystemStorage(location=dir_name)
            filelist = request.FILES['file_psko']
            filename_on_storage = fs.save(filelist.name, filelist)
            filepath_on_storage = fs.path(filename_on_storage)
            zuoptionslist = request.POST.getlist('zuoptions')
            oksoptionslist = request.POST.getlist('oksoptions')
            if 'loadmif' in request.POST:
                loadmifoption = True
            else:
                loadmifoption = False
            try:
                result = pskoload.convertList( filepath_on_storage, zuoptionslist, oksoptionslist, loadmifoption)
                data['count'] = result[0]
                fstorage = FileSystemStorage(location=os.path.dirname(result[1]))
                file_url_on_storage = os.path.normpath('/media/cost_cadastr/temp/' + 
                    os.path.basename(fstorage.base_location) + '/' +  os.path.basename(result[1]))
                data['link'] = file_url_on_storage
                data['link_name'] = 'Скачать готовый перечень'
                data['datecreate'] = result[2]
            except Exception as e:
                data['errors'] = e
        else:
            pass
    return HttpResponse(template.render(data, request))  
        
#-----------------------------
def cost_index(request):
    """
    стартовая страница раздела КС
    """
    template = loader.get_template('cost_cadastr/index.html')
    data = {}
    return HttpResponse(template.render(data, request))  

def cl_index(request):
    """
    стартовая страница раздела загрузки сведений ФИР
    """
    relevance = ClDataList.objects.latest('date_end').date_end
    cldatalist = ClDataList.objects.all()
    paginator = Paginator(cldatalist, 15)
    page_number = request.GET.get('page')
    page_cldatalist = paginator.get_page(page_number)
    cldatalist_count = cldatalist.count()
    current_date = datetime.today()#.strftime('%Y-%m-%d')
    data = {"cldatalist":page_cldatalist, "cldatalist_count":cldatalist_count, "current_date":current_date, "relevance":relevance}
    response = render(request, 'cost_cadastr/listcost/index.html', data)
    return response

def cl_load_form(request):
    """
    раздел загрузки файлов содержащих характеристики объектов необходимые для формирования перечней
    """
    template = loader.get_template('cost_cadastr/listcost/load.html')
    data = {}
    return HttpResponse(template.render(data, request))   

def cl_load_file(request):
    """
    загрузка файлов ФИР в БД
    """
    error = []
    error_log_url = []
    if request.method == 'POST':
        dir_name = xmlfirload.createDir(os.path.normpath(settings.MEDIA_ROOT + '/cost_cadastr/data/fir_data_in/'))
        if dir_name:
            date_time_file_load = datetime.now()
            fs = FileSystemStorage(location=dir_name)
            for f in request.FILES.getlist('files_fir'):
                filename_on_storage = fs.save(f.name, f)
                filepath_on_storage = fs.path(filename_on_storage)
                file_url = dir_name.replace(settings.MEDIA_ROOT, '').replace('\\', '/') + '/' + filename_on_storage
                file_url = '/media' + file_url
                #парсим файл протокола и пишем данные в БД
                file_protocol_data = xmlfirload.parseXMLprotocol(filepath_on_storage)
                if not file_protocol_data['error']:
                    cldatalist = ClDataList(date_start=file_protocol_data['dateStart'], date_end=file_protocol_data['dateEnd'], 
                        date_load=date_time_file_load, files_fir=filepath_on_storage, files_fir_url=file_url)
                    cldatalist.save()
                    logerror = xmlfirload.parseXMLdata(file_protocol_data)
                    if logerror:
                        error_log_url_str = logerror.replace(settings.MEDIA_ROOT, '').replace('\\', '/')
                        error_log_url.append('/media' + error_log_url_str)
                        error.append('При загрузке сведений по одному или нескольким объектам возникла ошибка, см. лог файл {0}'.format(os.path.normpath(logerror)))
                else:
                    error.append('Ошибка парсинга файла протокола, проверьте корректность загружаемых сведений')
        else:
            error = 'Ошибка сохранения файла'
    else:
        pass
    relevance = ClDataList.objects.latest('date_end').date_end
    cldatalist = ClDataList.objects.all()
    paginator = Paginator(cldatalist, 15)
    page_number = request.GET.get('page')
    page_cldatalist = paginator.get_page(page_number)
    cldatalist_count = cldatalist.count()
    current_date = datetime.today()#.strftime('%Y-%m-%d')
    errors = zip(error, error_log_url)
    data = {"cldatalist":page_cldatalist, "cldatalist_count":cldatalist_count, "current_date":current_date, "relevance":relevance, "errors":errors}
    response = render(request, 'cost_cadastr/listcost/index.html', data)
    return response

def cl_create_list(request):
    """
    формирование перечня для оценки
    """
    current_date = datetime.today()#.strftime('%Y-%m-%d')
    relevance = ClDataList.objects.latest('date_end').date_end
    if request.method == 'POST':
        #здесь вызов функции по формированию перечня в реквесте нужные параметры
        dateStart = request.POST["list_date_start"]
        dateEnd = request.POST["list_date_end"]
        objCount = request.POST["ObjCountSelect"]
        if "createKNlist" in request.POST:
            cadNumList = request.POST["cadnum"].split(",")
        else:
            cadNumList = None
        if xmllistcreate.createListForRating(dateStart, dateEnd, objCount, cadNumList): 
            pass
        else:
            #data["error"] = "Ошибка формирования перечня"
            pass
        listFiles = ClListRatingReady.objects.all()
        paginator = Paginator(listFiles, 15)
        page_number = request.GET.get('page')
        page_listFiles = paginator.get_page(page_number)
        listFiles_count = listFiles.count()
        data = {"listFiles":page_listFiles, "listFiles_count":listFiles_count, "current_date":current_date, "relevance":relevance}
    elif request.method == 'GET':
        listFiles = ClListRatingReady.objects.all()
        paginator = Paginator(listFiles, 15)
        page_number = request.GET.get('page')
        page_listFiles = paginator.get_page(page_number)
        listFiles_count = listFiles.count()
        data = {"listFiles":page_listFiles, "listFiles_count":listFiles_count, "current_date":current_date, "relevance":relevance}
        #data = {"error":"undefined error, request method is not POST"}
    response = render(request, 'cost_cadastr/listcost/lists.html', data)
    return response


def cost_cadastr(request):
    """
    стартовая страница раздела загрузка сведений о КС
    """
    template = loader.get_template('cost_cadastr/filescost/index.html')
    docs_count = Docs.objects.all().count()
    docs = Docs.objects.all().order_by('doc_date', 'doc_number').reverse()
    paginator = Paginator(docs, 15)
    page_number = request.GET.get('page')
    page_docs = paginator.get_page(page_number)
    data = {"docs":page_docs, "docs_count":docs_count}
    return HttpResponse(template.render(data, request))   

def cost_load_form(request):
    """
    раздел загрузки файлов с КС поступивших от ТОЦИК
    """
    template = loader.get_template('cost_cadastr/filescost/load.html')
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
            date_time_file_load = datetime.now()
            dir_name = xmlparser.create_folders(date_time_file_load)
            fs = FileSystemStorage(location=settings.MEDIA_ROOT + dir_name)
            #------------docs cost load--------
            if 'cadcostdoc' in request.FILES:
                cadcostdoc = request.FILES['cadcostdoc']
                filename_on_storage = fs.save(cadcostdoc.name, cadcostdoc)
                filepath_on_storage = fs.path(filename_on_storage)
                file_url_on_storage = os.path.normpath('/media/' + dir_name + '/' +  filename_on_storage)
            #----------------------------------
                fdocs = FileDocs(filename=filename_on_storage, filepath=filepath_on_storage,
                        urlfile=file_url_on_storage, datetime_load=date_time_file_load)
                fdocs.save()
            else:
                fdocs = None
            costdoc = Docs(doc_name=request.POST["doc_name"], doc_number=request.POST["doc_number"], 
                    doc_date=request.POST["doc_date"], doc_author=request.POST["doc_author"],
                    filedocs=fdocs)
            costdoc.save()
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
            return render(request, 'cost_cadastr/filescost/load.html', 
                    {"invalid_form_style":"is-invalid", "doc_name_value":request.POST["doc_name"],
                    "doc_number_value":request.POST["doc_number"],
                    "doc_author_value":request.POST["doc_author"]})
    else:
        return render(request, 'cost_cadastr/filescost/load.html', 
                {"errors":"Произошда какая-то неведомая херня :-(((", "doc_name_value":request.POST["doc_name"],
                "doc_number_value":request.POST["doc_number"],"doc_date_value":request.POST["doc_date"],
                "doc_author_value":request.POST["doc_author"]})
    
#---------------------------------
def editsave(request):
    """
    сохранение документа после редактирования
    """
    obj = Object.objects.filter(cost__doc_cost = request.COOKIES['docid'])
    doc = Docs.objects.filter(pk = request.COOKIES['docid'])
    if doc[0].filedocs:
        fdocs = FileDocs.objects.filter(pk = doc[0].filedocs.id)
    else:
        fdocs = None
    if request.method == 'POST':
        startdatestr = '2000-01-01'
        startdate = datetime.strptime(startdatestr, '%Y-%m-%d')
        selected_date = datetime.strptime(request.POST["doc_date"], '%Y-%m-%d')
        if selected_date.date() >= startdate.date() and selected_date.date() <= date.today():
            date_time_file_load = datetime.now()
            #------------docs cost load--------
            if 'cadcostdoc' in request.FILES:
                if obj[0].filecost:
                    dir_path = os.path.dirname(obj[0].filecost.filepath)
                    fs = FileSystemStorage(os.path.normpath(dir_path + '/'))
                    dir_name = dir_path.split('media')[1]
                else:
                    dir_name = xmlparser.create_folders(date_time_file_load)
                    fs = FileSystemStorage(location=settings.MEDIA_ROOT + dir_name)
                cadcostdoc = request.FILES['cadcostdoc']
                filename_on_storage = fs.save(cadcostdoc.name, cadcostdoc)
                filepath_on_storage = fs.path(filename_on_storage)
                file_url_on_storage = os.path.normpath('/media/' + dir_name + '/' +  filename_on_storage)
            #----------------------------------
                if fdocs:
                    fdocs.update(filename=filename_on_storage, filepath=filepath_on_storage,
                        urlfile=file_url_on_storage, datetime_load=date_time_file_load)
                    fdocs = fdocs.first()
                else:
                    fdocs = FileDocs(filename=filename_on_storage, filepath=filepath_on_storage,
                        urlfile=file_url_on_storage, datetime_load=date_time_file_load)
                    fdocs.save()
                doc.update(doc_name=request.POST["doc_name"], doc_number=request.POST["doc_number"], 
                        doc_date=dateutil.parser.parse(request.POST["doc_date"]), doc_author=request.POST["doc_author"],
                        filedocs=fdocs)
            else:
                doc.update(doc_name=request.POST["doc_name"], doc_number=request.POST["doc_number"], 
                        doc_date=dateutil.parser.parse(request.POST["doc_date"]), doc_author=request.POST["doc_author"])                
            return redirect('/cost_cadastr/')
        else:
            return render(request, 'cost_cadastr/filescost/load.html', 
                    {"invalid_form_style":"is-invalid", "doc_name_value":request.POST["doc_name"],
                    "doc_number_value":request.POST["doc_number"],
                    "doc_author_value":request.POST["doc_author"]})
    else:
        return render(request, 'cost_cadastr/filescost/load.html', 
                {"errors":"Произошда какая-то неведомая херня :-(((", "doc_name_value":request.POST["doc_name"],
                "doc_number_value":request.POST["doc_number"],"doc_date_value":request.POST["doc_date"],
                "doc_author_value":request.POST["doc_author"]})
#---------------------------------
def search(requests):
    """
    поиск объекта
    """
    if requests.method == 'POST':
        cadnum = requests.POST['cadnum']
        obj = Object.objects.filter(cad_num = cadnum)
    elif requests.method == 'GET':
        cadnum = requests.COOKIES['cadnum']
        obj = Object.objects.filter(cad_num = cadnum)
    paginator = Paginator(obj, 15)
    page_number = requests.GET.get('page')
    page_obj = paginator.get_page(page_number)
    data = {"obj":page_obj, "cadnum":cadnum, "obj_count":obj.count()}
    response = render(requests, 'cost_cadastr/filescost/search.html', data)
    if requests.method == 'POST':
        response.set_cookie('cadnum', cadnum)
    return response

    #необходимо реализовать поиск объекта и вывод результатов
#---------------------------------
def doc_detail(request):
    """
    детальная информация об объектах и КС поступивших с актом КС от ТОЦИК
    """
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
    response = render(request, 'cost_cadastr/filescost/docdet.html', data)
    if request.method == 'POST':
        response.set_cookie('docid', request.POST['docid'])
    return response

#---------------------------------------------
def editdoc(request):
    """
    редактирование документа
    """
    obj = Object.objects.filter(cost__doc_cost = request.COOKIES['docid'])
    doc = Docs.objects.filter(pk = request.COOKIES['docid'])
    data = {"doc_name_value":doc[0].doc_name, "doc_number_value":doc[0].doc_number,
            "doc_date_value":doc[0].doc_date, "doc_author_value":doc[0].doc_author}
    if doc[0].filedocs:
        data["doc_image"] = doc[0].filedocs.filepath
    else:
        data["doc_image"] = None
    response = render(request, 'cost_cadastr/filescost/docedit.html', data)
    return response
#---------------------------------------------
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

