from lxml import etree
from django.conf import settings
from xml.dom import minidom
import os
from datetime import datetime, date, time
from cost_cadastr.models import CadastrCosts, Object, Docs, FilesCost

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