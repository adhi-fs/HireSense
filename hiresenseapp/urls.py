from django.urls import  path

from hiresenseapp import views

urlpatterns = [
   path('', views.home_p, name='home_p'),
   path('registerf/', views.register_f, name='register_f'),
   path('loginf/', views.login_f, name='login_f'),
   path('logout/', views.logout_f, name='logout_f'),
   path('employer_dash/', views.employer_dashboard, name='employer_dashboard'),
   path('candidate_dash/', views.candidate_dashboard, name='candidate_dashboard'),
   path('addjob/', views.add_job_f, name='add_job_f'),
   path('edit-job/<int:job_id>/', views.edit_job_f, name='edit_job_f'),
   path('delete-job/<int:job_id>/', views.delete_job_f, name='delete_job_f'),
   path('apply_now_f/<int:job_id>/', views.apply_now_f, name='apply_now_f'),
   path('update_application/<int:app_id>/<str:action>/', views.update_application_status, name='update_application'),
   path('assign_interview/<int:app_id>/', views.assign_interview, name='assign_interview'),
   path('start_interview/<int:app_id>/', views.start_online_interview, name='start_online_interview'),
   path('toggle-job/<int:job_id>/', views.toggle_job_status, name='toggle_job_status'),
   path('add-interview-questions/<int:job_id>/', views.add_interview_questions, name='add_interview_questions'),
   path('edit-interview-question/<int:question_id>/', views.edit_interview_question, name='edit_interview_question'),
   path('delete-interview-question/<int:question_id>/', views.delete_interview_question, name='delete_interview_question'),
   path('take_interview/<int:job_id>/',views.take_interview, name='take_interview'),
   path('job/<int:job_id>/assign/', views.assign_interview_page, name='assign_interview_page'),
   path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
   path('admin-users/', views.admin_users, name='admin_users'),
   path('admin-users/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
   path('admin-users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
   path('admin-jobs/', views.admin_jobs, name='admin_jobs'),
   path('admin-jobs/jobs/view/<int:job_id>/', views.view_job, name='view_job'),
   path('admin-jobs/jobs/edit/<int:job_id>/', views.edit_job, name='edit_job'),
   path('admin-jobs/delete/<int:job_id>/', views.admin_delete_job, name='admin_delete_job'),
   path('admin-application/job-applications/', views.admin_job_applications, name='admin_job_applications'),
   path('admin-interviews/interviews/', views.admin_interview_sessions, name='admin_interview_sessions'),
   path('admin-mock/mock-questions/', views.admin_mock_questions, name='admin_mock_questions'),
   path('mock-interview/submit/', views.submit_mock_interview, name='submit_mock_interview'),
   path('mock/start_mock_interview/', views.start_mock_interview, name='start_mock_interview'),
   path('admin_mock/mock_interview/', views.mock_interview_session, name='mock_interview_session'),
   path('admin_mock/mock-question/delete/<int:question_id>/', views.delete_mock_question, name='delete_mock_question'),
   path('admin_mock/mock-question/edit/<int:question_id>/', views.edit_mock_question, name='edit_mock_question'),
   path('admin-mock/mock-results/', views.admin_mock_results, name='admin_mock_results'),





]


