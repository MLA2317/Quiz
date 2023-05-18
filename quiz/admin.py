from django.contrib import admin
from .models import Question, Category, Option, Result


admin.site.register(Category),
admin.site.register(Result),
admin.site.register(Question),
admin.site.register(Option)