from django.contrib import admin
from .models import Question, Category, Option, Result


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


class OptionInlineAdmin(admin.TabularInline):
    model = Option
    readonly_fields = ('id', )
    extra = 0


@admin.register(Question)
class QuestionsAdmin(admin.ModelAdmin):
    inlines = [OptionInlineAdmin]
    list_display = ('id', 'category', 'level', 'question')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'category', 'get_question', 'results')

    def get_question(self, obj):
        return ", ".join([question.question for question in obj.questions.all()])
