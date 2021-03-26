from lxml import etree
from django.conf import settings
#from xml.dom import minidom
import os
from datetime import datetime, date, time
from cost_cadastr.models import CadastrCosts, Object, Docs, FilesCost
from cost_cadastr.models import ClObject, ClCadNumNum, ClExploitationChar, ClAssignationType, ClAssignationCode
from cost_cadastr.models import ClAssignationBuilding, ClObjectType, ClParenCadastralNumbers, ClElementConstr
from cost_cadastr.models import ClCadCost, ClKeyParam, ClKeyParamTypes, ClLocation, ClLevels
from lxml import etree, objectify
import uuid
import glob
from zipfile import ZipFile
import datetime
import time
import dateutil.parser
from decimal import Decimal

def createDir(dirpath):
    """
    создаем директорию в формате uuid
    """
    uuid_str = str(uuid.uuid1())
    normal_dir_path = os.path.normpath(dirpath + '/' + uuid_str)
    try:
        os.mkdir(os.path.normpath(normal_dir_path))
        return normal_dir_path
    except:
        return False

def exctractZip(filename):
    """
    распаковывает zip архив во временную папку и возвращает список файлов в архиве с путями
    """
    flist = []
    tmpdir = createDir(settings.MEDIA_ROOT + '/cost_cadastr/temp')
    with ZipFile(filename, 'r') as zipObj:
        zipObj.extractall(tmpdir)
        fl = zipObj.namelist()
        for f in fl:
            flist.append(os.path.normpath(tmpdir + '/' + f))
    return flist

def parseXMLprotocol(arch_file):
    """
    парсим файл протокола для выборки:
    1. Периода выгрузки
    2. Имен файлов по типам объектов
    """
    data = {}
    filesinzip = exctractZip(arch_file)
    for f in filesinzip:
        if f.endswith('.xml'):
            #парсим файл протокола
            try:
                xml_doc = etree.parse(f)
                attachfilename = xml_doc.xpath('/Extract/Info/Attach/Name[1]/text()')[0]
                data['dataarchfilename'] = attachfilename
                startDate = xml_doc.xpath('/Extract/Period/Date_Start[1]/text()')[0]
                data['dateStart'] = dateutil.parser.parse(startDate)
                endDate = xml_doc.xpath('/Extract/Period/Date_End[1]/text()')[0]
                data['dateEnd'] = dateutil.parser.parse(endDate)
                buildingsNodes = xml_doc.xpath('/Extract/Files/Groups/Group[@Type="Buildings"]/File_Name')
                if buildingsNodes:
                    buildingsFilesList = []
                    for item in buildingsNodes:
                        buildingsFilesList.append(item.text)
                    data['filesBuildings'] = buildingsFilesList
                else:
                    data['filesBuildings'] = []
                constructionsNodes = xml_doc.xpath('/Extract/Files/Groups/Group[@Type="Constructions"]/File_Name')
                if constructionsNodes:
                    constructionsFilesList = []
                    for item in constructionsNodes:
                        constructionsFilesList.append(item.text)
                    data['filesConstructions'] = constructionsFilesList
                else:
                    data['filesConstructions'] = []
                unconstructionsNodes = xml_doc.xpath('/Extract/Files/Groups/Group[@Type="Uncompleted_Constructions"]/File_Name')
                if unconstructionsNodes:
                    unconstructionsFilesList = []
                    for item in unconstructionsNodes:
                        unconstructionsFilesList.append(item.text)
                    data['filesUncompConstructions'] = unconstructionsFilesList
                else:
                    data['filesUncompConstructions'] = []
                flatsNodes = xml_doc.xpath('/Extract/Files/Groups/Group[@Type="Flats"]/File_Name')
                if flatsNodes:
                    flatsFilesList = []
                    for item in flatsNodes:
                        flatsFilesList.append(item.text)
                    data['filesFlats'] = flatsFilesList
                else:
                    data['filesFlats'] = []
                data['error'] = None
            except:
                data['error'] = 'Ошибка парсинга файла протокола.'
        elif f.endswith('.zip'):
            data['dataarchfilenamewithpath'] = f
    return data

