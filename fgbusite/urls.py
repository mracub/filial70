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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ipd_xml_views.index),
    path('ipd_xml_to_mif/', ipd_xml_views.ipd_xml_to_mif),
    path('ipd_xml_to_mif/convert/', ipd_xml_views.convert),
    path('ipd_xml_to_mif/ok/', ipd_xml_views.ok),
    path('cost_cadastr/', cost_views.cost_cadastr),
    path('cost_cadastr/load/', cost_views.cost_load_form),
    path('cost_cadastr/loadf/', cost_views.cost_load),
    path('cost_cadastr/docdetail/', cost_views.doc_detail),
    path('cost_cadastr/createxml/', cost_views.create_xml),
    path('cost_cadastr/deletedoc/', cost_views.delete_doc),
    path('sheduler/', sheduler_views.index),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)