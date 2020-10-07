from django.conf import settings
import os
from datetime import datetime, date, time
from cost_cadastr.models import CadastrCosts, Object, Docs, FilesCost
from cost_cadastr.models import ClObject, ClCadNumNum, ClExploitationChar, ClAssignationType, ClAssignationCode
from cost_cadastr.models import ClAssignationBuilding, ClObjectType, ClParenCadastralNumbers, ClElementConstr
from cost_cadastr.models import ClCadCost, ClKeyParam, ClKeyParamTypes, ClLocation, ClLevels, ClListRatingReady
from lxml import etree, objectify
import uuid
import glob
from zipfile import ZipFile
import datetime
import time
import dateutil.parser
from decimal import Decimal
from cost_cadastr import xmlfirload
import requests

def createLocationNode(locationQuerySet):
    """
    создание узла "Адрес"
    """
    location = objectify.Element("Location")
    if locationQuerySet.okato is not None:
        location.OKATO = locationQuerySet.okato
    if locationQuerySet.kladr is not None:
        location.KLADR = locationQuerySet.kladr
    if locationQuerySet.oktmo is not None:
        location.OKTMO = locationQuerySet.oktmo
    if locationQuerySet.postal is not None:
        location.PostalCode = locationQuerySet.postal
    if locationQuerySet.region is not None:
        location.Region = str(locationQuerySet.region)
    if locationQuerySet.district_name is not None:
        location.District = None
        location.District.set("Name", locationQuerySet.district_name)
        if locationQuerySet.district_type is not None:
            location.District.set("Type", locationQuerySet.district_type)
    if locationQuerySet.city_name is not None:
        location.City = None
        location.City.set("Name", locationQuerySet.city_name)
        if locationQuerySet.city_type is not None:
            location.City.set("Type", locationQuerySet.city_type)
    if locationQuerySet.locality_name is not None:
        location.Locality = None
        location.Locality.set("Name", locationQuerySet.locality_name)
        if locationQuerySet.locality_type is not None:
            location.Locality.set("Type", locationQuerySet.locality_type)
    if locationQuerySet.street_name is not None:
        location.Street = None
        location.Street.set("Name", locationQuerySet.street_name)
        if locationQuerySet.street_type is not None:
            location.Street.set("Type", locationQuerySet.street_type)
    if locationQuerySet.home_number is not None:
        location.Level1 = None
        location.Level1.set("Value", locationQuerySet.home_number)
        if locationQuerySet.home_type is not None:
            location.Level1.set("Type", locationQuerySet.home_type)
    if locationQuerySet.corp_number is not None:
        location.Level2 = None
        location.Level2.set("Value", locationQuerySet.corp_number)
        if locationQuerySet.corp_type is not None:
            location.Level2.set("Type", locationQuerySet.corp_type)
    if locationQuerySet.str_number is not None:
        location.Level3 = None
        location.Level3.set("Value", locationQuerySet.str_number)
        if locationQuerySet.str_type is not None:
            location.Level3.set("Type", locationQuerySet.str_type)
    if locationQuerySet.apart_number is not None:
        location.Apartment = None
        location.Apartment.set("Value", locationQuerySet.apart_number)
        if locationQuerySet.apart_type is not None:
            location.Apartment.set("Type", locationQuerySet.apart_type)
    if locationQuerySet.note is not None:
        location.Note = locationQuerySet.note
    return location

def createCostNode(costQuerySet):
    """
    создание узла Стоимость
    """
    cadastralcost = objectify.Element("CadastralCost")
    cadastralcost.set("Value", str(costQuerySet.value))
    cadastralcost.set("Unit", costQuerySet.unit)
    if costQuerySet.date_valuation is not None:
        cadastralcost.DateValuation = costQuerySet.date_valuation.strftime('%Y-%m-%d')
    if costQuerySet.date_entering is not None:
        cadastralcost.DateEntering = costQuerySet.date_entering.strftime('%Y-%m-%d')
    if costQuerySet.date_approval is not None:
        cadastralcost.DateApproval = costQuerySet.date_approval.strftime('%Y-%m-%d')
    if costQuerySet.date_application is not None:
        cadastralcost.ApplicationDate = costQuerySet.date_application.strftime('%Y-%m-%d')
    if costQuerySet.doc_num is not None:
        cadastralcost.DocNumber = costQuerySet.doc_num
    if costQuerySet.doc_date is not None:
        cadastralcost.DocDate = costQuerySet.doc_date.strftime('%Y-%m-%d')
    if costQuerySet.doc_name is not None:
        cadastralcost.DocName = costQuerySet.doc_name
    return cadastralcost

