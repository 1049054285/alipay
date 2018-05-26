from django.conf.urls import url
from django.contrib import admin
from app01 import views
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^page1/', views.page1),
    url(r'^page2/', views.page2),
]
