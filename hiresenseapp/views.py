from django.shortcuts import redirect, render,get_object_or_404
from django.contrib.auth.models import User,auth
from django.contrib import messages
# from django.utils import timezone
from .forms import JobForm 
from django.db.models import Count
import re 
# from django.utils.timezone import now
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required,user_passes_test
from  .models import Profile,Jobs,Jobapplication,Interviewquestion,Interviewresult,Candidateanswer,Interviewsession,Mockinterviewquestions,MockInterviewResult
# Create your views here.
def home_p(request):
    return render(request, 'home.html')
def register_f(request):
    if request.method == 'POST':
        name = request.POST.get('fullname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        role = request.POST.get('role')

        if password != cpassword:
            messages.error(request, 'Passwords do not match.')
            return redirect('register_f')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register_f')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register_f')

        try:
            validate_password(password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect('register_f')

        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$'
        if not re.match(pattern, password):
            messages.error(
                request,
                "Password must contain uppercase, lowercase, number and special character."
            )
            return redirect('register_f')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=name
        )

        if role == 'employer':
            user.is_staff = True
            user.save()

        Profile.objects.create(
            user=user,
            role=role
        )

        messages.success(request, 'Account created successfully. Please login.')
        return redirect('login_f')

    return render(request, 'register.html')
def login_f(request):
    if request.method == 'POST':
        username_or_email=request.POST['username']
        password=request.POST['password']
        try:
            user_obj= User.objects.get(email=username_or_email)
            username=user_obj.username
        except User.DoesNotExist:
            username=username_or_email
        user=auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user) 
            messages.success(request, f'Welcome , {user.username}!')
            if user.is_superuser:
                return redirect('admin_dashboard')
            try:
                role=user.profile.role
                if role == 'candidate':
                    return redirect('candidate_dashboard')
                elif role == 'employer':
                    return redirect('employer_dashboard')   
                
                else:
                    return redirect('login_f')  
            except Profile.DoesNotExist:
                messages.error(request, 'not assigned with a role')
                return redirect('home_p')
        else:
            messages.error(request, 'Invalid credentials.please try again')
            return redirect('login_f')
    return render(request, 'login.html')

def logout_f(request):
    auth.logout(request)
    return redirect('home_p')

def employer_dashboard(request):
    employer_profile = Profile.objects.get(user=request.user)

    jobs = Jobs.objects.filter(
        employer=employer_profile
    ).order_by('-job_posted_on')

    candidate_applications = Jobapplication.objects.filter(
        job__in=jobs
    ).order_by('-applied_at')

    pending_applications = candidate_applications.filter(
        status='pending'
    )

    approved_requests = candidate_applications.filter(
        status='shortlisted'
    ).order_by('applied_at')

    selected_candidates = candidate_applications.filter(
        status='selected'
    )

    rejected_candidates = candidate_applications.filter(
        status='rejected'
    )

    # Dashboard statistics
    active_jobs_count = jobs.filter(
        job_status='open'
    ).count()

    applications_count = candidate_applications.count()

    interviews_count = candidate_applications.filter(
        interview_assigned=True
    ).count()

    selected_count = selected_candidates.count()

    context = {
        'jobs': jobs,

        'candidate_applications': pending_applications,

        'approved_requests': approved_requests,

        'selected_candidates': selected_candidates,

        'rejected_candidates': rejected_candidates,

        # Dashboard statistics
        'active_jobs_count': active_jobs_count,
        'applications_count': applications_count,
        'interviews_count': interviews_count,
        'selected_count': selected_count,
    }

    return render(
        request,
        'employer/employer_dashboard.html',
        context
    )

def candidate_dashboard(request):

    jobs = Jobs.objects.filter(job_status='open').order_by('-job_posted_on')
    applications = Jobapplication.objects.filter(candidate=request.user).select_related('job')
    applied_jobs_id = applications.values_list('job_id', flat=True)

    for app in applications:
        app.session_exists = Interviewsession.objects.filter(
            candidate=request.user,
            job=app.job
        ).exists()

    roles = Mockinterviewquestions.objects.values_list('job_role', flat=True).distinct()
    companies = Mockinterviewquestions.objects.values_list('company', flat=True).distinct()
    difficulties = Mockinterviewquestions.objects.values_list('difficulty', flat=True).distinct()

    return render(request, 'candidate/candidate_dashboard.html', {
        'jobs': jobs,
        'applications': applications,
        'applied_jobs_id': applied_jobs_id,
        'roles': roles,
        'companies': companies,
        'difficulties': difficulties
    })

