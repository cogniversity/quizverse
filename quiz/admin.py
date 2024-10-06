from django.contrib import admin
from .models import QuizBank, Question, CandidateAnswer, Profile, QuizAttempt

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz_bank', 'has_multiple_correct_answers')
    list_filter = ('quiz_bank', 'has_multiple_correct_answers')

# Register your models here.
admin.site.register(QuizBank)
admin.site.register(Question)
admin.site.register(QuizAttempt)
admin.site.register(CandidateAnswer)
admin.site.register(Profile)