def parseXMLdata(data):
    """
    парсит XML файлы с данными об объектах
    на входе словарь полученный после парсинга протокола
    """
    dataFiles = exctractZip(data['dataarchfilenamewithpath'])
    for f in dataFiles:
        try:
            for filesB in data['filesBuildings']:
                if f.endswith(filesB):
                    with open(f, 'rb') as xml_file:
                        xml_doc = etree.parse(xml_file)
                        buildingNodes = xml_doc.xpath('/GKN2FIR/Package/Buildings/Building')
                        parseXMLobjectNode(buildingNodes, '002001002000', f)
            for filesConstr in data['filesConstructions']:
                if f.endswith(filesConstr):
                    with open(f, 'rb') as xml_file:
                        xml_doc = etree.parse(xml_file)
                        constructionNodes = xml_doc.xpath('/GKN2FIR/Package/Constructions/Construction')
                        parseXMLobjectNode(constructionNodes, '002001004000', f)
            for filesUnConstr in data['filesUncompConstructions']:
                if f.endswith(filesUnConstr):
                    with open(f, 'rb') as xml_file:
                        xml_doc = etree.parse(xml_file)
                        unconstructionNodes = xml_doc.xpath('/GKN2FIR/Package/Uncompleted_Constructions/Uncompleted_Construction')
                        parseXMLobjectNode(unconstructionNodes, '002001005000', f)
            for filesFlat in data['filesFlats']:
                if f.endswith(filesFlat):
                    with open(f, 'rb') as xml_file:
                        xml_doc = etree.parse(xml_file)
                        flatNodes = xml_doc.xpath('/GKN2FIR/Package/Flats/Flat')
                        parseXMLobjectNode(flatNodes, '002001003000', f)     
        except:
            #при возникновении исключений в момент обработки XML файлов пишем в лог имя файла
            #
            logDir = os.path.dirname(f)
            logFile = logDir + '/' + 'filesErrors.log'
            with open(os.path.normpath(logFile), 'a') as mylog:
                mylog.write(os.path.basename(f))
                mylog.write('\n')