def createParentOKSNode(parentId):
    """
    создание родительского узла для помещений и машиномест
    """
    parentoks = objectify.Element("ParentOKS")
    parentobj = ClObject.objects.filter(pk=parentId).filter(DateRemoved__isnull=True).first()
    if parentobj:
        parentoks.CadastralNumberOKS = parentobj.CadastralNumber
        parentoks.ObjectType = parentobj.clobjecttype.ObjectTypeCode
        if parentobj.classignationbuilding is not None:
            parentoks.AssignationBuilding = parentobj.classignationbuilding.AssignationBuildingCode
        elif parentobj.AssignationConsName is not None:
            parentoks.AssignationName = parentobj.AssignationConsName
        if parentobj.clementconstr:
            elementConstrQuerySet = ClElementConstr.objects.filter(pk=parentobj.clementconstr_id)
            materialWall = objectify.SubElement(parentoks, "ElementsConstruct")
            materialWall.Material = None
            materialWall.Material.set("Wall", elementConstrQuerySet.first().ClElementConstrCode)
        else:
            pass
            #parentoks.ElementsConstruct = None
        parentoks.ExploitationChar = None
        if parentobj.clexploitationchar:
            exploitationCharQuerySet = ClExploitationChar.objects.filter(pk=parentobj.clexploitationchar_id)
            year_build = exploitationCharQuerySet.first().year_build
            if year_build is not None:
                parentoks.ExploitationChar.set("YearBuilt", year_build)
            year_used = exploitationCharQuerySet.first().year_used
            if year_used is not None:
                parentoks.ExploitationChar.set("YearUsed", year_used)
        parentoks.Floors = None
        if parentobj.Floors:
            parentoks.Floors.set("Floors", parentobj.Floors)
        if parentobj.UndergroundFloors is not None:
            parentoks.Floors.set("UndergroundFloors", parentobj.UndergroundFloors)
    return parentoks

def createPositionInObjectNode(objectQuerySet):
    """
    создание узла расположение в строении
    """
    positioninobject = objectify.Element("PositionInObject")
    levels = objectify.SubElement(positioninobject, "Levels")
    levelsQuerySet = ClLevels.objects.filter(clobject_id=objectQuerySet.id)
    if levelsQuerySet:
        for item in levelsQuerySet:
            if item.LevelNumber or item.LevelType:
                level = objectify.SubElement(levels, "Level")
                if item.LevelType:
                    level.set("Type", item.LevelType)
                else:
                    pass
                    #level.set("Type", '')
                if item.LevelNumber:
                    level.set("Number", item.LevelNumber)
                else:
                    pass
                    #level.set("Number", '')
                if item.Number_OnPlan:
                    position = objectify.SubElement(level, "Position")
                    position.set("NumberOnPlan", item.Number_OnPlan)
        return positioninobject
    else:
        return None

def createParentNode(objId):
    """
    формирование узла родительских объектов для Зданий, сооружений и ОНС
    objId = идентификатор объекта
    """
    parentcadastralnumbers = objectify.Element("ParentCadastralNumbers")
    parentKNQuerySet = ClParenCadastralNumbers.objects.filter(clobject_id=objId)
    if parentKNQuerySet:
        for item in parentKNQuerySet:
            cadnum = etree.SubElement(parentcadastralnumbers, "CadastralNumber")
            cadnum._setText(item.CadastralNumber)
    return parentcadastralnumbers
#--------------------------------
def createFlatsCadastralNumbers(relQuerySet):
    """
    создание узла FlatsCadastralNumbers
    """
    flatscadastralnumbers = objectify.Element("FlatsCadastralNumbers")
    for item in relQuerySet:
        if item.cad_num_child.DateRemoved is None and item.cad_num_child.clobjecttype.ObjectTypeCode == '002001003000':
            cadnum = etree.SubElement(flatscadastralnumbers, "CadastralNumber")
            cadnum._setText(item.cad_num_child.CadastralNumber)
    return flatscadastralnumbers
#--------------------------------
def CarParkingSpacesCadastralNumbers(relQuerySet):
    """
    создание узла FlatsCadastralNumbers
    """
    carparkingspaces = objectify.Element("CarParkingSpacesCadastralNumbers")
    for item in relQuerySet:
        if item.cad_num_child.DateRemoved is None and item.cad_num_child.clobjecttype.ObjectTypeCode == '002001009000':
            cadnum = etree.SubElement(carparkingspaces, "CadastralNumber")
            cadnum._setText(item.cad_num_child.CadastralNumber)
    return carparkingspaces
