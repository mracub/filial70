from django.db import models
from datetime import date

# Create your models here.


class Docs(models.Model):
    doc_name = models.CharField(max_length=1024)
    doc_number = models.CharField(max_length=64)
    doc_date = models.DateField(default=date.today)
    doc_author = models.CharField(max_length=256)

    def __str__(self):
        return self.doc_name

class CadastrCosts(models.Model):
    cost = models.FloatField()
    upks = models.FloatField()
    doc_cost = models.ForeignKey(Docs, on_delete=models.DO_NOTHING)

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
    cost = models.ForeignKey(CadastrCosts, on_delete=models.DO_NOTHING)
    filecost = models.ForeignKey(FilesCost, on_delete=models.DO_NOTHING)

    def __str_(self):
        return self.cad_num
        
class Test(models.Model):
    test = models.CharField(max_length=64)