def parseXMLobjectNode(xmlNode, objectType, fileName):
    """
    парсинг узла с данными об объекте. Общая функция для всех видов объектов.
    на вход принимает список узлов XML файла и вид объекта
    """
    #пишем в файл имя и время наала обработки обработки
    logDir = os.path.dirname(fileName)
    logFile = logDir + '/' + 'data.log'
    with open(os.path.normpath(logFile), 'a') as mylog:
        now = datetime.datetime.now()
        mylog.write(os.path.basename(fileName) + ' ' + str(len(xmlNode)) + ' ' + now.strftime("%d/%m/%Y %H:%M:%S"))
        mylog.write('\n')
    try:
        for index, item in enumerate(xmlNode):
            ClObjectDict = {}
            ClObjectDict['CadastralNumber'] = item.get('CadastralNumber')
            DateCreated = item.get('DateCreated')
            if DateCreated:
                ClObjectDict['DateCreated'] = dateutil.parser.parse(DateCreated).date()
            else:
                ClObjectDict['DateCreated'] = None
            DateRemoved = item.get('DateRemoved')
            if DateRemoved:
                ClObjectDict['DateRemoved'] = dateutil.parser.parse(DateRemoved).date()
            else:
                ClObjectDict['DateRemoved'] = None
            datecadastralrecord = item.xpath('.//Cadastral_Record/DateRecord')
            if datecadastralrecord:
                daterecord = datecadastralrecord[0].text
            if daterecord:
                ClObjectDict['DateCadastralRecord'] = dateutil.parser.parse(daterecord).date()
            else:
                ClObjectDict['DateCadastralRecord'] = None
            #-----------------------
            #при отсутствии у объекта DateCreated, хотя это нереально, но в Росреестре всё может быть, мы приравниваем
            #DateRecord=DateCadastralRecord
            #-----------------------
            if not ClObjectDict['DateCreated']:
                ClObjectDict['DateCreated'] = ClObjectDict['DateCadastralRecord']
            #кадастровый квартал, для помещений и машино-мест он в теге CadastralNumberKK
            #для остальных объектов в Parent_Object
            cadBlock = item.xpath('.//CadastralNumberKK')
            if cadBlock:
                ClObjectDict['CadastralBlock'] = cadBlock[0].text
            else:
                ClObjectDict['CadastralBlock'] = item.xpath('.//Parent_Object')[0].get('CadastralNumber')
            #----парсим тег Name------------
            nodeName = item.xpath('./Name')
            if nodeName:
                ClObjectDict['Name'] = nodeName[0].text
            else:
                ClObjectDict['Name'] = ''
            #этажность/этаж
            floorsBuilding = item.xpath('./Floors')
            if floorsBuilding:
                ClObjectDict['Floors'] = floorsBuilding[0].get('Floors')
                ClObjectDict['UndergroundFloors'] = floorsBuilding[0].get('Underground_Floors')
            else:
                ClObjectDict['Floors'] = None
                ClObjectDict['UndergroundFloors'] = None
            #площадь
            areaBuilding = item.xpath('./Area')
            if areaBuilding:
                ClObjectDict['Area'] = Decimal(areaBuilding[0].text)
            else:
                ClObjectDict['Area'] = None
            #адрес
            locationNode = item.xpath('./Location')
            if locationNode:
                ClLocationDict = parseXMLlocationNode(locationNode[0])
            else:
                ClLocationDict = {}
            #стоимость
            costNode = item.xpath('./CadastralCost')
            if costNode:
                ClCostDict = parseXMLcostNode(costNode[0])
            else:
                ClCostDict = {}
            #назначение для зданий
            assCodeNode = item.xpath('./Assignation_Code')
            assignationCode = {}
            if assCodeNode:
                assignationCode['assignationBuilding'] = assCodeNode[0].text
            else:
                assignationCode['assignationBuilding'] = None
            #материал стен
            constrElementNode = item.xpath('./Elements_Construct/Material')
            #materialWallCode = ''
            if constrElementNode:
                materialWallCode = constrElementNode[0].get('Wall')
            else:
                materialWallCode = None
            #эксплуатайионные характеристики год ввода/год постройки
            expl = item.xpath('./Exploitation_Char')
            if expl:
                ClExploitationDict = parseXMLexploitNode(expl[0])
            else:
                ClExploitationDict = {}
            #родительские КН для зданий, сооружений и ОНС
            parentCadNode = item.xpath('./Parent_CadastralNumbers')
            parentCadNums = []
            if parentCadNode:
                parentCadNums = parseXMLparentCadnumNode(parentCadNode[0])
            #эта часть сооружения и ОНС
            #назначение в текстовом виде
            assignationNameNode = item.xpath('./Assignation_Name')
            if assignationNameNode:
                ClObjectDict['AssignationConsName'] = assignationNameNode[0].text
            else:
                ClObjectDict['AssignationConsName'] = None
            #основные параметры
            keyParam = []
            keyParamNode = item.xpath('./KeyParameters')
            if keyParamNode:
                keyParam = parseXMLkeyparametersNode(keyParamNode[0])
            #степень готовности для ОНС
            degreeReadiness = item.xpath('./Degree_Readiness')
            if degreeReadiness:
                ClObjectDict['DegreeReadiness'] = degreeReadiness[0].text
            else:
                ClObjectDict['DegreeReadiness'] = None
            #flats
            #assignation flats
            assignationNode = item.xpath('./Assignation')
            if assignationNode:
                assignationCode = parseXMLassignationFlatsNode(assignationNode[0], assignationCode)
            else:
                assignationCode['assignationFlatCode'] = None
                assignationCode['assignationFlatType'] = None
            #расположение на этаже для помещения
            levelNode = item.xpath('./Levels/Level')
            ClLevelsDictsList = parseXMLlevelNode(levelNode)
            #кадастровый номер родителя
            cadastralNumberOKS = item.xpath('./CadastralNumberOKS')
            if cadastralNumberOKS:
                ClObjectDict['cadastralNumberOKS'] = cadastralNumberOKS[0].text
            else:
                ClObjectDict['cadastralNumberOKS'] = None
            #save data
            saveData(ClObjectDict, ClLocationDict, 
                            ClCostDict, assignationCode, keyParam, 
                            materialWallCode, ClExploitationDict, parentCadNums, objectType, ClLevelsDictsList)
#            with open(os.path.normpath(logFile), 'a') as mylog:
#                #now = datetime.datetime.now()
#                mylog.write(ClObjectDict['CadastralNumber'] + ' parse_time: {0}'.format(str(parse_time)) + 
#                    ' save_time: {0}'.format(str(save_time['save_time'])) + ' save_location: {0}'.format(str(save_time['save_time_location'])) +
#                    ' save_obj: {0}'.format(str(save_time['save_time_obj'])) + ' save_parent: {0}'.format(str(save_time['save_time_parent'])) +
#                    ' save_test: {0}'.format(str(save_time['save_time_test'])))
#                mylog.write('\n')
        return True
    except:
        #в лог пишем кадастровый номер объекта при обработке которого возникло исключение
        # надеясь на то, что при чтении кадастрового номера из файла ошибок не возникнет 
        #logDir = os.path.dirname(fileName)
        logFile = logDir + '/' + 'filesDataErrors.log'
        with open(os.path.normpath(logFile), 'a') as mylog:
            mylog.write(os.path.basename(fileName) + ' ' +ClObjectDict['CadastralNumber'] + 
                ' {0} from {1}'.format(index, len(xmlNode)))
            mylog.write('\n')
        return False