#--------------------------------
def createListInfo(objectsCount, objType):
    """
    формирование узла ListInfo
    """
    guid = str(uuid.uuid1())
    listInfo = objectify.Element("ListInfo")
    listInfo.set("DateForm", datetime.datetime.today().strftime('%Y-%m-%d'))
    listInfo.set("GUID", guid)
    listInfo.Region = '70'
    obj_type = objectify.SubElement(listInfo, "ObjectsType")
    obj_type.ObjectType = objType
    listInfo.Quantity = objectsCount

    return listInfo, guid
#--------------------------
def createKeyParametersNode(keyQuerySet):
    """
    создание узла ключевые параметры
    """
    keyparameters = objectify.Element("KeyParameters")
    for item in keyQuerySet:
        keyparam = etree.SubElement(keyparameters, "KeyParameter")
        keyparam.set("Type", item.valuetype.ClKeyParamCode)
        keyparam.set("Value", str(item.value))
    return keyparameters
#--------------------------
def validateNode(Node, objType, xmlschema):
    """
    валидация узла
    коряво формировать полностью структуру файла для валидации нужного узла, но пока так
    """
    xml = '''<?xml version="1.0"?>
    <ListForRating>
    </ListForRating>
    '''
    root = objectify.fromstring(xml)
    root.set("Version", "04")
    listInfoNode = createListInfo(1, objType)
    root.append(listInfoNode[0])
    objects = objectify.Element("Objects")
    #дальше нужно в зависимости от вида объекта формировать структуру
    if objType == '002001002000':
        obj = objectify.Element('Buildings')
        obj.append(Node)
        objects.append(obj)
    elif objType == '002001003000':
        obj = objectify.Element('Flats')
        obj.append(Node)
        objects.append(obj)
    elif objType == '002001004000':
        obj = objectify.Element('Constructions')
        obj.append(Node)
        objects.append(obj)
    elif objType == '002001005000':
        obj = objectify.Element('Uncompleteds')
        obj.append(Node)
        objects.append(obj)
    elif objType == '002001009000':
        obj = objectify.Element('CarParkingSpaces')
        obj.append(Node)
        objects.append(obj)

    root.append(objects)
    objectify.deannotate(root, xsi_nil=True)
    etree.cleanup_namespaces(root)
    if xmlschema.validate(root):
        return True
    else:
        return False

#--------------------------
def createCarParkingSpace(objectsQuerySet):
    """
    формирование записей о машиноместах
    """
    xml_schema_listforrating = os.path.normcase(os.path.join(settings.STATICFILES_DIRS[0], 
            'scheme/ListForRating_v04', 'ListForRating_v04.xsd'))
    xml_schema_doc = etree.parse(xml_schema_listforrating)
    xmlschema = etree.XMLSchema(xml_schema_doc)
    carparkingspaces_valid = objectify.Element("CarParkingSpaces")
    carparkingspaces_invalid = objectify.Element("CarParkingSpaces")
    valid = 0
    invalid = 0
    for item in objectsQuerySet:
        carparkingspace = objectify.Element("CarParkingSpace")
        carparkingspace.set("DateCreated", item.DateCreated.strftime('%Y-%m-%d'))
        carparkingspace.set("CadastralNumber", item.CadastralNumber)
        carparkingspace.CadastralBlock = item.CadastralBlock
        carparkingspace.ObjectType = '002001009000' #можно и так, если для каждого вида объекта своя функция
        parentOKSQuerySet = ClCadNumNum.objects.filter(cad_num_child_id=item.id).first().cad_num_parent
        if parentOKSQuerySet:
            carparkingspace.append(createParentOKSNode(parentOKSQuerySet.id))
        carparkingspace.Area = str(item.Area)
        #position
        position = createPositionInObjectNode(item)
        if position:
            carparkingspace.append(position)
        #create location Node
        if item.cllocation is not None:
            locationQuerySet = ClLocation.objects.filter(pk=item.cllocation_id).first()
            carparkingspace.append(createLocationNode(locationQuerySet))
        else:
            pass
            #carparkingspace.Location = None
        #create Cost node
        if item.clcadcost is not None:
            costQuerySet = ClCadCost.objects.filter(pk=item.clcadcost_id).first()
            carparkingspace.append(createCostNode(costQuerySet))
        else:
            pass
            #carparkingspace.CadastralCost = None
        if validateNode(carparkingspace, '002001009000', xmlschema):
            carparkingspaces_valid.append(carparkingspace)
            valid += 1
        else:
            carparkingspaces_invalid.append(carparkingspace)
            invalid += 1
    return carparkingspaces_valid, carparkingspaces_invalid, valid, invalid

