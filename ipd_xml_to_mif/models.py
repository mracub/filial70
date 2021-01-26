from django.db import models

# Create your models here.

class RequestDoc(models.Model):
    """
    модель документа
    """
    DATATYPE_CHOOSES = (
        ('ТЗ', 'Территориальная зона'),
        ('ЗОУИТ', 'Зона с особыми условиями использования территорий'),
    )
    STATUS_CHOOSES = (
        ('inwork', 'В работе'),
        ('closed', 'Завершен'),
        ('fail', 'Отозван'),
    )
    docNumber = models.CharField(max_length=64, default=None, blank=True, null=True)#номер документа
    docData = models.DateField(auto_now=False, default=None, blank=True, null=True)#дата документа
    sendAuthor = models.CharField(max_length=64, default=None, blank=True, null=True)#орган направивший
    dateReg = models.DateField(auto_now=False, default=None, blank=True, null=True)#дата регистрации в Филиале
    numberReg = models.CharField(max_length=64, default=None, blank=True, null=True)#номер регистрации в Филиале
    dataType = models.CharField(max_length=8, choices=DATATYPE_CHOOSES)#
    status = models.CharField(max_length=8, choices=STATUS_CHOOSES)#
    dateEnd = models.DateField(auto_now=False, default=None, blank=True, null=True)#датазавершения
    userCreated = models.CharField(max_length=64, default=None, blank=True, null=True)#нужно указывать ID

    def __str__(self):
        return self.docNumber

class Contractor(models.Model):
    """
    исполнитель работ
    """
    contractor = models.CharField(max_length=64, default=None, blank=True, null=True)

    def __str__(self):
        return self.contractor

class RequestAppeal(models.Model):
    """
    модель для обращения
    """
    DATATYPE_CHOOSES = (
        ('ТЗ', 'Территориальная зона'),
        ('ЗОУИТ', 'Зона с особыми условиями использования территорий'),
    )
    pvdNumber = models.CharField(max_length=64, default=None, blank=True, null=True)#дата номера ПВД
    kuvdNumber = models.CharField(max_length=64, default=None, blank=True, null=True)#номер КУВД
    appealNumber = models.CharField(max_length=64, default=None, blank=True, null=True)#номер обращения
    dateCreated = models.DateField(auto_now=False, default=None, blank=True, null=True)#дата регистрации
    dateReglament = models.DateField(auto_now=False, default=None, blank=True, null=True)#дата исполнения по регламенту
    dateClosed = models.DateField(auto_now=False, default=None, blank=True, null=True)#дата фактического завершения(присвоения номера или уведомления)
    dataType = models.CharField(max_length=8, choices=DATATYPE_CHOOSES)#вил объекта
    objectName = models.CharField(max_length=1024, default=None, blank=True, null=True)#наименование объекта
    docName = models.CharField(max_length=1024, default=None, blank=True, null=True)#наименование документа основания
    appealResult = models.CharField(max_length=1024, default=None, blank=True, null=True)#результат рассмотрения обращения
    notification = models.CharField(max_length=1024, default=None, blank=True, null=True)#причины уведомления
    userFinished = models.CharField(max_length=64, default=None, blank=True, null=True)#кто завершил!
    requestdoc = models.ForeignKey(RequestDoc, blank=True, null=True, on_delete=models.DO_NOTHING)#связь с документом
    contractor = models.ForeignKey(Contractor, blank=True, null=True, on_delete=models.DO_NOTHING)#связь с исполнителем работ

    def __str__(self):
        return self.appealNumber