@login_required
def add_job_f(request):
    if request.method == 'POST':
        job_title=request.POST['job_title']
        job_role=request.POST['job_role']
        job_location=request.POST['job_location']
        job_salary=request.POST['job_salary']
        job_description=request.POST['job_description']
        employer_profile=Profile.objects.get(user=request.user)
        Jobs.objects.create(
            job_title=job_title,
            job_role=job_role,
            job_location=job_location,
            job_salary=job_salary,
            job_status='open',
            job_description=job_description,
            employer=employer_profile
        )
        messages.success(request, 'Job vacancy added successfully..')
        return redirect('employer_dashboard')
    return render(request, 'employer/add_job.html')
@login_required
def edit_job_f(request, job_id):
    employer_profile = Profile.objects.get(user=request.user)
    job = get_object_or_404(
        Jobs,
        id=job_id,
        employer=employer_profile
    )
    if request.method == "POST":
        job.job_title = request.POST['job_title']
        job.job_role = request.POST['job_role']
        job.job_location = request.POST['job_location']
        job.job_salary = request.POST['job_salary']
        job.job_description = request.POST['job_description']
        job.job_status = request.POST['job_status']
        job.save()
        messages.success(request, "Job updated successfully.")
        return redirect('employer_dashboard')
    return render(request, 'employer/edit_job.html', {'job': job})
@login_required
def delete_job_f(request, job_id):
    employer_profile = Profile.objects.get(user=request.user)
    job = get_object_or_404(
        Jobs,
        id=job_id,
        employer=employer_profile 
    )
    job.delete()
    messages.success(request, "Job opening has been deleted successfully.")
    return redirect('employer_dashboard')
              
@login_required
def apply_now_f(request, job_id):
    if request.method == 'POST':
        resume=request.FILES.get('resume')
        cover_letter=request.FILES.get('cover_letter')
        additional_details=request.POST['details']
        job=get_object_or_404(Jobs, id=job_id)
        if Jobapplication.objects.filter(candidate=request.user, job=job).exists():
            messages.error(request, "You have already applied for this job.")
            return redirect('candidate_dashboard')
        application=Jobapplication(
            resume=resume,
            job=job,
            cover_letter=cover_letter,
            additional_details=additional_details,
            candidate=request.user
        )
        application.full_clean()
        application.save()
        messages.success(request, 'Application submitted successfully')
        return redirect('candidate_dashboard')
    
def update_application_status(request, app_id, action):
    application = get_object_or_404(Jobapplication, id=app_id)
    if action == "approve":
        application.status="shortlisted"
    elif action == 'decline':
        application.status="rejected"
    application.save()
    return redirect('employer_dashboard')
@login_required
def assign_interview(request, app_id):
    application = get_object_or_404(Jobapplication, id=app_id)
    if application.job.employer.user != request.user:
        messages.error(request, 'You are not authorized')
        return redirect('employer_dashboard')
    
    if application.job.job_status != 'open':
        messages.error(request, "cannot assign interview. Job is closed by the employer")
        return redirect('employer_dashboard')
    
    application.interview_assigned=True
    application.save()
    messages.success(request, f"Interview assigned to {application.candidate.username}")
    return redirect('employer_dashboard')