#-----------------------------------------
def saveData(ClObjectDict, ClLocationDict, ClCostDict, assCode, keyParam, materialWallCode, 
                 ClExploitationDict, parentCadNums, objectType, ClLevelsDictsList):
    """
    функция сохранения сведений об объекте
    """
    clobject = ClObject.objects.filter(CadastralNumber=ClObjectDict['CadastralNumber'])
    if clobject:
        #обновление
        #обновляем адрес
        locationQuerySet = ClLocation.objects.filter(pk=clobject[0].cllocation_id)
        if ClLocationDict and locationQuerySet:
            locationQuerySet = saveLocationData(ClLocationDict, locationQuerySet).first()
        elif ClLocationDict:
            locationQuerySet = saveLocationData(ClLocationDict)
        else:
            locationQuerySet = None
        #обновляем стоимость
        if ClCostDict:
            costQuerySet = ClCadCost.objects.filter(pk=clobject[0].clcadcost_id)
        else:
            costQuerySet = None
        if ClCostDict and costQuerySet:
            costQuerySet = saveCostData(ClCostDict, costQuerySet).first()
        elif ClCostDict:
            costQuerySet = saveCostData(ClCostDict)
        else:
            costQuerySet = None#это наверное лишнее, если ничего не выбрали в запросе, то значит и обновлять нечего
        #обновляем код назначения здания
        if assCode['assignationBuilding']:
            assignationCodeTemp = ClAssignationBuilding.objects.filter(AssignationBuildingCode=assCode['assignationBuilding'])
        else:
            assignationCodeTemp = None
        if assignationCodeTemp:
            assignationCodeQuerySet=assignationCodeTemp.first()
        else:
            assignationCodeQuerySet = None
        #обновляем код назначения и тип помещения
        if assCode['assignationFlatCode']:
            assignationCodeFlatQuerySet = ClAssignationCode.objects.filter(AssignationFlatCode=assCode['assignationFlatCode'])
        else:
            assignationCodeFlatQuerySet = None
        if assignationCodeFlatQuerySet:
            assignationCodeFlatQuerySet = assignationCodeFlatQuerySet.first()
            #clobject.update(classignationcode=assignationCodeFlatQuerySet.first())
        else:
            #это наверное лишнее, если ничего не выбрали в запросе, то значит и обновлять нечего
            #clobject.update(classignationcode=None)
            pass
        if assCode['assignationFlatType']:
            assignationTypeFlatQuerySet = ClAssignationType.objects.filter(AssignationTypeCode=assCode['assignationFlatType'])
        else:
            assignationTypeFlatQuerySet = None
        if assignationTypeFlatQuerySet:
            assignationTypeFlatQuerySet = assignationTypeFlatQuerySet.first()
            #clobject.update(classignationtype=assignationTypeFlatQuerySet.first())
        else:
            pass
        #обновляем материал стен
        if materialWallCode:
            materialWallCodeTemp = ClElementConstr.objects.filter(ClElementConstrCode=materialWallCode)
        else:
            materialWallCodeTemp = None
        if materialWallCodeTemp:
            materialWallCodeQuerySet = materialWallCodeTemp.first()
        else:
            materialWallCodeQuerySet = None
        #обновляем эксплуатационные характеристики
        if ClExploitationDict:
            exploitationQuerySet = ClExploitationChar.objects.filter(pk=clobject[0].clexploitationchar_id)
        else:
            exploitationQuerySet = None
        if ClExploitationDict and exploitationQuerySet:
            exploitationQuerySet = saveExploitationData(ClExploitationDict, exploitationQuerySet).first()
        elif ClExploitationDict:
            exploitationQuerySet = saveExploitationData(ClExploitationDict)
        else:
            exploitationQuerySet = None
        #обновляем вид объекта
        if objectType == '002001003000' and not assCode['assignationFlatCode'] and not assCode['assignationFlatType']:
            objectTypeQuerySet = ClObjectType.objects.filter(ObjectTypeCode='002001009000')
        else:
            objectTypeQuerySet = ClObjectType.objects.filter(ObjectTypeCode=objectType)
        if objectTypeQuerySet:
            objectTypeQuerySet = objectTypeQuerySet.first()
        else:
            objectTypeQuerySet = None
            #clobject.update(clobjecttype=objectTypeQuerySet)
        #обновляем данные объекта ClObject
        clobject.update(CadastralNumber=ClObjectDict['CadastralNumber'],
            DateCreated=ClObjectDict['DateCreated'],
            DateRemoved=ClObjectDict['DateRemoved'],
            DateCadastralRecord=ClObjectDict['DateCadastralRecord'],
            CadastralBlock=ClObjectDict['CadastralBlock'],
            Name=ClObjectDict['Name'],
            Floors=ClObjectDict['Floors'],
            UndergroundFloors=ClObjectDict['UndergroundFloors'],
            Area=ClObjectDict['Area'],
            AssignationConsName = ClObjectDict['AssignationConsName'],
            DegreeReadiness=ClObjectDict['DegreeReadiness'],
            cllocation=locationQuerySet,
            clobjecttype=objectTypeQuerySet,
            classignationbuilding=assignationCodeQuerySet,
            clexploitationchar=exploitationQuerySet,
            clementconstr=materialWallCodeQuerySet,
            clcadcost=costQuerySet,
            classignationcode=assignationCodeFlatQuerySet,
            classignationtype=assignationTypeFlatQuerySet)
        #уровни
        if objectType == '002001003000' or objectType == '002001009000':
            saveLevels(ClLevelsDictsList, clobject.first())
        #обновляем родительские ЗУ
        if parentCadNums:
            saveParentCadastarlNumbers(parentCadNums, clobject.first())
        #сохранение ключевых параметров для соружений
        if keyParam:
            saveKeyParametersData(keyParam, clobject.first())
        #обновляем связь many to many для помещений
        if objectType == '002001003000' and ClObjectDict['cadastralNumberOKS']:
            cadnumparent = ClObject.objects.filter(CadastralNumber=ClObjectDict['cadastralNumberOKS'])
            cadnumrelation = ClCadNumNum.objects.filter(cad_num_child=clobject[0].pk)
            if cadnumparent and cadnumrelation and not ClObjectDict['DateRemoved']:
                cadnumrelation.update(cad_num_parent=cadnumparent[0], cad_num_child=clobject[0])
            elif cadnumparent and not ClObjectDict['DateRemoved']:
                #create relation
                cadnumrelation = ClCadNumNum(cad_num_parent=cadnumparent[0], cad_num_child=clobject[0])
                cadnumrelation.save()
            elif cadnumrelation and not cadnumparent: #ClObjectDict['DateRemoved'] убрал условие удаление связи с архивным родителем
                cadnumrelation.delete()

    else:
        #создание нового объекта в БД
        #адрес
        if ClLocationDict:
            locationQuerySet = saveLocationData(ClLocationDict)
        else:
            locationQuerySet = None
        #раздел кадастровая стоимость
        if ClCostDict:
            costQuerySet = saveCostData(ClCostDict)
        else:
            costQuerySet = None
        #достаем код назначения для здания из справочной таблицы
        assignationCodeTemp = ClAssignationBuilding.objects.filter(AssignationBuildingCode=assCode['assignationBuilding'])
        if len(assignationCodeTemp):
            assignationCodeQuerySet = assignationCodeTemp[0]
        else:
            assignationCodeQuerySet = None
        #код назначения для помещения
        assignationCodeFlatTemp =  ClAssignationCode.objects.filter(AssignationFlatCode=assCode['assignationFlatCode'])
        if assignationCodeFlatTemp:
            assignationCodeFlatQuerySet = assignationCodeFlatTemp[0]
        else:
            assignationCodeFlatQuerySet = None
        #код вида помещения
        assignationTypeFlatTemp = ClAssignationType.objects.filter(AssignationTypeCode=assCode['assignationFlatType'])
        if assignationTypeFlatTemp:
            assignationTypeFlatQuerySet = assignationTypeFlatTemp[0]
        else:
            assignationTypeFlatQuerySet = None
        #материал стен
        materialWallCodeTemp = ClElementConstr.objects.filter(ClElementConstrCode=materialWallCode)
        if materialWallCodeTemp:
            materialWallCodeQuerySet = materialWallCodeTemp[0]
        else:
            materialWallCodeQuerySet = None
        #вип объекта
        #обновляем вид объекта
        if objectType == '002001003000' and not assCode['assignationFlatCode'] and not assCode['assignationFlatType']:
            objectTypeQuerySet = ClObjectType.objects.filter(ObjectTypeCode='002001009000').first()
        else:
            objectTypeQuerySet = ClObjectType.objects.filter(ObjectTypeCode=objectType).first()
        #эксплуатационные характеристики
        if ClExploitationDict:
            exploitationQuerySet = saveExploitationData(ClExploitationDict)
        else:
            exploitationQuerySet = None
        #сохраняем объект
        objectQuerySet = ClObject(CadastralNumber=ClObjectDict['CadastralNumber'],
                                    DateCreated=ClObjectDict['DateCreated'],
                                    DateRemoved=ClObjectDict['DateRemoved'],
                                    DateCadastralRecord=ClObjectDict['DateCadastralRecord'],
                                    CadastralBlock=ClObjectDict['CadastralBlock'],
                                    Name=ClObjectDict['Name'],
                                    Floors=ClObjectDict['Floors'],
                                    UndergroundFloors=ClObjectDict['UndergroundFloors'],
                                    Area=ClObjectDict['Area'],
                                    DegreeReadiness=ClObjectDict['DegreeReadiness'],
                                    AssignationConsName = ClObjectDict['AssignationConsName'],
                                    cllocation=locationQuerySet,
                                    clobjecttype=objectTypeQuerySet,
                                    classignationbuilding=assignationCodeQuerySet,
                                    clexploitationchar=exploitationQuerySet,
                                    clementconstr=materialWallCodeQuerySet,
                                    clcadcost=costQuerySet,
                                    classignationcode=assignationCodeFlatQuerySet,
                                    classignationtype=assignationTypeFlatQuerySet)
        objectQuerySet.save()
        #уровни
        if objectType == '002001003000' or objectType == '002001009000':
            saveLevels(ClLevelsDictsList, objectQuerySet)
        #формируем и сохраняем список родительских кадастровых номеров для зданий, сооружений и ОНС
        if parentCadNums:
            saveParentCadastarlNumbers(parentCadNums, objectQuerySet)
        #сохранение ключевых параметров для сооружения
        if keyParam:
            saveKeyParametersData(keyParam, objectQuerySet)
        #формируем связь many to many для помещений
        if objectType == '002001003000' and ClObjectDict['cadastralNumberOKS']:
            cadnumparent = ClObject.objects.filter(CadastralNumber=ClObjectDict['cadastralNumberOKS'])
            if cadnumparent and not ClObjectDict['DateRemoved']:
                cadnumrelation = ClCadNumNum(cad_num_parent=cadnumparent[0], cad_num_child=objectQuerySet)
                cadnumrelation.save()
