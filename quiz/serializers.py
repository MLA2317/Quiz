from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Question, Category, Option, Result
from account.serializer import MyProfileSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'question', 'option', 'is_true']


class OptionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['option']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'category', 'level', 'question', 'options']


class QuestionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'category', 'question']

    # def validate(self, attrs):
    #     question = attrs.get('question')
    #     options = attrs.get('options')
    #     if question != options:
    #         raise ValidationError({
    #             'message': 'These answers are not relevant to the questions'
    #         })
    #     return attrs


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'author', 'category', 'questions', 'results', 'created_date']