#--------------------------
def createFlat(objectsQuerySet):
    """
    формирование записей о зданиях
    """
    xml_schema_listforrating = os.path.normcase(os.path.join(settings.STATICFILES_DIRS[0], 
            'scheme/ListForRating_v04', 'ListForRating_v04.xsd'))
    xml_schema_doc = etree.parse(xml_schema_listforrating)
    xmlschema = etree.XMLSchema(xml_schema_doc)
    flats_valid = objectify.Element("Flats")
    flats_invalid = objectify.Element("Flats")
    valid = 0
    invalid = 0
    for item in objectsQuerySet:
        flat = objectify.Element("Flat")
        flat.set("DateCreated", item.DateCreated.strftime('%Y-%m-%d'))
        flat.set("CadastralNumber", item.CadastralNumber)
        flat.CadastralBlock = item.CadastralBlock
        flat.ObjectType = '002001003000' #можно и так, если для каждого вида объекта своя функция
        parentOKS = ClCadNumNum.objects.filter(cad_num_child_id=item.id).first()
        if parentOKS:
            parentOKSID = parentOKS.cad_num_parent_id
            flat.append(createParentOKSNode(parentOKSID))
        flat.Name = item.Name
        assignation = objectify.SubElement(flat, "Assignation")
        if item.classignationcode is not None:
            assignation.AssignationCode = ClAssignationCode.objects.filter(pk=item.classignationcode_id).first().AssignationFlatCode
        if item.classignationtype is not None:
            assignation.AssignationType = ClAssignationType.objects.filter(pk=item.classignationtype_id).first().AssignationTypeCode
        flat.Area = str(item.Area)
        #position
        position = createPositionInObjectNode(item)
        if position:
            flat.append(position)
        #create location Node
        if item.cllocation is not None:
            locationQuerySet = ClLocation.objects.filter(pk=item.cllocation_id).first()
            flat.append(createLocationNode(locationQuerySet))
        else:
            pass
            #flat.Location = None
        #create Cost node
        if item.clcadcost is not None:
            costQuerySet = ClCadCost.objects.filter(pk=item.clcadcost_id).first()
            flat.append(createCostNode(costQuerySet))
        else:
            pass
            #flat.CadastralCost = None
        if validateNode(flat, '002001003000', xmlschema):
            flats_valid.append(flat)
            valid += 1
        else:
            flats_invalid.append(flat)
            invalid += 1
    return flats_valid, flats_invalid, valid, invalid
#--------------------------
def createUncompletedConstructions(objectsQuerySet):
    """
    формирование записей об объектах незавершенного строительства
    """
    xml_schema_listforrating = os.path.normcase(os.path.join(settings.STATICFILES_DIRS[0], 
            'scheme/ListForRating_v04', 'ListForRating_v04.xsd'))
    xml_schema_doc = etree.parse(xml_schema_listforrating)
    xmlschema = etree.XMLSchema(xml_schema_doc)
    uncompleteds_valid = objectify.Element("Uncompleteds")
    uncompleteds_invalid = objectify.Element("Uncompleteds")
    valid = 0
    invalid = 0
    for item in objectsQuerySet:
        uncompleted = objectify.Element("Uncompleted")
        uncompleted.set("DateCreated", item.DateCreated.strftime('%Y-%m-%d'))
        uncompleted.set("CadastralNumber", item.CadastralNumber)
        uncompleted.CadastralBlock = item.CadastralBlock
        parentNode = createParentNode(item.id)
        if parentNode is not None:
            uncompleted.append(parentNode)
        #construction.Name = item.Name
        uncompleted.ObjectType = '002001005000' #можно и так, если для каждого вида объекта своя функция
        uncompleted.AssignationName = item.AssignationConsName
        #key parameters
        keyParamQuerySet = ClKeyParam.objects.filter(clobject_id=item.id)
        if keyParamQuerySet is not None:
            uncompleted.append(createKeyParametersNode(keyParamQuerySet))
        #create location Node
        if item.cllocation is not None:
            locationQuerySet = ClLocation.objects.filter(pk=item.cllocation_id).first()
            uncompleted.append(createLocationNode(locationQuerySet))
        else:
            pass
            #uncompleted.Location = None
        #create Cost node
        if item.clcadcost is not None:
            costQuerySet = ClCadCost.objects.filter(pk=item.clcadcost_id).first()
            uncompleted.append(createCostNode(costQuerySet))
        else:
            pass
            #uncompleted.CadastralCost = None
        uncompleted.DegreeReadiness = item.DegreeReadiness
        if validateNode(uncompleted, '002001005000', xmlschema):
            uncompleteds_valid.append(uncompleted)
            valid += 1
        else:
            uncompleteds_invalid.append(uncompleted)
            invalid += 1
    return uncompleteds_valid, uncompleteds_invalid, valid, invalid

