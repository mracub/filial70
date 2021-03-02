from django.db import models
from datetime import date

# Create your models here.
#модели для конвертации перечня оцененных объектов полученных из ТОЦИКа

class FileDocs(models.Model):
    filename = models.CharField(max_length=256)
    filepath = models.CharField(max_length=256, default=None)
    urlfile = models.URLField(max_length=1024, default=None)
    datetime_load = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.filename

class Docs(models.Model):
    doc_name = models.CharField(max_length=1024)
    doc_number = models.CharField(max_length=64)
    doc_date = models.DateField(default=date.today)
    doc_author = models.CharField(max_length=256)
    filedocs = models.ForeignKey(FileDocs, on_delete=models.CASCADE, default=None, blank=True, null=True)

    def __str__(self):
        return self.doc_name

class CadastrCosts(models.Model):
    cost = models.FloatField()
    upks = models.FloatField()
    doc_cost = models.ForeignKey(Docs, on_delete=models.CASCADE)

    def __str__(self):
        return self.cost

class FilesCost(models.Model):
    filename = models.CharField(max_length=256)
    filepath = models.CharField(max_length=256, default=None)
    urlfile = models.URLField(max_length=1024, default=None)
    datetime_load = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.filename

class Object(models.Model):
    cad_num = models.CharField(max_length=64)
    cad_num_block = models.CharField(max_length=64, default=None)
    obj_type = models.CharField(max_length=64, default='002001001000')
    cost = models.ForeignKey(CadastrCosts, on_delete=models.CASCADE)
    filecost = models.ForeignKey(FilesCost, on_delete=models.CASCADE)

    def __str_(self):
        return self.cad_num
        
