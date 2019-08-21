# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import PersonalizeModel

class PersonalizeModelAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'model_arn', 'model_type', 'model_sort_order')

admin.site.register(PersonalizeModel, PersonalizeModelAdmin)
