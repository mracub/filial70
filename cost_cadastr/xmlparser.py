from lxml import etree
from django.conf import settings
from xml.dom import minidom
import os
from datetime import datetime, date, time
from cost_cadastr.models import CadastrCosts, Object, Docs, FilesCost
from lxml import etree, objectify
import uuid
import glob
from zipfile import ZipFile

class XMLParseError(Exception):
    """
    class exception
    """
    pass

def parsexml(xmlfile, filecost, costdoc):
    try:
        xml_doc = minidom.parse(xmlfile)
        xml_doc_lxml = etree.parse(xmlfile)
        xml_schema_filename_cost = os.path.normcase(os.path.join(settings.STATICFILES_DIRS[0], 
                'scheme/V02_STD_Cadastral_Cost', 'STD_Cadastral_Cost.xsd'))
        xml_schema_doc_cost = etree.parse(xml_schema_filename_cost)
        xmlschema_cost = etree.XMLSchema(xml_schema_doc_cost)
        cost_data = {}
        if xmlschema_cost.validate(xml_doc_lxml):
            cadastral_districts = xml_doc.getElementsByTagNameNS('*', 'Cadastral_Districts')
            for cd in cadastral_districts:
                cadastral_blocks = cd.getElementsByTagNameNS('*', 'Cadastral_Block')
                for cb in cadastral_blocks:
                    cost_data["cad_block"] = cb.getAttribute('CadastralNumber')
                    parcel = cb.getElementsByTagNameNS('*', 'Parcel')
                    for item in parcel:
                        cost_data["cad_num"] = item.getAttribute('CadastralNumber')
                        cost_data["upks"] = float(item.getElementsByTagNameNS('*', 'Specific_CadastralCost')[0].getAttribute('Value'))
                        cost_data["cost"] = float(item.getElementsByTagNameNS('*', 'CadastralCost')[0].getAttribute('Value'))
                        save_cost_data(cost_data, filecost, costdoc)
        else:
            raise XMLParseError("Файл не соответствует XML схеме")
        return True
    except XMLParseError as err:
        return False

def save_cost_data(costdata, filecost, costdoc):
    try:
        cadcost = CadastrCosts(cost=costdata["cost"], upks=costdata["upks"], doc_cost=costdoc)
        cadcost.save()
        obj = Object(cad_num=costdata["cad_num"], cad_num_block=costdata["cad_block"], cost=cadcost, filecost=filecost)
        obj.save()
    except:
        return False
    finally:
        return True
    
def create_folders(dt):
    xml_storage_dir = settings.MEDIA_ROOT + '/cost_cadastr/'
    folder_name = datetime.strftime(dt, "%Y-%m-%d_%H-%M-%S")
    full_path = xml_storage_dir + folder_name
    dir_name = '/cost_cadastr/' + folder_name + '/'
    try:
        os.mkdir(os.path.normpath(full_path))
        return os.path.normpath(dir_name)
    except:
        return False

def create_obj(object):
    """
    функция формирует сведения об объекте в XML
    """
#    objs = objectify.Element("objects")
    obj = objectify.Element("object")
    obj.cad_number = object["cad_num"]
    obj.type = object["obj_type"]
    obj_info = objectify.SubElement(obj, "information_object")
    obj_cost = objectify.SubElement(obj_info, "cost")
    obj_cost.value = object["obj_cost"]
    obj_cost.cost_index = object["obj_cost_index"]
    obj_cost.approvement_date = object["approvement_date"]
    obj_cost.determination_date = object["determination_date"]
    return obj

def create_doc(doc_data):
    """
    функция формирует теге по документу основания в XML документ основания описан статично (пока)
    """
    doc = objectify.Element("document")
    doc.document_code = doc_data["document_code"]
    doc.document_name = doc_data["document_name"]
    doc.document_number = doc_data["document_number"]
    doc.document_date = doc_data["document_date"]
    doc.document_issuer = doc_data["document_issuer"]
    return doc


def create_xml(file_path, object, doc, file_name='70_cad_num_'):
    """
    функция создаёт XML файл
    file_path - путь к выходной папке
    file_name - в качесвте имени файла нужно передать кадастровый номер для простоты идентификации
    object - словарь с описанием объекта и его характеристик
    """  

    xml = '''<?xml version="1.0"?>
    <interact_entry_realty>
    </interact_entry_realty>
    '''
    root = objectify.fromstring(xml)
    guid = str(uuid.uuid1())
    root.set("guid", guid)
    root.set("version", "01")

    objs = objectify.Element("objects")

    for o in object:
        objs.append(create_obj(o))
        
    root.append(objs)
    doc = create_doc(doc)
   
    root.append(doc)

    objectify.deannotate(root)
    etree.cleanup_namespaces(root)
    obj_xml = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    try:
        with open(file_path + 'interact_entry_realty_' + file_name + '_' + guid + '.xml', 'wb') as xml_writer:
            xml_writer.write(obj_xml)
    except IOError:
        pass

def clearfolder(path):
    files = os.listdir(path)
    for f in files:
        os.remove(path + '\\' + f)

def packxmltozip(path):
    zipname = os.path.normpath(path + '//' + '70_cad_cost_' + str(uuid.uuid1()) + '.zip')
    files = glob.glob(os.path.normpath(path) + '\\*.xml')
    os.chdir(path)
    with ZipFile(zipname, 'w') as zipObj:
        for f in files:
            zipObj.write(os.path.basename(f))
    return os.path.normpath(zipname)