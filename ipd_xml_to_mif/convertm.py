"""
пасрит XML файлы ZoneToGKN и TerritoryToGKN формирую mif/mid файлы по координатам указанным в XML.
Можго парсить много вложенных папок. Файлы mif/mid пишутся в теже директории, где лежат ZoneToGKN и TerritoryToGKN в формате UUID.mif и UUID.mid
"""
from shapely.geometry import Polygon
#from shapely.geometry import Point
import sys
import os
import uuid
from xml.dom import minidom
from lxml import etree
import glob
from django.conf import settings


def parseXML (xmlFileTerr, xmlFileZone):
    """
    парсим XML и формируем массив контуров
    """
    xml_doc_terr = minidom.parse(xmlFileTerr)
    contours = []
    EntitySpatial = xml_doc_terr.getElementsByTagNameNS('*', 'EntitySpatial')
    SpatialElement = EntitySpatial[0].getElementsByTagNameNS('*', 'SpatialElement')
    for sp_item in SpatialElement:
        contour = []
        SpelementUnit = sp_item.getElementsByTagNameNS('*', 'SpelementUnit')
        for sp_unit in SpelementUnit:
            Ordinate = sp_unit.getElementsByTagNameNS('*', 'Ordinate')
            contour.append(str(Ordinate[0].getAttribute('Y') + ' ' + Ordinate[0].getAttribute('X')))
        contours.append(contour)
    xml_doc_zone = minidom.parse(xmlFileZone)
    #здесь два раза парсим один и тот же XML файл разными способами только потому, 
    #что изначально функция писалась с использованием minidom в котором нет возможности валидировать в соответствии с XML схемой
    xml_doc = etree.parse(xmlFileZone)
    xml_schema_filename_zone = os.path.normcase(os.path.join(settings.STATICFILES_DIRS[0], 
                'scheme/ZoneToGKN_v05/ZoneToGKN', 'ZoneToGKN_v05.xsd'))
    xml_schema_doc_zone = etree.parse(xml_schema_filename_zone)
    xmlschema_zone = etree.XMLSchema(xml_schema_doc_zone)
    if xmlschema_zone.validate(xml_doc):
        try:
            newzones = xml_doc_zone.getElementsByTagNameNS('*','NewZones')
            zone = newzones[0].getElementsByTagNameNS('*', 'Zone')
            name_by_doc = zone[0].getElementsByTagNameNS('*', 'CodeZoneDoc')
            zoneName = name_by_doc[0].firstChild.data
        except:
            zoneName = 'no zone name'
    else:
        try:
            newbounds = xml_doc_zone.getElementsByTagNameNS('*','NewBounds')
            newbound = newbounds[0].getElementsByTagNameNS('*', 'NewBound')
            description = newbound[0].getElementsByTagNameNS('*', 'Description')
            zoneName = description[0].firstChild.data
        except:
            zoneName = 'no bound name'
    return contours, zoneName


def listToPolygon(coordList):
    """
    функция принимает на вход список координат и выдает объект типа Polygon
    """
    listCoordinates = []
    for item in coordList:
        coord = item.split()
        coordTuple = (float(coord[0]), float(coord[1]))
        listCoordinates.append(coordTuple)
    polygon = Polygon(listCoordinates)
    return polygon