@login_required
def start_online_interview(request, app_id):
    application = get_object_or_404(Jobapplication, id=app_id, candidate=request.user)

    # Job and interview checks
    if application.job.job_status != "open":
        messages.error(request, "This job is no longer active.")
        return redirect('candidate_dashboard')
    if application.job.job_status == "cancelled":
        messages.error(request, "Interview has been cancelled")
        return redirect('candidate_dashboard')
    if not application.interview_assigned:
        messages.error(request, "Interview not assigned yet.")
        return redirect('candidate_dashboard')

    questions = list(application.job.interview_questions.all())
    total_questions = len(questions)
    current_index = int(request.GET.get('q', 0))  

    if 'answers' not in request.session:
        request.session['answers'] = {}

    if request.method == 'POST':
        question = questions[current_index]
        answer = request.POST.get(f"answer_{question.id}", "")
        answers = request.session['answers']
        answers[str(question.id)] = answer
        request.session['answers'] = answers

        next_index = current_index + 1

        if next_index >= total_questions:
            total_score = 0
            for q in questions:
                ans = request.session['answers'].get(str(q.id), "").lower()
                keywords = [k.strip().lower() for k in q.keywords.split(",")]
                matched = sum(1 for k in keywords if k in ans)
                score = (matched / len(keywords) * q.max_score) if keywords else 0
                total_score += score

            passed = total_score >= application.job.passing_Score

            Interviewresult.objects.create(
                application=application,
                total_score=int(total_score),
                passed=passed
            )

            # Update application status
            application.interview_assigned = False
            application.status = 'selected' if passed else 'rejected'
            application.save()

            del request.session['answers']

            messages.success(request, f"Interview submitted! Total Score: {int(total_score)}")
            return redirect('candidate_dashboard')

        else:
            return redirect(f"{request.path}?q={next_index}")

    question = questions[current_index]

    context = {
        'application': application,
        'question': question,
        'current_index': current_index + 1,
        'total_questions': total_questions,
        'is_last': current_index + 1 == total_questions,
    }

    return render(request, 'candidate/interview_page.html', context)
def toggle_job_status(request, job_id):
    job=get_object_or_404(Jobs, id=job_id)
    if job.employer.user != request.user:
        messages.error(request, "You are not authorized")
        return redirect('employer_dashboard')
    
    if job.job_status == 'open':
        job.job_status = 'closed' 
        job.save()
        applications=Jobapplication.objects.filter(job=job)
        for app in applications:
            app.interview_assigned = False
            app.status = 'cancelled'
            app.save()
        messages.warning(request, 'Job Closed. All interviews cancelled')
    else:
        job.job_status = 'open'
        job.save()
        Jobapplication.objects.filter(
            job=job,
            status='cancelled'
        ).update(status='reviewed')
        messages.success(request, "Job Opened Successfully")
    return redirect('employer_dashboard')
def add_interview_questions(request,job_id):
    job=get_object_or_404(Jobs, id=job_id)
    if request.method == 'POST':
        question_text= request.POST['question_text']
        keywords=request.POST['keywords']
        max_score=request.POST['max_score']
        if question_text and keywords and max_score:
            Interviewquestion.objects.create(
                job=job,
                question_text=question_text,
                keywords=keywords,
                max_score=max_score
            )
            messages.success(request, 'Question added successfully')
            return redirect('add_interview_questions', job_id=job.id)
        
    questions=job.interview_questions.all()
    return render(request, 'employer/add_interview_questions.html', {'job' : job, 'questions' : questions})
def edit_interview_question(request, question_id):
    question=get_object_or_404(Interviewquestion, id=question_id)
    job=question.job
    if request.method == 'POST':
        question_text=request.POST.get('question_text')
        keywords = request.POST.get('keywords')
        max_score = request.POST.get('max_score')
        if question_text and keywords and max_score:
            question.question_text =question_text
            question.keywords = keywords
            question.max_score=max_score
            question.save()
            messages.success(request, "question updated successfully")
            return redirect('add_interview_questions', job.id)
    return render(request, 'employer/edit_interview_questions.html', {'question' : question, 'job' : job})
def delete_interview_question(request, question_id):
    question = get_object_or_404(Interviewquestion, id=question_id)
    job_id = question.job.id
    question.delete()
    messages.success(request, 'Question deleted successfully!')
    return redirect('add_interview_questions', job_id=job_id)
