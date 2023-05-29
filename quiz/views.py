from django.db.models import Avg, Count, Subquery, Q
from django.db import models
from django.http import HttpResponseNotFound
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions, serializers, status, views
from .serializers import CategorySerializer, QuestionSerializer, QuestionResultSerializer, ResultSerializer, OptionResultSerializer, OptionSerializer
from .models import Category, Question, Option, Result
from account.models import Account
from account.serializer import MyProfileSerializer
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class QuestionAPIView(generics.ListAPIView):  # Questionlani korish uchun
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset()
        category_id = self.kwargs.get('category_id')
        print(category_id)
        print(qs)
        if category_id:
            # answered_questions = Result.objects.filter(author=self.request.user, categories_id=category_id).values('questions')
            answered_questions = Result.objects.filter(author=self.request.user, categories_id=category_id,
                                                       questions__options__is_true=True).values('questions')
            qs = qs.filter(category_id=category_id).exclude(id__in=Subquery(answered_questions)).order_by('?')[:5]
            # qs = qs.filter(Q(category_id=category_id) |
            #                Q(id__in=Subquery(answered_questions))).order_by('?')[:5]
            print(qs)
            return qs
        return HttpResponseNotFound('Not found!')


class ResultList(generics.ListAPIView):  # Umumiy resultatlari uchun
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    # def get_queryset(self, *args, **kwargs):
    #     qs = super().get_queryset()
    #     author = self.request.user
    #     print(author)
    #     if qs:
    #         qs = Option.objects.filter(author=author)
    #         print(qs)
    #     print(qs)
    #     return qs


class AnswersAPIView(APIView):  # javoblarini jonatish uchun

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'category_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Category_id'
                ),
                'questions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'question_id': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='Question_id'
                            ),
                            'option_is': openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description='Option_id'
                            ),
                        }
                    )
                )
            },
            required=['category_id', 'questions'],
            example={
                'category_id': 1,
                'questions': [
                    {
                        'question_id': 2,
                        'option_id': 3
                    },
                    {
                        'question_id': 3,
                        'option_id': 7
                    },
                    {
                        'question_id': 4,
                        'option_id': 11
                    },
                    {
                        'question_id': 5,
                        'option_id': 15
                    },
                    {
                        'question_id': 6,
                        'option_id': 19
                    }
                ]
            }
        )
    )
    def post(self, request):  # 2 - usul
        statistic = []
        count = 0
        account = self.request.user
        category_id = self.request.data.get('category_id')
        questions = self.request.data.get('questions')

        try:
            Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response("Category not found")
        result = Result.objects.create(author_id=account.id, category_id=category_id)

        j = 0
        for i in questions:
            question_id = int(i.get('question_id'))
            option_id = int(i.get('option_id'))
            try:
                question = Question.objects.get(id=question_id)
                option = Option.objects.get(id=option_id)
            except Exception as e:
                raise ValidationError(e.args)
            all_options = [n.id for n in question.options.all()]
            if option_id not in all_options:
                result.delete()
                return Response({'message': 'Answer does not match the question, please send correct data'})
            statistic.append({
                "Question": QuestionResultSerializer(question).data,
                "Option": OptionResultSerializer(option).data
            })

            final_option = Question.objects.filter(options__is_true=True, category_id=category_id, id=question_id,
                                                   options=option)
            if final_option:
                count += 100 // len(questions)
                statistic[j]["Student's option"] = "True"
            else:
                statistic[j]["Student's option"] = "False"

            result.questions.add(question)
            j += 1
        if 99 <= count < 100:
            count = 100
        result.result = count
        result.save()
        result_serialized = ResultSerializer(result).data
        response_data = {
            "result": result_serialized,
            "statistic": statistic,
            'result_percentage': count,
        }

        return Response(response_data)

    # def post(self, request): # 1 -usul
    #     count = 0
    #     account = self.request.user
    #     categories_id = self.request.data.get('category_id')
    #     questions = self.request.data.get('questions')
    #     print(questions)
    #     try:  # category ni id sini tekshiradi
    #         Category.objects.get(id=categories_id)
    #     except Category.DoesNotExist:
    #         return Response("Category not found")
    #     result = Result.objects.create(author_id=account.id, category_id=categories_id) # author_id bu modeldagi author
    #     print(result)
    #     correct_answer = []
    #     incorrect_answer = []
    #     processed_questions = set()
    #     for i in questions:
    #         print(i)
    #         question = int(i.get('question_id'))
    #         option = int(i.get('option_id'))
    #         # all_options = [m.id for m in Option.objects.filter(question_id=question)]
    #         # if option in all_options:
    #         #     return Response({'message': "Answer is not found, please send correct data"})
    #         try:  # question_id bn option_id ni tekshiradi
    #             question_id = Question.objects.get(id=question)
    #             option_id = Option.objects.get(id=option)#  question=question_id - bu question_id lani tegishli option idlari
    #         except (Question.DoesNotExist, Option.DoesNotExist):
    #             continue
    #         if question_id.id in processed_questions:
    #             raise ValueError('You already solved this question')
    #             # continue
    #         answer = Question.objects.filter(options__is_true=True, category_id=categories_id, options=option_id, question=question_id)
    #         if answer:
    #             correct_answer.append((f"Question: {question_id.question}", f"Answers: {option_id.option} --> True"))
    #
    #             count += 100 // len(questions)
    #             print(count)
    #         else:
    #             incorrect_answer.append((f"Question: {question_id.question}", f"Answers: {option_id.option} --> Wrong"))
    #         result.questions.add(question)
    #     result.results = count
    #     print(result)
    #     result.save()
    #     response_data = {
    #         'author': account.id,
    #         'category': categories_id,
    #         'result_percentage': count,
    #         'correct_answer': correct_answer,
    #         'incorrect_answer': incorrect_answer
    #     }
    #     return Response({'response_data': response_data})
        # return Response("result saved")
        # return Response({"Your results": result.results})
        # return Response(data=result)