#    save_time['save_time'] = time.time() - save_time_start
    return True
#-----------------------------------------

def saveLevels(ClLevelsDictsList, objectQuerySet=None):
    """
    сохранение уровней
    """
    levels = ClLevels.objects.filter(clobject_id=objectQuerySet.id)
    if levels:
        levels.delete()
    for item in ClLevelsDictsList:
        levelsSet = ClLevels(Number_OnPlan=item['Number_OnPlan'], 
                        LevelNumber=item['LevelNumber'], 
                        LevelType=item['LevelType'],
                        clobject=objectQuerySet)
        levelsSet.save()
#-----------------------------------------
def saveKeyParametersData(keyParam, objectQuerySet=None):
    """
    сохранение ключевых параметров для Сооружений и ОНС
    """
    keyparams = ClKeyParam.objects.filter(clobject_id=objectQuerySet.id)
    if keyparams:
        keyparams.delete()
    for item in keyParam:
        keyParamTypeSet = ClKeyParamTypes.objects.filter(ClKeyParamCode=item['Type'])
        keyParamSet = ClKeyParam(value=float(item['Value']), valuetype=keyParamTypeSet[0], clobject=objectQuerySet)
        keyParamSet.save()

def saveParentCadastarlNumbers(parentCadNums, objectQuerySet=None):
    """
    созданение кадастровых номеров ЗУ являющихся родителями для Зданий, Сооружений и ОНС
    """
    numbers = ClParenCadastralNumbers.objects.filter(clobject_id=objectQuerySet.id)
    if numbers:
        numbers.delete()
        pass
    for cadNum in parentCadNums:
        cadNumSet = ClParenCadastralNumbers(CadastralNumber=cadNum, clobject=objectQuerySet)
        cadNumSet.save()


