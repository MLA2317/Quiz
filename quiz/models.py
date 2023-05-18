from django.db import models
from account.models import Account


class TimeStamp(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Category(TimeStamp):
    title = models.CharField(max_length=21)

    def __str__(self):
        return self.title

#
# class Level(models.Model):
#     subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
#     title = models.CharField(max_length=221)
#
#     def __str__(self):
#         return self.title


class Question(TimeStamp):
    LEVEL = (
        (0, '1-level(easy)'),
        (1, '2-level(middle)'),
        (2, '3-level(hard)')
    )
    categories = models.ForeignKey(Category, verbose_name='category', on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVEL)
    questions = models.CharField(max_length=221)

    def __str__(self):
        return self.questions


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.CharField(max_length=221)
    is_true = models.BooleanField(default=False)

    def __str__(self):
        return self.option


class Result(TimeStamp):
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    categories = models.ForeignKey(Category, verbose_name='category', on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question)
    results = models.DecimalField(decimal_places=2, max_digits=5)

    def __str__(self):
        return f"{self.results} of {self.author}"