#--------------------------
def createConstructions(objectsQuerySet):
    """
    формирование записей о сооружениях
    """
    xml_schema_listforrating = os.path.normcase(os.path.join(settings.STATICFILES_DIRS[0], 
            'scheme/ListForRating_v04', 'ListForRating_v04.xsd'))
    xml_schema_doc = etree.parse(xml_schema_listforrating)
    xmlschema = etree.XMLSchema(xml_schema_doc)
    constructions_valid = objectify.Element("Constructions")
    constructions_invalid = objectify.Element("Constructions")
    valid = 0
    invalid = 0
    for item in objectsQuerySet:
        construction = objectify.Element("Construction")
        construction.set("DateCreated", item.DateCreated.strftime('%Y-%m-%d'))
        construction.set("CadastralNumber", item.CadastralNumber)
        construction.CadastralBlock = item.CadastralBlock
        parentNode = createParentNode(item.id)
        if parentNode:
            construction.append(parentNode)
        construction.Name = item.Name
        construction.ObjectType = '002001004000' #можно и так, если для каждого вида объекта своя функция
        construction.AssignationName = item.AssignationConsName
        construction.ExploitationChar = None
        if item.clexploitationchar is not None:
            exploitationCharQuerySet = ClExploitationChar.objects.filter(pk=item.clexploitationchar_id)
            year_build = exploitationCharQuerySet.first().year_build
            if year_build is not None:
                construction.ExploitationChar.set("YearBuilt", year_build)
            year_used = exploitationCharQuerySet.first().year_used
            if year_used is not None:
                construction.ExploitationChar.set("YearUsed", year_used)
        construction.Floors = None
        if item.Floors is not None:
            construction.Floors.set("Floors", item.Floors)
        if item.UndergroundFloors is not None:
            construction.Floors.set("UndergroundFloors", item.UndergroundFloors)
        #key parameters
        keyParamQuerySet = ClKeyParam.objects.filter(clobject_id=item.id)
        if keyParamQuerySet is not None:
            construction.append(createKeyParametersNode(keyParamQuerySet))
        #create location Node
        if item.cllocation is not None:
            locationQuerySet = ClLocation.objects.filter(pk=item.cllocation_id).first()
            construction.append(createLocationNode(locationQuerySet))
        else:
            pass
            #construction.Location = None
        #create Cost node
        if item.clcadcost is not None:
            costQuerySet = ClCadCost.objects.filter(pk=item.clcadcost_id).first()
            construction.append(createCostNode(costQuerySet))
        else:
            pass
            #construction.CadastralCost = None
        #add flats and parkings
        relQuerySet = ClCadNumNum.objects.filter(pk__in=item.cad_num_parent.all())
        if relQuerySet:
            flatsChild = createFlatsCadastralNumbers(relQuerySet)
            if flatsChild:
                construction.append(createFlatsCadastralNumbers(relQuerySet))
            carplacesChild = CarParkingSpacesCadastralNumbers(relQuerySet)
            if carplacesChild:
                construction.append(CarParkingSpacesCadastralNumbers(relQuerySet))
        #------
        if validateNode(construction, '002001004000', xmlschema):
            constructions_valid.append(construction)
            valid += 1
        else:
            constructions_invalid.append(construction)
            invalid += 1
    return constructions_valid, constructions_invalid, valid, invalid
#--------------------------