"""
 {
      "category_id": 1,
      "questions": [
        {
          "question_id": 2,
          "option_id": 3
        },
        {
          "question_id": 3, 
          "option_id": 7
        },
        {
          "question_id": 4,
          "option_id": 11
        },
        {
          "question_id": 5,
          "option_id": 15
        },
        {
          "question_id": 6,
          "option_id": 19
        }
      ]
    }
"""


class AverageListForCategory(APIView):  # Categoriya boyicha o'rta arifmetika
    def get(self, request):
        categories = Category.objects.all()
        cat_results = []

        for category in categories:
            average = Result.get_average_results(category)
            if average is not None:
                round_average = round(average, 2)
                cat_results.append({'category': category.title, 'average': round_average})
            else:
                cat_results.append({'category': category.title, 'average': average})
        return Response({'results': cat_results})


    # class AverageListForDate(APIView):
    #     permission_classes = [permissions.IsAdminUser]
    #
    #     @staticmethod
    #     def get(request):
    #         time_period = request.GET.get('time_period', 'day')
    #
    #         if time_period == 'day':
    #             trunc_func = TruncDay('created_date')
    #         elif time_period == 'week':
    #             trunc_func = TruncWeek('created_date')
    #         elif time_period == 'month':
    #             trunc_func = TruncMonth('created_date')
    #         else:
    #             return Response("Invalid time_period parameter", status=status.HTTP_400_BAD_REQUEST)
    #
    #         results = Result.objects.annotate(
    #             result_count=Count('id'),
    #             average_results=Avg('results'),
    #             truncated_date=trunc_func,
    #         ).values('truncated_date', 'result_count', 'average_results')
    #
    #         return Response(results, status=status.HTTP_200_OK)
    # def get(self, request):
    #     categories = Category.objects.all()
    #     cat_results = []
    #
    #     day = request.GET.get('day')  # Olingan kun
    #     month = request.GET.get('month')  # Olingan oy
    #     year = request.GET.get('year')  # Olingan yil
    #
    #     for category in categories:
    #         average = Result.get_average_results_dates(category, day, month, year)
    #         cat_results.append({'category': category.title, 'average': average})
    #
    #     return Response({'results': cat_results})

    # class DayStatisticListAPIView(generics.ListAPIView):
    #     queryset = Result.objects.all()
    #     serializer_class = ResultSerializer
    #
    #     def get_queryset(self):
    #         qs = Result.objects.annotate(day=TruncDay('created_date')).filter(day=timezone.now().date()).annotate(
    #             total_results=Count('id'))
    #         return qs
    #
    #
    # class WeekStatisticListAPIView(generics.ListAPIView):
    #     queryset = Result.objects.all()
    #     serializer_class = ResultSerializer
    #
    #     def get_queryset(self):
    #         now = timezone.now().date()
    #         past_week = now - timedelta(days=7)
    #         qs = Result.objects.filter(created_date__range=[past_week, now]).annotate(total_results=Count('id'))
    #         return qs
    #
    #
    # class MonthStatisticListAPIView(generics.ListAPIView):
    #     queryset = Result.objects.all()
    #     serializer_class = ResultSerializer
    #
    #     def get_queryset(self):
    #         now = timezone.now().date()
    #         past_month = now - timedelta(days=30)
    #         qs = Result.objects.filter(created_date__range=[past_month, now]).annotate(total_results=Count('id'))
    #         return qs
    #

