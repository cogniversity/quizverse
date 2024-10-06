from django.urls import path
from .views import (
    home_view,
    quiz_view,
    results_view,
    add_quiz_bank_view,
    remove_quiz_bank_view,
    upload_questions_view,
    register_view,
    login_view,
    logout_view,
    profile_view,
    quiz_history_view,
    admin_user_management_view,
    update_user_profile_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('quiz/<int:quiz_bank_id>/', quiz_view, name='quiz_view'),
    path('results/<int:quiz_bank_id>/', results_view, name='results_view'),
    path('add-quiz-bank/', add_quiz_bank_view, name='add_quiz_bank'),
    path('remove-quiz-bank/<int:quiz_bank_id>/', remove_quiz_bank_view, name='remove_quiz_bank'),
    path('upload-questions/', upload_questions_view, name='upload_questions'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('quiz-history/', quiz_history_view, name='quiz_history'),
    path('admin_user_management/', admin_user_management_view, name='admin_user_management'),
    path('admin_update_user_profile/<int:user_id>/', update_user_profile_view, name='update_user_profile'),

]