def createBuilding(objectsQuerySet):
    """
    формирование записей о зданиях
    """
    xml_schema_listforrating = os.path.normcase(os.path.join(settings.STATICFILES_DIRS[0], 
            'scheme/ListForRating_v04', 'ListForRating_v04.xsd'))
    xml_schema_doc = etree.parse(xml_schema_listforrating)
    xmlschema = etree.XMLSchema(xml_schema_doc)
    buildings_valid = objectify.Element("Buildings")
    buildings_invalid = objectify.Element("Buildings")
    valid = 0
    invalid = 0
    for item in objectsQuerySet:
        building = objectify.Element("Building")
        building.set("DateCreated", item.DateCreated.strftime('%Y-%m-%d'))
        building.set("CadastralNumber", item.CadastralNumber)
        building.CadastralBlock = item.CadastralBlock
        parentNode = createParentNode(item.id)
        if parentNode:
            building.append(parentNode)
        building.Name = item.Name
        building.ObjectType = '002001002000' #можно и так, если для каждого вида объекта своя функция
        
        if item.classignationbuilding:
            assignationBuildingQuerySet = ClAssignationBuilding.objects.filter(pk=item.classignationbuilding_id)
            building.AssignationBuilding = assignationBuildingQuerySet.first().AssignationBuildingCode
        else:
            pass#возможно здесь будет лучше добавить пустой закрытый тег
        if item.clementconstr:
            elementConstrQuerySet = ClElementConstr.objects.filter(pk=item.clementconstr_id)
            materialWall = objectify.SubElement(building, "ElementsConstruct")
            materialWall.Material = None
            materialWall.Material.set("Wall", elementConstrQuerySet.first().ClElementConstrCode)
        else:
            pass
            #building.ElementsConstruct = None
        building.ExploitationChar = None
        if item.clexploitationchar:
            exploitationCharQuerySet = ClExploitationChar.objects.filter(pk=item.clexploitationchar_id)
            year_build = exploitationCharQuerySet.first().year_build
            if year_build is not None:
                building.ExploitationChar.set("YearBuilt", year_build)
            year_used = exploitationCharQuerySet.first().year_used
            if year_used is not None:
                building.ExploitationChar.set("YearUsed", year_used)
        building.Floors = None
        if item.Floors:
            building.Floors.set("Floors", item.Floors)
        if item.UndergroundFloors is not None:
            building.Floors.set("UndergroundFloors", item.UndergroundFloors)
        building.Area = item.Area
        #create location Node
        if item.cllocation:
            locationQuerySet = ClLocation.objects.filter(pk=item.cllocation_id).first()
            building.append(createLocationNode(locationQuerySet))
        else:
            pass
            #building.Location = None
        #create Cost node
        if item.clcadcost:
            costQuerySet = ClCadCost.objects.filter(pk=item.clcadcost_id).first()
            building.append(createCostNode(costQuerySet))
        else:
            pass
            #building.CadastralCost = None
        #create FlatsCadastralNumbers node
        #------
        relQuerySet = ClCadNumNum.objects.filter(pk__in=item.cad_num_parent.all())
        if relQuerySet:
            flatsChild = createFlatsCadastralNumbers(relQuerySet)
            if flatsChild:
                building.append(createFlatsCadastralNumbers(relQuerySet))
            carplacesChild = CarParkingSpacesCadastralNumbers(relQuerySet)
            if carplacesChild:
                building.append(CarParkingSpacesCadastralNumbers(relQuerySet))
        #------
        if validateNode(building, '002001002000', xmlschema):
            buildings_valid.append(building)
            valid += 1
        else:
            buildings_invalid.append(building)
            invalid += 1
    return buildings_valid, buildings_invalid, valid, invalid
#------------------------------

