from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, FileResponse
from datetime import datetime, date, time
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from django.db import models
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.core.paginator import Paginator
from luckygardener.models import Author, ContestLuckyGardener



# Create your views here.

def index(request):
    """
    стартовая страница раздела КС
    """
    template = loader.get_template('luckygardener/index.html')
    im = {}
    images = ContestLuckyGardener.objects.all()
    im["images"] = images
    return HttpResponse(template.render(im, request))  