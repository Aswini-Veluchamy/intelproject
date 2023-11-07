from django.contrib import admin
from .models import KeyMessageTable
from .models import RiskTable
from .models import KeyProgramMetricTable
from .models import DetailsMessageTable

admin.site.register(KeyMessageTable)
admin.site.register(RiskTable)
admin.site.register(KeyProgramMetricTable)
admin.site.register(DetailsMessageTable)