def saveExploitationData(ClExploitationDict, exploitationQuerySet=None):
    """
    запись сведений о годе ввода/постройки
    """
    exploitationQueryTemp = exploitationQuerySet
    if exploitationQueryTemp:
        exploitationQueryTemp.update(year_build=ClExploitationDict['year_build'],
                                                    year_used=ClExploitationDict['year_used'])
    else:
        exploitationQueryTemp = ClExploitationChar(year_build=ClExploitationDict['year_build'],
                                                    year_used=ClExploitationDict['year_used'])
        exploitationQueryTemp.save()
    return exploitationQueryTemp

def saveCostData(ClCostDict, costQuerySet=None):
    """
    запись сведений о КС
    """
    costQuerySetTemp = costQuerySet
    if ClCostDict['value']:
        costValue = float(ClCostDict['value'])
    else:
        costValue = None
    if costQuerySetTemp:
        costQuerySetTemp.update(value=costValue,
                                    unit=ClCostDict['unit'],
                                    date_entering=ClCostDict['date_entering'],
                                    date_approval=ClCostDict['date_approval'],
                                    date_application=ClCostDict['date_application'],
                                    date_valuation=ClCostDict['date_valuation'])
    else:
        costQuerySetTemp = ClCadCost(value=costValue,
                                    unit=ClCostDict['unit'],
                                    date_entering=ClCostDict['date_entering'],
                                    date_approval=ClCostDict['date_approval'],
                                    date_application=ClCostDict['date_application'],
                                    date_valuation=ClCostDict['date_valuation'])
        costQuerySetTemp.save()
    return costQuerySetTemp