class DayStatic(views.APIView):
    def get(self, request, *args, **kwargs):
        day = []
        total_results = []
        average = []
        results = Result.objects.annotate(day=TruncDay('created_date'))
        daily_statistics = results.values('day').annotate(total_results=Count('id'), avg_results=Avg('results'),)
        for stat in daily_statistics:
            day = stat['day']
            average = stat['avg_results']
            total_results = stat['total_results']
        return Response({"Day": day, "average": f"{round(average)}%", "Total Results": total_results})


class WeekStatic(views.APIView):
    def get(self, request, *args, **kwargs):
        week = []
        total_results = []
        average = []
        results = Result.objects.annotate(week=TruncWeek('created_date'))
        weekly_statistics = results.values('week').annotate(total_results=Count('id'), avg_results=Avg('results'))
        for stat in weekly_statistics:
            week = stat['week']
            average = stat['avg_results']
            total_results = stat['total_results']
        return Response({"week": week, "average": round(average), "Total Results": total_results})


class MonthStatic(views.APIView):
    def get(self, request, *args, **kwargs):
        month = []
        total_results = []
        average = []
        results = Result.objects.annotate(month=TruncMonth('created_date'))
        monthly_statistics = results.values('month').annotate(total_results=Count('id'), avg_results=Avg('results'))
        for stat in monthly_statistics:
            month = stat['month']
            average = stat['avg_results']
            total_results = stat['total_results']
        return Response({"Month": month, "average": round(average), "Total Results": total_results})


class AverageStaticForStudent(APIView):  # Student statiskasi bo'yciha
    def get(self, request):
        authors = Account.objects.all()
        author_results = []
        for author in authors:
            average_result_author = Result.get_average_authors(author)
            serializer_author = MyProfileSerializer(author).data
            if average_result_author is not None:
                round_average = round(average_result_author, 2)
                author_results.append({"author": serializer_author, 'average': round_average})
            else:
                author_results.append({"author": serializer_author, 'average': average_result_author})
        return Response({'result of student': author_results})

        # for category in categories:
        #     average = Result.get_average_results(category)
        #     if average is not None:
        #         round_average = round(average, 2)
        #         cat_results.append({'category': category.title, 'average': round_average})
        #     else:
        #         cat_results.append({'category': category.title, 'average': average})
        # return Response({'results': cat_results})


class CategoryStatisticsAPIView(APIView):
    # http://127.0.0.1:8000/quiz/statistic/category//?start_date=2023-05-29&end_date=2023-05-30
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({'message': 'start_date and end_date parameters are required'}, status=400)

        try:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return Response({'message': 'start_date and end_date must be in the format YYYY-MM-DD'}, status=400)

        category_stats = Result.objects.filter(created_date__range=(start_date, end_date)).values_list('categories')\
            .annotate(attempts=models.Count('id'), total_results=models.Avg('results'))\
            .values('categories__title', 'author__username', 'attempts', 'total_results')

        statistics = []

        for category in category_stats:
            category_info = {
                'category': category['categories__title'],
                'author': category["author__username"],
                'attempts': category['attempts'],
                'total_result': category['total_results']
            }
            statistics.append(category_info)

        return Response(statistics)