def take_interview(request, job_id):
    job=get_object_or_404(Jobs, id=job_id)
    questions=Interviewquestion.objects.filter(job=job)
    if request.method == 'POST':
        for question in questions:
            ans_text=request.POST.get(f"answer_{question.id}")
            Candidateanswer.objects.update_or_create(
                candidate=request.user,
                job=job,
                question=question,
                defaults={"answer_text" : ans_text}
            )
            messages.success(request, "Your answers have been submitted successfully!")
            return redirect('candidate_dashboard')
    
    return render(request, 'take_interview.html', {'job':job, 'questions':questions})
def assign_interview_page(request, job_id):
    job=get_object_or_404(Jobs, id=job_id)
    candidates=User.objects.filter(jobapplication__job=job, jobapplication__status__in=['pending', 'reviewed', 'shortlisted']).distinct()
    if request.method == 'POST':
        candidate_id=request.POST.get('candidate_id')
        candidate=get_object_or_404(User, id=candidate_id)
        application=Jobapplication.objects.get(candidate=candidate, job=job)
        session,created = Interviewsession.objects.get_or_create(
            candidate=candidate,
            job=job
        )
        if created:
            questions=Interviewquestion.objects.filter(job=job)
            for q in questions:
                Candidateanswer.objects.create(session=session, question=q)
            application.interview_assigned = True
            application.save()
            messages.success(request, f"interview assigned to {candidate.username} successfully")
        else:
            messages.info(request, f"{candidate.username} already has an assigned interview for this job")
        return redirect('assign_interview_page', job_id=job.id)
    return render(request, 'employer/assign_interview.html', {
        'job' : job,
        'candidates' : candidates
    })
    
def is_admin(user):
    return user.is_superuser and user.is_authenticated

@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = User.objects.count()
    total_candidates=User.objects.filter(is_staff=False, is_superuser=False).count()
    total_employers=User.objects.filter(is_staff=True, is_superuser=False).count()
    
    total_jobs=Jobs.objects.count()
    total_applications=Jobapplication.objects.count()
    total_interviews=Interviewsession.objects.count()
    
    recent_jobs = Jobs.objects.order_by('job_posted_on')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_applications = Jobapplication.objects.order_by('-applied_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_candidates': total_candidates,
        'total_employers': total_employers,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'total_interviews': total_interviews,
        'recent_jobs': recent_jobs,
        'recent_users': recent_users,
        'recent_applications': recent_applications,
    }

    return render(request, 'admin/admin_dashboard.html', context)
    
@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.select_related('profile').all().order_by('-date_joined')   


    context = {
        'users': users
    }

    return render(request, 'admin/admin_users.html', context)

@user_passes_test(is_admin)
def admin_edit_user(request, user_id):

    user_obj = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user_obj.username = request.POST.get("username")
        user_obj.email = request.POST.get("email")
        user_obj.first_name = request.POST.get("first_name")
        user_obj.last_name = request.POST.get("last_name")

        role = request.POST.get("role")

        if role == "admin":
            user_obj.is_superuser = True
            user_obj.is_staff = True
        elif role == "employer":
            user_obj.is_superuser = False
            user_obj.is_staff = True
        else:  
            user_obj.is_superuser = False
            user_obj.is_staff = False

        user_obj.is_active = request.POST.get("is_active") == "on"

        user_obj.save()
        messages.success(request, "User updated successfully!")
        return redirect("admin_users")

    return render(request, "admin/admin_edit_user.html", {"user_obj": user_obj})

@user_passes_test(is_admin)
def admin_delete_user(request, user_id):

    user_obj = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user_obj.delete()
        messages.success(request, "User deleted successfully!")
        return redirect("admin_users")

    return render(request, "admin/admin_delete_user.html", {"user_obj": user_obj})

@user_passes_test(is_admin)
def admin_jobs(request):

    jobs = Jobs.objects.select_related('employer__user') \
        .annotate(total_applications=Count('jobapplication')) \
        .order_by('-job_posted_on')

    context = {
        'jobs': jobs
    }

    return render(request, 'admin/admin_jobs.html', context)

@user_passes_test(is_admin)
def admin_delete_job(request, job_id):

    job = get_object_or_404(Jobs, id=job_id)

    if request.method == "POST":
        job.delete()
        return redirect('admin_jobs')

    return render(request, 'admin/admin_delete_job.html', {'job': job})

