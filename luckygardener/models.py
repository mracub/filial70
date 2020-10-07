from django.db import models

# Create your models here.
class Author(models.Model):
    full_name = models.TextField(blank=True, null=True)
    short_name = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name


class ContestLuckyGardener(models.Model):
    """
    модель для конкурса "Удачный дачник"
    """
    image_ns = models.ImageField(upload_to='luckygardener', blank=True, null=True)#normal size
    image_ss = models.ImageField(upload_to='luckygardener', blank=True, null=True)#small size
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING)
    comment = models.CharField(max_length=1024, blank=True, null=True)