def createXML(objectsQuerySet, objType, tmpFilesDir, correction_flag=None):
    """
    создание XML файла
    objectsQuerySet = выборка объектов
    objType = вид объекта
    tmpFilesDir = путь к временной папке куда будем писать XML файлы
    """
    xml = '''<?xml version="1.0"?>
    <ListForRating>
    </ListForRating>
    '''
    objects = objectify.Element("Objects")
    obj = []
    filelist = []
    #дальше нужно в зависимости от вида объекта формировать структуру
    if objType == '002001002000':
        obj = createBuilding(objectsQuerySet)
    #    objects.append(obj[0])
    elif objType == '002001003000':
        obj = createFlat(objectsQuerySet)
    #    objects.append(obj[0])#здесь добавляем только валидные объекты
    elif objType == '002001004000':
        obj = createConstructions(objectsQuerySet)
    #    objects.append(obj[0])
    elif objType == '002001005000':
        obj = createUncompletedConstructions(objectsQuerySet)
    #    objects.append(obj[0])
    elif objType == '002001009000':
        obj = createCarParkingSpace(objectsQuerySet)
    objects.append(obj[0])
    #формирование арсположения на этаже для помещений вынести в отдельную функцию
    #
    root = objectify.fromstring(xml)
    root.set("Version", "04")
    listInfoNode = createListInfo(obj[2], objType)
    root.append(listInfoNode[0])
    root.append(objects)
    objectify.deannotate(root, xsi_nil=True)
    etree.cleanup_namespaces(root)
    obj_xml = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')
    if correction_flag:
        fileName = os.path.normpath(tmpFilesDir + '/' + 'ListInfo_K_'  + listInfoNode[1] + '.xml')
    else:
        fileName = os.path.normpath(tmpFilesDir + '/' + 'ListInfo_'  + listInfoNode[1] + '.xml')
    try:
        with open(fileName, 'wb') as xml_writer:
            xml_writer.write(obj_xml)
        filelist.append(fileName)
    except:
        pass
    if obj[1]:
        root_invalid = objectify.fromstring(xml)
        root_invalid.set("Version", "04")
        listInfoNode_invalid = createListInfo(obj[3], objType)
        root_invalid.append(listInfoNode_invalid[0])
        objects_invalid = objectify.Element("Objects")
        objects_invalid.append(obj[1])
        root_invalid.append(objects_invalid)
        objectify.deannotate(root_invalid, xsi_nil=True)
        etree.cleanup_namespaces(root_invalid)
        obj_xml_invalid = etree.tostring(root_invalid, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        if correction_flag:
            fileName = os.path.normpath(tmpFilesDir + '/' + 'ListInfo_INVALID_K_'  + listInfoNode_invalid[1] + '.xml')
        else:
            fileName = os.path.normpath(tmpFilesDir + '/' + 'ListInfo_INVALID_'  + listInfoNode_invalid[1] + '.xml')
        try:
            with open(fileName, 'wb') as xml_writer:
                xml_writer.write(obj_xml_invalid)
            filelist.append(fileName)
        except:
            pass
    return filelist

#------------------------------------------------
def listTolist(listDest, listSource):
    """
    херово когда логику приходится менять уже вконце
    """
    for item in listSource:
        listDest.append(item)
    return listDest
#------------------------------------------------
def packToZIP(outdir, filesList):
    """
    упаковка полученных в формате XML перечней в архив
    """
    guid = str(uuid.uuid1())
    fileZip = os.path.join(outdir, 'ListInfo_' + guid + '.zip')
    with ZipFile(fileZip, 'w') as zipobj:
        for f in filesList:
            zipobj.write(f, os.path.basename(f))
    return fileZip
#------------------------------------------------
def selectCadNums(objListCreated, objListChanged):
    """
    формирование списка КН объектов по которым нужно загрузить графическую часть
    """
    cadNums = []
    objListQuerySetCreated = objListCreated.filter(clobjecttype__ObjectTypeCode__in=['002001002000', '002001004000', '002001005000'])
    for item in objListQuerySetCreated:
        cadNums.append(item.CadastralNumber)
    objListQuerySetChanged = objListChanged.filter(clobjecttype__ObjectTypeCode__in=['002001002000', '002001004000', '002001005000'])
    for item in objListQuerySetChanged:
        cadNums.append(item.CadastralNumber)
    return cadNums
#------------------------------------------------
def loadMifMid(tmpFilesDir, cadNums):
    """
    загруза MIF/MID файлов
    """
    graph = os.path.normpath(tmpFilesDir + '/graphics')
    try:
        os.mkdir(graph)
    except:
        pass
    urltmpl = 'http://popd-geoapi-balancer-01.prod.egrn/api/v1/mif_export/realty?kn='
    for kn in cadNums:
        url = urltmpl + kn.replace(':', '%3A')
        savePath = os.path.normpath(graph + '/' + kn.replace(':', '_') + '.zip')
        try:
            r = requests.get(url)
            r.raise_for_status()
        except Exception as err:
            pass
        else:
            with open(savePath, 'wb') as f:
                f.write(r.content)
#------------------------------------------------
def createListForRating(dateStart, dateEnd, objCount):
    """
    формирование перечня для оценки
    dateStart - дата начала периода выгрузки перечня (включительно)
    dateEnd - дата окончания периода выгрузки перечня (включительно)
    objCount - количество объектов в одном XML - файле, пока не используем
    """
    objListCreated = ClObject.objects.filter(DateCreated__range=[datetime.datetime.strptime(dateStart, "%Y-%m-%d").date(), 
                                                                datetime.datetime.strptime(dateEnd, "%Y-%m-%d").date()]).filter(DateRemoved__isnull=True)
    objListChanged = ClObject.objects.filter(DateCadastralRecord__range=[datetime.datetime.strptime(dateStart, "%Y-%m-%d").date(), 
                                                                datetime.datetime.strptime(dateEnd, "%Y-%m-%d").date()]).exclude(
                                                                    DateCreated__range=[datetime.datetime.strptime(dateStart, "%Y-%m-%d").date(), 
                                                                    datetime.datetime.strptime(dateEnd, "%Y-%m-%d").date()]).filter(DateRemoved__isnull=True)
    #сразу в выборке исключить объекты без назначения для зданий, сооружений, помещений и без площади для
    #зданий, помещений и машиномест, также исключить снятые с учета объекты
    tmpFilesDir = xmlfirload.createDir(settings.MEDIA_ROOT + '/cost_cadastr/temp/')
    listFiles = []
    #формируем перечень зданий (постановка)
    #здесь нужна проверка на то, что в выборке действительно есть объекты, чтобы не формировать пустые файлы
    objListQuerySet = objListCreated.filter(clobjecttype__ObjectTypeCode='002001002000')
    if objListQuerySet:
        listSource = createXML(objListQuerySet, '002001002000', tmpFilesDir)
        listTolist(listFiles, listSource)
    #формируем перечень зданий (изменения)
    objListQuerySet = objListChanged.filter(clobjecttype__ObjectTypeCode='002001002000')
    if objListQuerySet:
        listSource = createXML(objListQuerySet, '002001002000', tmpFilesDir, True)
        listTolist(listFiles, listSource)
    #формируем перечень сооружений (постановка)
    objListQuerySet = objListCreated.filter(clobjecttype__ObjectTypeCode='002001004000')
    if objListQuerySet:
        listSource = createXML(objListQuerySet, '002001004000', tmpFilesDir)
        listTolist(listFiles, listSource)
    #формируем перечень сооружений (изменения)
    objListQuerySet = objListChanged.filter(clobjecttype__ObjectTypeCode='002001004000')
    if objListQuerySet:
        listSource = createXML(objListQuerySet, '002001004000', tmpFilesDir, True)
        listTolist(listFiles, listSource)
    #формируем перечень ОНС (постановка)
    objListQuerySet = objListCreated.filter(clobjecttype__ObjectTypeCode='002001005000')
    if objListQuerySet:
        listSource = createXML(objListQuerySet, '002001005000', tmpFilesDir)
        listTolist(listFiles, listSource)
    #формируем перечень ОНС (изменения)
    objListQuerySet = objListChanged.filter(clobjecttype__ObjectTypeCode='002001005000')
    if objListQuerySet:
        listSource = createXML(objListQuerySet, '002001005000', tmpFilesDir, True)
        listTolist(listFiles, listSource)
    #формируем перечень помещений (постановка)
    objListQuerySet = objListCreated.filter(clobjecttype__ObjectTypeCode='002001003000')
    if objListQuerySet:
        listSource = createXML(objListQuerySet, '002001003000', tmpFilesDir)
        listTolist(listFiles, listSource)
    #формируем перечень помещений (изменения)
    objListQuerySet = objListChanged.filter(clobjecttype__ObjectTypeCode='002001003000')
    if objListQuerySet:
        listSource = createXML(objListQuerySet, '002001003000', tmpFilesDir, True)
        listTolist(listFiles, listSource)
    #формируем перечень машино-мест (постановка)
    objListQuerySet = objListCreated.filter(clobjecttype__ObjectTypeCode='002001009000')
    if objListQuerySet:
        listSource = createXML(objListQuerySet, '002001009000', tmpFilesDir)
        listTolist(listFiles, listSource)
    #формируем перечень машиномест (изменения)
    objListQuerySet = objListChanged.filter(clobjecttype__ObjectTypeCode='002001009000')
    if objListQuerySet:
        listSource = createXML(objListQuerySet, '002001009000', tmpFilesDir, True)
        listTolist(listFiles, listSource)
    #загрузка графической части перечня
    cadNums = selectCadNums(objListCreated, objListChanged)
    loadMifMid(tmpFilesDir, cadNums)
    #архивирование перечня
    outdir = xmlfirload.createDir(settings.MEDIA_ROOT + '/cost_cadastr/data/list_rating_out/')
    if listFiles:
        listfileZip = packToZIP(outdir, listFiles)
        file_url = '/media' + listfileZip.replace(settings.MEDIA_ROOT, '').replace('\\', '/')
        listfileZipName = os.path.basename(listfileZip)
    else:
        listfileZipName = None
        file_url = None
    #запись данных о перечне в БД
    listratingready = ClListRatingReady(file_list_name=listfileZipName,
                                        file_list_url=file_url,
                                        date_period_start=datetime.datetime.strptime(dateStart, "%Y-%m-%d").date(),
                                        date_period_end=datetime.datetime.strptime(dateEnd, "%Y-%m-%d").date(),
                                        #date_list_create=,
                                        total_objects_count=objListCreated.count() + objListChanged.count())
    listratingready.save()
    #записать в таблицу сформированных файлов
    return True