@user_passes_test(is_admin)
def view_job(request, job_id):
    job = get_object_or_404(Jobs, id=job_id)
    return render(request, 'admin/view_job.html', {'job': job})

@user_passes_test(is_admin)
def edit_job(request, job_id):
    job = get_object_or_404(Jobs, id=job_id)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            print("Form saved!")
            return redirect('admin_jobs')  
    else:
    
        form = JobForm(instance=job)

    return render(request, 'admin/edit_job.html', {'form': form})

@user_passes_test(is_admin)
def admin_job_applications(request):
    applications = Jobapplication.objects.select_related('candidate', 'job', 'job__employer').all().order_by('-applied_at')
    
    context = {
        'applications': applications,
    }
    return render(request, 'admin/job_applications.html', context)

@user_passes_test(is_admin)
def admin_interview_sessions(request):
    sessions = Interviewsession.objects.select_related('candidate', 'job', 'job__employer').all().order_by('-assigned_on')

    context = {
        'sessions': sessions
    }
    return render(request, 'admin/interview_sessions.html', context)


@user_passes_test(is_admin)
def admin_mock_questions(request):

    if request.method == "POST":
        Mockinterviewquestions.objects.create(
            job_role=request.POST.get('job_role'),
            company=request.POST.get('company'),
            difficulty=request.POST.get('difficulty'),
            question_text=request.POST.get('question'),
            keywords=request.POST.get('keywords'),
            max_score=request.POST.get('max_score')
        )
        return redirect('admin_mock_questions')

    questions = Mockinterviewquestions.objects.all().order_by('-created_at')

    context = {
        'questions': questions
    }

    return render(request, 'admin/admin_mock_questions.html', context)

# def start_mock_interview(request):
#     if request.method == "POST":
#         role = request.POST.get('job_role')
#         difficulty = request.POST.get('difficulty')
#         company = request.POST.get('company')

#         questions = Mockinterviewquestions.objects.filter(
#             job_role=role,
#             difficulty=difficulty,
#             company=company
#         )[:20]

#         if questions.count() < 20:
#             return render(request, 'candidate/not_enough_questions.html')

#         request.session['mock_questions'] = list(questions.values_list('id', flat=True))
#         request.session['mock_index'] = 0
#         request.session['mock_score'] = 0

#         return redirect('mock_interview_session')


@login_required
def start_mock_interview(request):
    if request.method == "POST":
        role = request.POST.get('job_role')
        difficulty = request.POST.get('difficulty')
        company = request.POST.get('company')

        questions = Mockinterviewquestions.objects.filter(
            job_role=role,
            difficulty=difficulty,
            company=company
        )[:20]

        if questions.count() < 20:
            messages.error(request, "Not enough questions for this selection.")
            return redirect('candidate_dashboard')

        request.session['mock_session'] = {
            'role': role,
            'difficulty': difficulty,
            'company': company,
            'question_ids': list(questions.values_list('id', flat=True)),
            'current_index': 0,
            'score': 0
        }

        return redirect('mock_interview_session')

    roles = Mockinterviewquestions.objects.values_list('job_role', flat=True).distinct()
    companies = Mockinterviewquestions.objects.values_list('company', flat=True).distinct()
    difficulties = Mockinterviewquestions.objects.values_list('difficulty', flat=True).distinct()

    return render(request, 'candidate/start_mock.html', {
        'roles': roles,
        'companies': companies,
        'difficulties': difficulties
    })

# def mock_interview_session(request):
#     question_ids = request.session.get('mock_questions', [])
#     current_index = request.session.get('mock_index', 0)
#     score = request.session.get('mock_score', 0)

#     if not question_ids:
#         return redirect('candidate_dashboard')

#     if current_index >= len(question_ids):
#         final_score = score
#         # Clear session
#         request.session.pop('mock_questions')
#         request.session.pop('mock_index')
#         request.session.pop('mock_score')
#         return render(request, 'candidate/mock_feedback.html', {'score': final_score})

#     question = get_object_or_404(Mockinterviewquestions, id=question_ids[current_index])

