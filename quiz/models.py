from django.db import models, IntegrityError
from account.models import Account
from django.db.models import Avg, UniqueConstraint, Q


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
    category = models.ForeignKey(Category, verbose_name='category', on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVEL)
    question = models.CharField(max_length=221)

    def __str__(self):
        return self.question


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option = models.CharField(max_length=221)
    is_true = models.BooleanField(default=False)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['question'],
                condition=Q(is_true=True),
                name="correct_option"
            )
        ]

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            raise IntegrityError('Only one option can be marked as correct for a question')

    def __str__(self):
        return f"{self.option}'s"


class Result(TimeStamp):
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, verbose_name='category', on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question)
    options = models.ManyToManyField(Option)
    results = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.results} of {self.author}"

    @staticmethod
    def get_average_results(category):
        average = Result.objects.filter(category=category).aggregate(avg_results=Avg('results'))
        return average['avg_results']

    @staticmethod
    def get_average_authors(author):
        average = Result.objects.filter(author=author).aggregate(Avg('results'))['results__avg']
        return average



    # @staticmethod
    # def get_average_results_dates(category, day, month, year):
    #     average = Result.objects.filter(
    #         categories=category,
    #         created_date__day=day,
    #         created_date__month=month,
    #         created_date__year=year
    #     ).annotate(avg_results=Avg('results'))
    #     return average['avg_results']