def writeMIF(contoursList, dir_path_to_write):
    """
    формируем MIF файл маза фака
    """
    guid = str(uuid.uuid1())
    outMifFile = os.path.normcase(dir_path_to_write + '/' + guid + '.mif')
    outMidFile = os.path.normcase(dir_path_to_write + '/' + guid + '.mid')
    file_out_mif = open(outMifFile, 'w', encoding='UTF-8') #
    file_out_mid = open(outMidFile, 'w', encoding='UTF-8') 

    print('Version 300', file=file_out_mif)
    print('Charset "Neutral"', file=file_out_mif)
    print('Delimiter ","', file=file_out_mif)
    print('CoordSys NonEarth Units "m" Bounds (0, 0) (20000000, 20000000)', file=file_out_mif)
    print('Columns 3', file=file_out_mif)
    print('  ID Integer', file=file_out_mif)
    print('  LABEL Char(254)', file=file_out_mif)    
    print('  NOTE Char(254)', file=file_out_mif)
    print('Data\n', file=file_out_mif)
    
    i = 0
    for contour in range(len(contoursList[0])):
        if len(contoursList[0]) > 1 and i < len(contoursList[0]) - 1 and listToPolygon(contoursList[0][i]).intersects(listToPolygon(contoursList[0][i+1])) and contour == i:
            contoursIn = 0
            for c in range(len(contoursList[0])-i):
                if listToPolygon(contoursList[0][i]).intersects(listToPolygon(contoursList[0][c+i])) and c > 0: 
                    contoursIn += 1
            if contoursIn >0:
                print('Region {}'.format(contoursIn+1), file=file_out_mif)
                print(len(contoursList[0][i]), file=file_out_mif)
                for item in contoursList[0][i]:
                    print(item, file=file_out_mif)
                for con in range(contoursIn):
                    print(len(contoursList[0][i+con+1]), file=file_out_mif)
                    for it in contoursList[0][i+con+1]:
                        print(it, file=file_out_mif)
                i += (contoursIn + 1)
        elif contour == i:
            print('Region 1', file=file_out_mif)
            print(len(contoursList[0][contour]), file=file_out_mif)
            for item in contoursList[0][contour]:
                print(item, file=file_out_mif)
            i += 1

    print(',,"{}"'.format(contoursList[1]), file=file_out_mid)
    file_out_mif.close()
    file_out_mid.close()
    return os.path.basename(outMifFile), os.path.basename(outMidFile)

def checkXML(fileXML, typeXML):
    """
    type:
        false - zonetogkn
        true - territory or mapplan
    """
    if typeXML:
        try:
            xml_doc = etree.parse(fileXML)
            xml_schema_filename_terr = os.path.normcase(os.path.join(settings.STATICFILES_DIRS[0], 
                'scheme/TerritoryToGKN_v01/TerritoryToGKN', 'TerritoryToGKN_v01.xsd'))
            xml_schema_filename_map = os.path.normcase(os.path.join(settings.STATICFILES_DIRS[0], 
                'scheme/MapPlan_v01/MapPlan', 'MapPlan_v01.xsd'))
            xml_schema_doc_terr = etree.parse(xml_schema_filename_terr)
            xml_schema_doc_map = etree.parse(xml_schema_filename_map)
            xmlschema_terr = etree.XMLSchema(xml_schema_doc_terr)
            xmlschema_map = etree.XMLSchema(xml_schema_doc_map)
            if xmlschema_terr.validate(xml_doc) or xmlschema_map.validate(xml_doc):
                return True
            else:
                return False
        except:
            return False
    else:
        try:
            xml_doc = etree.parse(fileXML)
            xml_schema_filename_zone = os.path.normcase(os.path.join(settings.STATICFILES_DIRS[0], 
                'scheme/ZoneToGKN_v05/ZoneToGKN', 'ZoneToGKN_v05.xsd'))
            xml_schema_filename_bound = os.path.normcase(os.path.join(settings.STATICFILES_DIRS[0], 
                'scheme/BoundToGKN_v03/BoundToGKN', 'BoundToGKN_v03.xsd'))
            xml_schema_doc_zone = etree.parse(xml_schema_filename_zone)
            xml_schema_doc_bound = etree.parse(xml_schema_filename_bound)
            xmlschema_zone = etree.XMLSchema(xml_schema_doc_zone)
            xmlschema_bound = etree.XMLSchema(xml_schema_doc_bound)
            if xmlschema_zone.validate(xml_doc) or xmlschema_bound.validate(xml_doc):
                return True
            else:
                return False
        except:
            return False