class XmlDocEgrn(models.Model):
    """
    данная модель задумывалась для хранения сформированных файлов, если "отдавать" сформированный архив
    сразу пользователю, то наверное она не нужна
    """
    filename = models.CharField(max_length=256, default=None)
    filepath = models.CharField(max_length=256, default=None)
    urlfile = models.URLField(max_length=1024, default=None)
    datetime_create = models.DateTimeField(auto_now=True)
    docs = models.ForeignKey(Docs, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.filename


#модели для подготовки перечня объектов для направления в ТОЦИК

class ClLocation(models.Model):
    """
    описывает адрес
    """
    okato = models.CharField(max_length=64, default=None, blank=True, null=True)
    kladr = models.CharField(max_length=64, default=None, blank=True, null=True)
    oktmo = models.CharField(max_length=64, default=None, blank=True, null=True)
    postal = models.CharField(max_length=64, default=None, blank=True, null=True)
    region = models.IntegerField()
    district_type = models.CharField(max_length=64, default=None, blank=True, null=True)
    district_name = models.CharField(max_length=256, default=None, blank=True, null=True)
    city_type = models.CharField(max_length=64, default=None, blank=True, null=True)
    city_name = models.CharField(max_length=256, default=None, blank=True, null=True)
    locality_type = models.CharField(max_length=64, default=None, blank=True, null=True)
    locality_name = models.CharField(max_length=256, default=None, blank=True, null=True)
    street_type = models.CharField(max_length=64, default=None, blank=True, null=True)
    street_name = models.CharField(max_length=256, default=None, blank=True, null=True)
    home_type = models.CharField(max_length=64, default=None, blank=True, null=True)
    home_number = models.CharField(max_length=256, default=None, blank=True, null=True)
    corp_type = models.CharField(max_length=64, default=None, blank=True, null=True)
    corp_number = models.CharField(max_length=256, default=None, blank=True, null=True)
    str_type = models.CharField(max_length=64, default=None, blank=True, null=True)
    str_number = models.CharField(max_length=256, default=None, blank=True, null=True)
    apart_type = models.CharField(max_length=64, default=None, blank=True, null=True)
    apart_number = models.CharField(max_length=1024, default=None, blank=True, null=True)
    note = models.CharField(max_length=4000, default=None, blank=True, null=True)

    def __str__(self):
        return self.note


class ClCadCost(models.Model):
    """
    описывает кадастровую стоимость объекта
    """
    value = models.FloatField(default=None, blank=True, null=True)
    unit = models.CharField(max_length=64, default=None, blank=True, null=True)
    date_entering = models.DateField(auto_now=False, default=None, blank=True, null=True)
    date_approval = models.DateField(auto_now=False, default=None, blank=True, null=True)
    date_application = models.DateField(auto_now=False, default=None, blank=True, null=True)
    date_valuation = models.DateField(auto_now=False, default=None, blank=True, null=True)
    doc_num = models.CharField(max_length=64, default=None, blank=True, null=True)
    doc_date = models.DateField(auto_now=False, default=None, blank=True, null=True)
    doc_name = models.CharField(max_length=256, default=None, blank=True, null=True)

    def __str__(self):
        return self.value

class ClElementConstr(models.Model):
    """
    описывает конструктивные элементы(материал стен) объекта
    """
    
    ClElementConstrCode = models.CharField(max_length=12)
    ClElementConstrName = models.CharField(max_length=64)

    def __str__(self):
        return self.ClElementConstrName


class ClObjectType(models.Model):
    """
    справочник типа объекта
    """
    ObjectTypeCode = models.CharField(max_length=12)
    ObjectTypeName = models.CharField(max_length=64)

    def __str__(self):
        return self.ObjectTypeName

    class Meta:
        indexes = [
            models.Index(fields=['ObjectTypeCode',]),
        ]

class ClAssignationBuilding(models.Model):
    """
    справочник назначений зданий
    """
    AssignationBuildingCode = models.CharField(max_length=12)
    AssignationBuildingName = models.CharField(max_length=64)

    def __str__(self):
        return self.AssignationBuildingName

    class Meta:
        indexes = [
            models.Index(fields=['AssignationBuildingCode',]),
        ]

class ClAssignationCode(models.Model):
    """
    справочник назначений помещений
    """
    AssignationFlatCode = models.CharField(max_length=12)
    AssignationFlatName = models.CharField(max_length=64)

    def __str__(self):
        return self.AssignationFlatName

    class Meta:
        indexes = [
            models.Index(fields=['AssignationFlatCode',]),
        ]


class ClAssignationType(models.Model):
    """
    справочник назначений помещений по типу
    """
    AssignationTypeCode = models.CharField(max_length=12)
    AssignationTypeName = models.CharField(max_length=64)

    def __str__(self):
        return self.AssignationTypeName

    class Meta:
        indexes = [
            models.Index(fields=['AssignationTypeCode',]),
        ]

class ClExploitationChar(models.Model):
    """
    эксплуатационные характеристики (год вводаб год постройки)
    """
    year_build = models.CharField(max_length=4, default=None, blank=True, null=True)
    year_used = models.CharField(max_length=4, default=None, blank=True, null=True)

    def __str__(self):
        return self.year_build

class ClListRatingReady(models.Model):
    """
    описывает сформированные перечни 
    """
    file_list_name = models.URLField(max_length=1024, default=None, blank=True, null=True) #file name
    file_list_url = models.URLField(max_length=1024, default=None, blank=True, null=True)#created file link
    date_period_start = models.DateField(auto_now=False) #date start of period upload
    date_period_end = models.DateField(auto_now=False) #date end of period upload
    date_list_create = models.DateField(auto_now=True) #date create list fo rating
    total_objects_count = models.IntegerField()

    def __str_(self):
        return self.file_list_name


class ClObject(models.Model):
    """
    описывает объект
    """
    CadastralNumber = models.CharField(max_length=64)#кадастровый номер
    DateCreated = models.DateField(auto_now=False)#дата внесения в ЕГРН
    DateRemoved = models.DateField(auto_now=False, blank=True, null=True)#дата исключения из ЕГРН
    DateCadastralRecord = models.DateField(auto_now=False, blank=True, null=True)#дата внесения изменений в ЕГРН
    CadastralBlock = models.CharField(max_length=64)#кадастровый квартал
    Name = models.CharField(max_length=4096, blank=True, null=True)#наименование
    AssignationConsName = models.CharField(max_length=1024, blank=True, null=True)
    Floors = models.CharField(max_length=64, blank=True, null=True)
    UndergroundFloors = models.CharField(max_length=64, blank=True, null=True)
    Area = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    #Number_OnPlan = models.CharField(max_length=256, null=True, blank=True)
    #LevelNumber = models.CharField(max_length=64, blank=True, null=True)
    #LevelType = models.CharField(max_length=64, blank=True, null=True)
    DegreeReadiness = models.CharField(max_length=8, blank=True,null=True)
    #keys
    #cllevels = models.ForeignKey(ClLevels, blank=True, null=True, on_delete=models.CASCADE)#уровни
    cllocation = models.ForeignKey(ClLocation, blank=True, null=True, on_delete=models.CASCADE)#адрес
    clobjecttype = models.ForeignKey(ClObjectType, blank=True, null=True, on_delete=models.DO_NOTHING)#тип объекта
    classignationcode = models.ForeignKey(ClAssignationCode, blank=True, null=True, on_delete=models.DO_NOTHING)#код назначения
    classignationtype = models.ForeignKey(ClAssignationType, blank=True, null=True, on_delete=models.DO_NOTHING)#тип назначения
    classignationbuilding = models.ForeignKey(ClAssignationBuilding, blank=True, null=True, on_delete=models.DO_NOTHING)#назначение здания
    clexploitationchar = models.ForeignKey(ClExploitationChar, blank=True, null=True, on_delete=models.DO_NOTHING)#год постройки год ввода
    clementconstr = models.ForeignKey(ClElementConstr, blank=True, null=True, on_delete=models.DO_NOTHING)#конструктивные элементы
    clcadcost = models.ForeignKey(ClCadCost, blank=True, null=True, on_delete=models.DO_NOTHING)#кадастровая стоимость
    cadnumnum = models.ManyToManyField('self', through='ClCadNumNum', symmetrical=False, blank=True)#связь между объектами Здание-Помещения
    cllistratingready = models.ForeignKey(ClListRatingReady, blank=True, null=True, on_delete=models.DO_NOTHING)#связь объекта с выгрузками


    def __str__(self):
        return self.CadastralNumber

    class Meta:
        indexes = [
            models.Index(fields=['CadastralNumber', 'DateCreated', 'DateCadastralRecord',]),
        ]
#--------------
class ClLevels(models.Model):
    """
    описывает уровни для помещений и машиномест
    """
    Number_OnPlan = models.CharField(max_length=256, null=True, blank=True)
    LevelNumber = models.CharField(max_length=64, blank=True, null=True)
    LevelType = models.CharField(max_length=64, blank=True, null=True)
    clobject = models.ForeignKey(ClObject, blank=True, null=True, on_delete=models.DO_NOTHING)

    def __str_(self):
        return self.LevelNumber

    class Meta:
        indexes = [
            models.Index(fields=['LevelType', 'LevelNumber',]),
        ]
#--------------
class ClKeyParamTypes(models.Model):
    """
    справочник видов основного параметра
    """
    ClKeyParamCode = models.CharField(max_length=2)
    ClKeyParamName = models.CharField(max_length=64)

    def __str__(self):
        return self.ClKeyParamName
    
    class Meta:
        indexes = [
            models.Index(fields=['ClKeyParamCode', 'ClKeyParamName',]),
        ]

class ClKeyParam(models.Model):
    """
    описывает основной параметр объекта
    """
    value = models.FloatField()
    valuetype = models.ForeignKey(ClKeyParamTypes, blank=True, null=True, on_delete=models.DO_NOTHING)
    clobject = models.ForeignKey(ClObject, blank=True, null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.value
    
    class Meta:
        indexes = [
            models.Index(fields=['value', 'valuetype',]),
        ]

class ClParenCadastralNumbers(models.Model):
    """
    родительские кадастровые номера для зданий, строений сооружений
    """
    CadastralNumber = models.CharField(max_length=64)#кадастровый номер
    clobject = models.ForeignKey(ClObject, blank=True, null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.CadastralNumber

    class Meta:
        indexes = [
            models.Index(fields=['CadastralNumber', ]),
        ]

class ClCadNumNum(models.Model):
    """
    описывает связи объекта с другими объектами(кадастровыми номерами объектов)
    """
    cad_num_parent = models.ForeignKey(ClObject, related_name='cad_num_parent', on_delete=models.DO_NOTHING)
    cad_num_child = models.ForeignKey(ClObject, related_name='cad_num_child', on_delete=models.DO_NOTHING)
    comment = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['cad_num_parent', 'cad_num_child',]),
        ]

class ClDataList(models.Model):
    """
    описывает периоды загрузки данных
    """
    date_start = models.DateField(auto_now=False)#дата начала периода
    date_end = models.DateField(auto_now=False)#дата конец периода
    date_load = models.DateField(auto_now=True, blank=True, null=True)#дата загрузки
    files_fir = models.URLField(max_length=1024, default=None)
    files_fir_url = models.URLField(max_length=1024, default=None, blank=True, null=True)
    """
    files_oks_new = models.URLField(max_length=1024, default=None)
    files_oks_change = models.URLField(max_length=1024, default=None)
    files_flats_new = models.URLField(max_length=1024, default=None)
    files_flats_change = models.URLField(max_length=1024, default=None)
    files_oks_zu_relations = models.URLField(max_length=1024, default=None)
    files_flats_oks_relations = models.URLField(max_length=1024, default=None)
    """
    clobject = models.ForeignKey(ClObject, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.files_fir

