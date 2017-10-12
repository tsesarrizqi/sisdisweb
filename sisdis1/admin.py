from django.contrib import admin

# Register your models here.
from .models import CountReq, Nasabah

admin.site.register(CountReq)
admin.site.register(Nasabah)
