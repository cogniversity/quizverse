from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import QuizBank, Question, CandidateAnswer, QuizAttempt, Profile, User
from .forms import JSONUploadForm, ProfileUpdateForm
import json
import random
import logging
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .decorators import admin_required

# Set up logging
logger = logging.getLogger(__name__)

# User Registration View
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                logger.info(f"User {username} registered and logged in.")
                return redirect('home')
            else:
                messages.error(request, 'Registration failed. Please try again.')
                logger.warning(f"Registration failed for user {username}.")
    else:
        form = UserCreationForm()

    return render(request, 'quiz/register.html', {'form': form})

# User Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"User {username} logged in.")
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            logger.warning(f"Failed login attempt for user {username}.")
    
    return render(request, 'quiz/login.html')

# User Logout View
@login_required
def logout_view(request):
    logger.info(f"User {request.user.username} logged out.")
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            logger.info(f"Profile updated for user {request.user.username}.")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'quiz/profile.html', {'form': form})

@admin_required
def upload_questions_view(request):
    if request.method == 'POST':
        form = JSONUploadForm(request.POST, request.FILES)
        if form.is_valid():
            json_file = request.FILES['json_file']
            quiz_bank = form.cleaned_data['quiz_bank']  # Get the selected quiz bank
            
            try:
                data = json.load(json_file)  # Parse the uploaded JSON file
                for item in data:
                    question_text = item['question_text']
                    options = item['options']
                    correct_answers = [opt['option_text'] for opt in options if opt.get('is_correct', False)]

                    # Save the question to the database
                    question = Question(
                        quiz_bank=quiz_bank,
                        question_text=question_text,
                        options=json.dumps([opt['option_text'] for opt in options]),  # Store options as JSON
                        correct_answers=json.dumps(correct_answers),  # Store correct answers as JSON
                        has_multiple_correct_answers=len(correct_answers) > 1  # Set if there are multiple correct answers
                    )
                    question.save()

                messages.success(request, 'Questions uploaded successfully!')
                logger.info(f"Questions uploaded to quiz bank '{quiz_bank.name}' successfully.")
                return redirect('home')  # Redirect after successful upload
            except json.JSONDecodeError:
                messages.error(request, 'Invalid JSON file. Please upload a valid file.')
                logger.error('Invalid JSON file uploaded for questions.')
        else:
            messages.error(request, 'Form is not valid. Please correct the errors.')

    else:
        form = JSONUploadForm()

    return render(request, 'quiz/upload_questions.html', {'form': form})

def home_view(request):
    if request.user.is_authenticated:
        quiz_banks = QuizBank.objects.all()
    
        # Get the user's quiz attempt history
        attempts = QuizAttempt.objects.filter(user=request.user).order_by('-attempt_date')
        
        if request.user.profile.is_admin:
            return render(request, 'quiz/home_admin.html', {'quiz_banks': quiz_banks, 'attempts': attempts})
        else:
            return render(request, 'quiz/home_user.html', {'quiz_banks': quiz_banks, 'attempts': attempts})
    else:
        return redirect('login')  # Or a landing page for non-authenticated users

@login_required
def quiz_view(request, quiz_bank_id):
    quiz_bank = get_object_or_404(QuizBank, id=quiz_bank_id)

    if request.method == 'POST':
        total_questions = request.POST.get('total_questions')
        score = 0

        # Create a new QuizAttempt
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz_bank=quiz_bank,
            total_questions=total_questions,
        )

        question_ids = [key.split('_')[1] for key in request.POST if key.startswith('question_')]
        questions = Question.objects.filter(id__in=question_ids)
        question_map = {f'question_{q.id}': q for q in questions}  # Use 'question_{q.id}' as the key

        # Evaluate answers and calculate score
        for key, value in request.POST.items():
            if key.startswith('question_'):
                question = question_map[key]  # Fetch the question using 'question_{id}' as the key
                correct_answers = question.get_correct_answers()
                selected_answers = request.POST.getlist(key)  # Use key directly since it's the same as the form field
                
                # Record the candidate answer
                CandidateAnswer.objects.create(
                    quiz_attempt=attempt,
                    question=question,
                    selected_answers=json.dumps(selected_answers),
                    score=1 if set(correct_answers) == set(selected_answers) else 0
                )

                # Calculate the score
                score += 1 if set(correct_answers) == set(selected_answers) else 0

        # Update the score in the attempt
        attempt.score = score
        attempt.save()

        messages.success(request, 'Quiz submitted successfully! Your score has been recorded.')
        logger.info(f"User {request.user.username} submitted quiz for '{quiz_bank.name}' with a score of {score}.")
        return redirect('results_view', quiz_bank_id=quiz_bank_id)

    questions = list(quiz_bank.questions.all())
    random.shuffle(questions)  # Shuffle the list
    questions = questions[:25]  # Get the first 25 questions

    for question in questions:
        question.options = question.get_options()  # Convert JSON string to a list
        question.correct_answers = question.get_correct_answers()  # Convert JSON string to a list

    return render(request, 'quiz/quiz_view.html', {'quiz_bank': quiz_bank, 'questions': questions})

