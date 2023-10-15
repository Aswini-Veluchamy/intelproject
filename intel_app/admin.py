from django.contrib import admin
from .models import KeyMessageTable
from .models import RiskTable

admin.site.register(KeyMessageTable)
admin.site.register(RiskTable)