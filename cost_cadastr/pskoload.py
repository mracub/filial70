from django.conf import settings
import os
from datetime import datetime, date, time
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
import shutil