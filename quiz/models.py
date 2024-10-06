from django.db import models
import json
from django.contrib.auth.models import User


class QuizBank(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz_bank = models.ForeignKey(QuizBank, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    options = models.JSONField()  # Store options as JSON
    correct_answers = models.JSONField()  # Store correct answers as JSON
    has_multiple_correct_answers = models.BooleanField(default=False)  # Indicates if question has multiple correct answers

    def __str__(self):
        return self.question_text
    
    def get_options(self):
        """ Convert options JSON string to a list """
        return json.loads(self.options) if isinstance(self.options, str) else self.options
    
    def get_correct_answers(self):
        """ Convert correct answers JSON string to a list """
        return json.loads(self.correct_answers) if isinstance(self.correct_answers, str) else self.correct_answers


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_bank = models.ForeignKey(QuizBank, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField()
    attempt_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz_bank.name} - {self.attempt_date}"


class CandidateAnswer(models.Model):
    quiz_attempt = models.ForeignKey(QuizAttempt, related_name='candidate_answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answers = models.JSONField()  # Store selected answers as JSON
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.quiz_attempt.user.username} - {self.question.question_text}"
    
    def get_selected_answers(self):
        """ Convert selected answers JSON string to a list """
        return json.loads(self.selected_answers) if isinstance(self.selected_answers, str) else self.selected_answers
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
