"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
# from django.contrib import admin
from django.urls import path, include
from web_project import views

# todo: add urls based on the templates, make sure the url abbr name matches base nav-link url
urlpatterns = [
    # path('admin/', admin.site.urls),
    # path('', views.login_action,),  # TODO
    path('', views.get_ingredient_list_page,),  # TODO
    path('web_project/', include('web_project.urls')),
]
