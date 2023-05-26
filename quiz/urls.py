from django.urls import path
from . import views


urlpatterns = [
    path('category/', views.CategoryList.as_view()),
    path('question/<int:category_id>/', views.QuestionAPIView.as_view()),
    path('result/', views.ResultList.as_view()),
    path('answers/', views.AnswersAPIView.as_view()),
    path('average_by_category/', views.AverageListForCategory.as_view()),
    path('for_day_statistic/', views.DayStatisticListAPIView.as_view()),
    path('for_week_statistic/', views.WeekStatisticListAPIView.as_view()),
    path('for_month_statistic/', views.MonthStatisticListAPIView.as_view()),
    # path('average_for_date/', views.AverageListForDate.as_view()),
    path('statistic_for_student/', views.AverageStaticForStudent.as_view())
]