def saveLocationData(ClLocationDict, locationQuerySet=None):
    """
    запись сведений об адресе в БД.
    """
    locationQuerySetTemp = locationQuerySet
    if locationQuerySetTemp:
        locationQuerySetTemp.update(okato=ClLocationDict['okato'],
                                kladr=ClLocationDict['kladr'],
                                postal=ClLocationDict['postal'],
                                region=ClLocationDict['region'],
                                district_type=ClLocationDict['district_type'],
                                district_name=ClLocationDict['district_name'],
                                city_type=ClLocationDict['city_type'],
                                city_name=ClLocationDict['city_name'],
                                locality_type=ClLocationDict['locality_type'],
                                locality_name=ClLocationDict['locality_name'],
                                street_type=ClLocationDict['street_type'],
                                street_name=ClLocationDict['street_name'],
                                home_type=ClLocationDict['home_type'],
                                home_number=ClLocationDict['home_number'],
                                corp_type=ClLocationDict['corp_type'],
                                corp_number=ClLocationDict['corp_number'],
                                str_type=ClLocationDict['str_type'],
                                str_number=ClLocationDict['str_number'],
                                apart_type=ClLocationDict['apart_type'],
                                apart_number=ClLocationDict['apart_number'],
                                note=ClLocationDict['note'])
    else:
        locationQuerySetTemp = ClLocation(okato=ClLocationDict['okato'],
                                kladr=ClLocationDict['kladr'],
                                postal=ClLocationDict['postal'],
                                region=ClLocationDict['region'],
                                district_type=ClLocationDict['district_type'],
                                district_name=ClLocationDict['district_name'],
                                city_type=ClLocationDict['city_type'],
                                city_name=ClLocationDict['city_name'],
                                locality_type=ClLocationDict['locality_type'],
                                locality_name=ClLocationDict['locality_name'],
                                street_type=ClLocationDict['street_type'],
                                street_name=ClLocationDict['street_name'],
                                home_type=ClLocationDict['home_type'],
                                home_number=ClLocationDict['home_number'],
                                corp_type=ClLocationDict['corp_type'],
                                corp_number=ClLocationDict['corp_number'],
                                str_type=ClLocationDict['str_type'],
                                str_number=ClLocationDict['str_number'],
                                apart_type=ClLocationDict['apart_type'],
                                apart_number=ClLocationDict['apart_number'],
                                note=ClLocationDict['note'])
        locationQuerySetTemp.save()
    return locationQuerySetTemp

def parseXMLassignationFlatsNode(assignationNode, assignationCode):
    """
    парсин узла назначения для помещений
    """
    if assignationNode is not None:
        assignationFlatCodeNode = assignationNode.xpath('./AssignationCode')
        if assignationFlatCodeNode:
            assignationCode['assignationFlatCode'] = assignationFlatCodeNode[0].text
        else:
            assignationCode['assignationFlatCode'] = None
        assignationFlatTypeNode = assignationNode.xpath('./AssignationType')
        if assignationFlatTypeNode:
            assignationCode['assignationFlatType'] = assignationFlatTypeNode[0].text
        else:
            assignationCode['assignationFlatType'] = None
    else:
        assignationCode['assignationFlatCode'] = None
        assignationCode['assignationFlatType'] = None
    return assignationCode


def parseXMLparentCadnumNode(parentNode):
    """
    парсим узел Parent_CadastralNumbers - родительские кадастровые номера
    """
    parent = []
    parentCadNums = parentNode.xpath('./Parent_CadastralNumber')
    for num in parentCadNums:
        parent.append(num.get('CadastralNumber'))
    return parent

def parseXMLlevelNode(levelNode):
    """
    парсинг узла level
    """
    level = []
    for item in levelNode:
        ClLevelsDict = {}
        ClLevelsDict['LevelNumber'] = item.get('Number')
        ClLevelsDict['LevelType'] = item.get('Type')
        positionNode = item.xpath('./Position')
        if positionNode:
            ClLevelsDict['Number_OnPlan'] = positionNode[0].get('Number_OnPlan')
        else:
            ClLevelsDict['Number_OnPlan'] = None
        level.append(ClLevelsDict)
    return level

