from django.db.models import Avg, Count, Subquery, Q
from django.http import HttpResponseNotFound
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions, serializers, status
from .serializers import CategorySerializer, QuestionSerializer, ResultSerializer
from .models import Category, Question, Option, Result
from account.models import Account
from account.serializer import MyProfileSerializer
from datetime import datetime, timedelta
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth


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
            answered_questions = Result.objects.filter(author=self.request.user, categories_id=category_id).values('questions')
            qs = qs.filter(category_id=category_id).exclude(id__in=Subquery(answered_questions)).order_by('?')[:5]
            # answered_questions = Result.objects.filter(author=self.request.user, categories_id=category_id,
            #                                            options__is_true=False).values('questions')
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
    def post(self, request):
        count = 0
        account = self.request.user
        categories_id = self.request.data.get('category_id')
        questions = self.request.data.get('questions')
        print(questions)
        try:  # category ni id sini tekshiradi
            Category.objects.get(id=categories_id)
        except Category.DoesNotExist:
            return Response("Category not found")
        result = Result.objects.create(author_id=account.id, categories_id=categories_id) # author_id bu modeldagi author
        print(result)
        correct_answer = []
        incorrect_answer = []
        for i in questions:
            print(i)
            question = int(i.get('question_id'))
            option = int(i.get('option_id'))
            try: # question_id bn option_id ni tekshiradi
                question_id = Question.objects.get(id=question)
                option_id = Option.objects.get(id=option)
            except (Question.DoesNotExist, Option.DoesNotExist):
                continue
            answer = Question.objects.filter(options__is_true=True, category_id=categories_id, options=option_id, question=question_id)
            if answer:
                correct_answer.append((f"Question: {question_id.question}", f"Answers: {option_id.option} --> True"))

                count += 100 // len(questions)
                print(count)
            else:
                incorrect_answer.append((f"Question: {question_id.question}", f"Answers: {option_id.option} --> Wrong"))
            result.questions.add(question)
        result.results = count
        print(result)
        result.save()
        response_data = {
            'author': account.id,
            'category': categories_id,
            'result_percentage': count,
            'correct_answer': correct_answer,
            'incorrect_answer': incorrect_answer
        }
        return Response({'response_data': response_data})
        # return Response("result saved")
        # return Response({"Your results": result.results})
        # return Response(data=result)


"""
 {
      "category_id": 1,
      "questions": [
        {
          "question_id": 1,
          "option_id": 1
        },
        {
          "question_id": 2, 
          "option_id": 5
        },
        {
          "question_id": 3,
          "option_id": 9
        },
        {
          "question_id": 4,
          "option_id": 13
        },
        {
          "question_id": 5,
          "option_id": 17
        }
      ]
    }
"""


# class AverageListForCategory(APIView):
#     def get(self, request):
#         categories = Category.objects.all()
#         cat_results = []
#         for category in categories:
#             results = Result.objects.filter(categories=category)
#             print(results)
#             if results:
#                 average = results.aggregate(categories=Avg('category'))
#                 print(average)
#                 avg_count = average['category']
#                 print(avg_count)
#                 cat_results.append({'category': category.name, 'average': avg_count})
#             else:
#                 cat_results.append({'category': category.name, 'average': 0})
#
#             return Response({'results': cat_results})


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

class DayStatisticListAPIView(generics.ListAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    def get_queryset(self):
        qs = Result.objects.annotate(day=TruncDay('created_date')).filter(day=timezone.now().date()).annotate(total_results=Count('id'))
        return qs


class WeekStatisticListAPIView(generics.ListAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    def get_queryset(self):
        now = timezone.now().date()
        past_week = now - timedelta(days=7)
        qs = Result.objects.filter(created_date__range=[past_week, now]).annotate(total_results=Count('id'))
        return qs


class MonthStatisticListAPIView(generics.ListAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    def get_queryset(self):
        now = timezone.now().date()
        past_month = now - timedelta(days=30)
        qs = Result.objects.filter(created_date__range=[past_month, now]).annotate(total_results=Count('id'))
        return qs


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