@login_required
def results_view(request, quiz_bank_id):
    attempts = QuizAttempt.objects.filter(quiz_bank_id=quiz_bank_id, user=request.user).order_by('-attempt_date')

    # Fetch the latest attempt to show the details
    latest_attempt = attempts.first() if attempts.exists() else None
    candidate_answers = latest_attempt.candidate_answers.all() if latest_attempt else []

    # Fetch the quiz bank from the latest attempt
    quiz_bank = latest_attempt.quiz_bank if latest_attempt else None

    # Parse selected_answers JSON for each candidate answer
    for answer in candidate_answers:
        answer.selected_answers = json.loads(answer.selected_answers)  # Convert JSON to Python list

    context = {
        'attempts': attempts,
        'latest_attempt': latest_attempt,
        'candidate_answers': candidate_answers,
        'quiz_bank': quiz_bank,  # Pass quiz_bank to the template
    }
    return render(request, 'quiz/results.html', context)

@admin_required
def add_quiz_bank_view(request):
    if request.method == 'POST':
        quiz_bank_name = request.POST.get('quiz_bank_name')
        if quiz_bank_name:
            QuizBank.objects.create(name=quiz_bank_name)
            messages.success(request, f'Quiz bank "{quiz_bank_name}" added successfully!')
            logger.info(f'Quiz bank "{quiz_bank_name}" added by admin {request.user.username}.')
        else:
            messages.error(request, 'Please enter a quiz bank name.')

    return redirect('home')

@admin_required
def remove_quiz_bank_view(request, quiz_bank_id):
    try:
        quiz_bank = QuizBank.objects.get(id=quiz_bank_id)
        quiz_bank.delete()
        messages.success(request, f'Quiz bank "{quiz_bank.name}" removed successfully!')
        logger.info(f'Quiz bank "{quiz_bank.name}" removed by admin {request.user.username}.')
    except QuizBank.DoesNotExist:
        messages.error(request, 'Quiz bank not found.')
        logger.error(f'Tried to remove non-existent quiz bank with ID {quiz_bank_id}.')

    return redirect('home')

@login_required
def quiz_history_view(request):
    attempts = QuizAttempt.objects.filter(user=request.user).order_by('-attempt_date')
    logger.info(f"User {request.user.username} accessed their quiz history.")
    return render(request, 'quiz/quiz_history.html', {'attempts': attempts})

@admin_required
def admin_user_management_view(request):
    users = User.objects.all()
    logger.info(f"Admin {request.user.username} accessed user management.")
    return render(request, 'quiz/admin_user_management.html', {'users': users})

@admin_required
def update_user_profile_view(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        is_admin = request.POST.get('is_admin') == 'on'
        
        # Validate input data
        if not first_name or not last_name:
            messages.error(request, 'First name and last name are required.')
            logger.warning(f"Admin {request.user.username} failed to update user profile: missing fields.")
            return render(request, 'quiz/update_user_profile.html', {'profile': profile})

        profile.first_name = first_name
        profile.last_name = last_name
        profile.bio = bio
        profile.is_admin = is_admin
        profile.save()
        messages.success(request, f'Profile for {profile.user.username} updated successfully!')
        logger.info(f"Admin {request.user.username} updated profile for user {profile.user.username}.")
        return redirect('admin_user_management')  # Redirect to the user management page

    return render(request, 'quiz/admin_update_user_profile.html', {'profile': profile})