def parseXMLkeyparametersNode(keyNode):
    """
    парсим узел KeyParameters - ключевые характеристики
    """
    keyparam = []
    keyParamNode = keyNode.xpath('./KeyParameter')
    for item in keyParamNode:
        keyparamDict = {'Value':item.get('Value'), 'Type':item.get('Type')}
        keyparam.append(keyparamDict)
    return keyparam


def parseXMLexploitNode(exploitNode):
    """
    парсинг узла Exploitation_Char - эксплуатационные характеристики
    """
    exploit = {}
    yb = exploitNode.get('Year_Built')
    if yb:
        exploit['year_build'] = yb
    else:
        exploit['year_build'] = None
    yu = exploitNode.get('Year_Used')
    if yu:
        exploit['year_used'] = yu
    else:
        exploit['year_used'] = None
    return exploit

def parseXMLcostNode(costNode):
    """
    разбор узла кадастровая стоимость
    """
    cost = {}
    Value = costNode.get('Value')
    if Value:
        cost['value'] = Value
    else:
        cost['value'] = None
    Unit = costNode.get('Unit')
    if Unit:
        cost['unit'] = Unit
    else:
        cost['unit'] = None
    DateEntering= costNode.get('DateEntering')
    if DateEntering:
        cost['date_entering'] = dateutil.parser.parse(DateEntering)
    else:
        cost['date_entering'] = None
    DateApproval = costNode.get('DateApproval')
    if DateApproval:
        cost['date_approval'] = dateutil.parser.parse(DateApproval)
    else:
        cost['date_approval'] = None
    ApplicationDate = costNode.get('ApplicationDate')
    if ApplicationDate:
        cost['date_application'] = dateutil.parser.parse(ApplicationDate)
    else:
        cost['date_application'] = None
    DateValuation =  costNode.get('DateValuation')
    if DateValuation:
        cost['date_valuation'] = dateutil.parser.parse(DateValuation)
    else:
        cost['date_valuation'] = None
    return cost

def parseXMLlocationNode(locationNode):
    """
    разбор узла location, возвращает словарь
    """
    location = {}
    okato = locationNode.xpath('./Code_OKATO')
    if okato:
        location['okato'] = okato[0].text
    else:
        location['okato'] = None
    kladr = locationNode.xpath('./Code_KLADR')
    if kladr:
        location['kladr'] = kladr[0].text
    else:
        location['kladr'] = None
    postal = locationNode.xpath('./Postal_Code')
    if postal:
        location['postal'] = postal[0].text
    else:
        location['postal'] = None
    region = locationNode.xpath('./Region')
    if region:
        location['region'] = region[0].text
    else:
        location['region'] = None
    district = locationNode.xpath('./District')
    if district:
        location['district_type'] = district[0].get('Type')
        location['district_name'] = district[0].get('Name')
    else:
        location['district_type'] = None
        location['district_name'] = None
    city = locationNode.xpath('./City')
    if city:
        location['city_type'] = city[0].get('Type')
        location['city_name'] = city[0].get('Name')
    else:
        location['city_type'] = None
        location['city_name'] = None
    locality = locationNode.xpath('./Locality')
    if locality:
        location['locality_type'] = locality[0].get('Type')
        location['locality_name'] = locality[0].get('Name')
    else:
        location['locality_type'] = None
        location['locality_name'] = None
    street = locationNode.xpath('./Street')
    if street:
        location['street_type'] = street[0].get('Type')
        location['street_name'] = street[0].get('Name')
    else:
        location['street_type'] = None
        location['street_name'] = None
    home = locationNode.xpath('./Level1')
    if home:
        location['home_type'] = home[0].get('Type')
        location['home_number'] = home[0].get('Value')
    else:
        location['home_type'] = None
        location['home_number'] =  None
    corp = locationNode.xpath('./Level2')
    if corp:
        location['corp_type'] = corp[0].get('Type')
        location['corp_number'] = corp[0].get('Value')
    else:
        location['corp_type'] = None
        location['corp_number'] = None
    stroenie = locationNode.xpath('./Level3')
    if stroenie:
        location['str_type'] = stroenie[0].get('Type')
        location['str_number'] = stroenie[0].get('Value')
    else:
        location['str_type'] = None
        location['str_number'] = None
    apart = locationNode.xpath('./Apartment')
    if apart:
        location['apart_type'] = apart[0].get('Type')
        location['apart_number'] = apart[0].get('Value')
    else:
        location['apart_type'] = None
        location['apart_number'] = None
    loc = locationNode.xpath('./Note')
    if loc:
        location['note'] = loc[0].text
    else:
        location['note'] = None
    return location
