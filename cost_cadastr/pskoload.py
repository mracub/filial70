from django.conf import settings
import os
from datetime import datetime, date, time
from lxml import etree, objectify
import uuid
import glob
from zipfile import ZipFile
import datetime
import time
import dateutil.parser
from decimal import Decimal
from cost_cadastr import xmlfirload, xmllistcreate
import requests
import shutil
from lxml import etree, objectify

def validateXML(xmlfile):
    """
    проверка на соовтетствие XML-схеме
    """
    try:
        xml_doc = etree.parse(xmlfile)
    except Exception as e:
        raise Exception("Ошибка парсинга XML-файла {0}".format(xmlfile))
    else:
        return True
        xml_schema_filename = os.path.normcase(os.path.join(settings.STATICFILES_DIRS[0], 
                'scheme/ListForRating_v04/', 'ListForRating_v04.xsd '))
        xml_schema_doc = etree.parse(xml_schema_filename)
        xmlschema = etree.XMLSchema(xml_schema_doc)
        if xmlschema.validate(xml_doc):
            return True
        else:
            return False
#--------------------------
def chekfiles(fileName, zuoptionslist, oksoptionslist, loadmifoption):
    """
    проверка файлана условия соответствия критериям выбранных объектов
    """
    try:
        xml_doc = etree.parse(fileName)
    except Exception as e:
        raise Exception("Ошибка парсинга XML-файла {0}".format(fileName))
    else:
        objecttype = xml_doc.xpath('/ListForRating/ListInfo/ObjectsType/ObjectType')[0].text
        #если объект ОКС проверяем на вхождение в список указанных пользователем
        if objecttype in oksoptionslist:
            cadnums = []
            if objecttype == '002001002000':
                buildingNodes = xml_doc.xpath('/ListForRating/Objects/Buildings/Building')
                for building in buildingNodes:
                    cadnums.append(building.get('CadastralNumber'))
                if loadmifoption:
                    xmllistcreate.loadMifMid(os.path.normpath(os.path.dirname(fileName)), cadnums)
            elif objecttype == '002001004000':
                constrNodes = xml_doc.xpath('/ListForRating/Objects/Constructions/Construction')
                for constr in constrNodes:
                    cadnums.append(constr.get('CadastralNumber'))
                if loadmifoption:
                    xmllistcreate.loadMifMid(os.path.normpath(os.path.dirname(fileName)), cadnums)
            elif objecttype == '002001005000':
                unconstrNodes = xml_doc.xpath('/ListForRating/Objects/Uncompleteds/Uncompleted')
                for unconstr in unconstrNodes:
                    cadnums.append(unconstr.get('CadastralNumber'))
                if loadmifoption:
                    xmllistcreate.loadMifMid(os.path.normpath(os.path.dirname(fileName)), cadnums)
            elif objecttype == '002001003000':
                flatsNodes = xml_doc.xpath('/ListForRating/Objects/Flats/Flat')
                for flat in flatsNodes:
                    cadnums.append(flat.get('CadastralNumber'))
            elif objecttype == '002001009000':
                carsNodes = xml_doc.xpath('/ListForRating/Objects/CarParkingSpaces/CarParkingSpace')
                for car in carsNodes:
                    cadnums.append(car.get('CadastralNumber'))
            return len(cadnums)
        #если объект ЗУ
        elif objecttype == '002001001000' and zuoptionslist:
            categories = xml_doc.xpath('//ListForRating/ListInfo/Categories/Category')
            chek_cat = False
            for item in categories:
                if item.text in zuoptionslist:
                    chek_cat = True
            if not chek_cat:
                return False
            else:        
                parcels = xml_doc.xpath('//ListForRating/Objects/Parcels/Parcel')
                count = int(xml_doc.xpath('//ListForRating/ListInfo/Quantity')[0].text)
                for item in parcels:
                    item_category = item.xpath('./Category')[0].text
                    if item_category not in zuoptionslist:
                        item.getparent().remove(item)
                        count -= 1
                if count > 0:
                    xml_doc.xpath('//ListForRating/ListInfo/Quantity')[0].text = str(count)
                    xml_doc.write(fileName, encoding='UTF-8')
                    return count
                else:
                    return False
        else:
            return False
        
#------------------------------------
def convertList(filelist, zuoptionslist, oksoptionslist, loadmifoption):
    """
    переформатирование перечня 
    """
    #распаковываем перечень
    try:
        xml_files_list = xmlfirload.exctractZip(filelist)
    except Exception as e:
        raise Exception("Ошибка распаковки архивного файла")
    else:
        #создадим директорию для загрузки графики
#        if loadmifoption:
#            try:
#                normal_dir_path = os.path.normpath(os.path.dirname(xml_files_list[0]))
#                os.mkdir(os.path.normpath(normal_dir_path))
#            except:
#                raise Exception("Ошибка создания директории для загрузки MIF файлов")
        
        totalobjectscount = 0
        for item in xml_files_list:
            count = chekfiles(item, zuoptionslist, oksoptionslist, loadmifoption)
            if not count:
                os.remove(item)
            else:
                totalobjectscount += count
        out_dir = xmlfirload.createDir(settings.MEDIA_ROOT + '/cost_cadastr/temp')
        file_out = xmllistcreate.packToZIP2(out_dir, os.path.dirname(xml_files_list[0]))
        return totalobjectscount, file_out
        

