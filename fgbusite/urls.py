"""fgbusite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ipd_xml_to_mif import views as ipd_xml_views
from cost_cadastr import views as cost_views
from sheduler import views as sheduler_views
from django.conf import settings
from django.conf.urls.static import static
from luckygardener import views as luckygardener_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ipd_xml_views.index),
    path('ipd/', ipd_xml_views.index_ipd),
    path('ipd/login/', ipd_xml_views.login),
    path('ipd/request_list/', ipd_xml_views.request_list),
    path('ipd/request_list/adddoc/', ipd_xml_views.adddoc),
    path('ipd/xml_to_mif/', ipd_xml_views.ipd_xml_to_mif),
    path('ipd/xml_to_mif/convert/', ipd_xml_views.convert),
    path('ipd/xml_to_mif/ok/', ipd_xml_views.ok),
    path('cost_cadastr/cc/', cost_views.cost_cadastr),
    path('cost_cadastr/', cost_views.cost_index),
    path('cost_cadastr/load/', cost_views.cost_load_form),
    path('cost_cadastr/loadf/', cost_views.cost_load),
    path('cost_cadastr/editdoc/', cost_views.editdoc),
    path('cost_cadastr/editsave/', cost_views.editsave),
    path('cost_cadastr/docdetail/', cost_views.doc_detail),
    path('cost_cadastr/createxml/', cost_views.create_xml),
    path('cost_cadastr/deletedoc/', cost_views.delete_doc),
    path('cost_cadastr/search/', cost_views.search),
    path('cost_cadastr/cl/', cost_views.cl_index),
    path('cost_cadastr/cl/load/', cost_views.cl_load_form),
    path('cost_cadastr/cl/loadf/', cost_views.cl_load_file),
    path('cost_cadastr/cl/createdlist/', cost_views.cl_create_list),
    path('cost_cadastr/psko/', cost_views.psko_index),
    path('cost_cadastr/psko/loadf/', cost_views.psko_load_file),
    path('luckygardener/', luckygardener_views.index),
    path('sheduler/', sheduler_views.index),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)