#     if request.method == "POST":
#         answer = request.POST.get('answer', '').lower()
#         keywords = [k.strip() for k in question.keywords.lower().split(',')]
#         match_count = sum(1 for k in keywords if k in answer)
#         question_score = min(match_count, question.max_score)
#         request.session['mock_score'] = score + question_score
#         request.session['mock_index'] = current_index + 1
#         return redirect('mock_interview_session')

#     return render(request, 'candidate/interview_page.html', {
#         'question': question,
#         'current_index': current_index + 1,
#         'total_questions': len(question_ids),
#         'progress_percent': int((current_index / len(question_ids)) * 100),
#         'is_last': current_index == len(question_ids) - 1
#     })

@login_required
def mock_interview_session(request):
    session = request.session.get('mock_session')
    if not session:
        messages.error(request, "No active mock interview session found.")
        return redirect('candidate_dashboard')

    question_ids = session['question_ids']
    current_index = session['current_index']
    score = session['score']

    if current_index >= len(question_ids):
        result = MockInterviewResult.objects.create(
            candidate=request.user,
            job_role=session['role'],
            company=session['company'],
            difficulty=session['difficulty'],
            total_score=score,
            total_questions=len(question_ids)
        )

        del request.session['mock_session']

        return render(request, 'candidate/mock_feedback.html', {
            'score': score,
            'total_questions': len(question_ids),
            'role': result.job_role,
            'company': result.company,
            'difficulty': result.difficulty
        })

    question = get_object_or_404(Mockinterviewquestions, id=question_ids[current_index])

    if request.method == "POST":
        answer = request.POST.get('answer', '').lower()
        keywords = [k.strip().lower() for k in question.keywords.split(',')]
        match_count = sum(1 for k in keywords if k in answer)
        question_score = min(match_count, question.max_score)

        session['score'] += question_score
        session['current_index'] += 1
        request.session['mock_session'] = session

        return redirect('mock_interview_session')

    return render(request, 'candidate/interview_page.html', {
        'question': question,
        'current_index': current_index + 1,
        'total_questions': len(question_ids),
        'progress_percent': int((current_index / len(question_ids)) * 100),
        'is_last': current_index == len(question_ids) - 1
    })



def submit_mock_interview(request):
    role = request.session.get('mock_role')
    difficulty = request.session.get('mock_difficulty')
    company = request.session.get('mock_company')

    questions = Mockinterviewquestions.objects.filter(
        job_role=role,
        difficulty=difficulty,
        company=company
    )[:20]

    total_score = 0

    for q in questions:
        answer = request.POST.get(f'answer_{q.id}', '').lower()
        keywords = [k.strip().lower() for k in q.keywords.split(',')]
        match_count = sum(1 for k in keywords if k in answer)
        question_score = min(match_count, 5)  # max 5 per question
        total_score += question_score

    MockInterviewResult.objects.create(
        candidate=request.user,
        job_role=role,
        company=company,
        difficulty=difficulty,
        total_score=total_score,
        total_questions=questions.count()
    )

    return render(request, 'candidate/mock_feedback.html', {
        'score': total_score,
        'total_questions' : len(questions),
        'role': role,
        'difficulty': difficulty,
        'company': company
    })


@user_passes_test(is_admin)
def delete_mock_question(request, question_id):
    question = get_object_or_404(Mockinterviewquestions, id=question_id)
    question.delete()
    return redirect('admin_mock_questions')

@user_passes_test(is_admin)
def edit_mock_question(request, question_id):
    question = get_object_or_404(Mockinterviewquestions, id=question_id)

    if request.method == "POST":
        question.job_role = request.POST.get('job_role')
        question.difficulty = request.POST.get('difficulty')
        question.company = request.POST.get('company')
        question.question_text = request.POST.get('question')
        question.keywords = request.POST.get('keywords')
        question.max_score = request.POST.get('max_score')
        question.save()
        return redirect('admin_mock_questions')  

    return render(request, 'admin/edit_mock_question.html', {'question': question})

@user_passes_test(is_admin)
def admin_mock_results(request):
    results = MockInterviewResult.objects.select_related('candidate').order_by('-completed_at')
    return render(request, 'admin/admin_mock_results.html', {'results': results})
