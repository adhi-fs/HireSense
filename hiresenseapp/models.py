from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# Create your models here.
class Profile(models.Model):
    ROLE_CHOICES=(
        ('candidate' , 'Candidate'),
        ('employer' , 'Employer')
    )

    user=models.OneToOneField(User,on_delete=models.CASCADE )
    role=models.CharField(max_length=30, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
class Jobs(models.Model):

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
    ]

    job_title=models.CharField(max_length=50)
    job_role=models.CharField(max_length=50)
    job_location=models.CharField(max_length=50)
    job_description=models.TextField()
    job_salary=models.CharField(max_length=50)
    employer=models.ForeignKey(Profile, on_delete=models.CASCADE)
    job_posted_on=models.DateTimeField(auto_now_add=True)
    job_status=models.CharField(choices=STATUS_CHOICES, default='open')

    passing_Score=models.IntegerField(default=5)

    def __str__(self):
        return f'{self.job_title} - {self.employer.user.username}'
    
class Jobapplication(models.Model):
    STATUS_CHOICE= [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('selected', 'Selected'),
        ('cancelled', 'Cancelled'),
    ]

    candidate=models.ForeignKey(User, on_delete=models.CASCADE)
    job=models.ForeignKey(Jobs, on_delete=models.CASCADE)
    resume=models.FileField(upload_to='resumes/')
    cover_letter=models.FileField(upload_to='cover_letters/')
    additional_details=models.TextField()
    status=models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')
    applied_at=models.DateTimeField(auto_now_add=True)
    interview_assigned=models.BooleanField(default=False)
    

    def clean(self):
        if self.resume and not self.resume.name.endswith('.pdf'):
            raise ValidationError("Resume must be a PDF file.")
        
        if self.cover_letter and not self.cover_letter.name.endswith('.pdf'):
            raise ValidationError("cover letter must be a PDF file")

    def __str__(self):
        return f'{self.candidate.username} - {self.job.job_title}'


class Interviewquestion(models.Model):
    job=models.ForeignKey(Jobs,on_delete=models.CASCADE, related_name='interview_questions')
    question_text=models.TextField()
    keywords=models.TextField(help_text='comma seperated keywords')
    max_score=models.IntegerField(default=10)

    def __str__(self):
        return f"{self.job.job_title} - Question"
    

class Interviewresult(models.Model):
    application=models.OneToOneField(Jobapplication, on_delete=models.CASCADE)
    total_score=models.IntegerField(default=0)
    passed=models.BooleanField(default=False)
    submitted_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application.candidate.username} - Result"
    

class Interviewsession(models.Model):
    candidate=models.ForeignKey(User, on_delete=models.CASCADE)
    job=models.ForeignKey(Jobs,on_delete=models.CASCADE)
    assigned_on=models.DateTimeField(auto_now_add=True)
    completed=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.candidate.username} - {self.job.job_title}"
    

class Candidateanswer(models.Model):
    # candidate=models.ForeignKey(User, on_delete=models.CASCADE)
    # job=models.ForeignKey(Jobs, on_delete=models.CASCADE)
    session=models.ForeignKey(Interviewsession, on_delete=models.CASCADE, null=True)
    question=models.ForeignKey(Interviewquestion, on_delete=models.CASCADE)
    answer_text=models.TextField()
    score=models.FloatField(default=0)
    submitted_on=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session.candidate.username}-{self.question.id}"
    
class Mockinterviewquestions(models.Model):
     DIFFICULTY_CHOICES = (
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    )

     job_role = models.CharField(max_length=100)
     company = models.CharField(max_length=100, )
     difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, null=True)

     question_text = models.TextField(null=True)
     keywords = models.TextField(help_text="Comma separated keywords")
     max_score = models.IntegerField(default=10)

     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
        return f"{self.job_role} - {self.difficulty} - {self.company}"
    
class MockInterviewResult(models.Model):
    candidate = models.ForeignKey(User, on_delete=models.CASCADE)
    job_role = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20)
    total_score = models.IntegerField()
    total_questions = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.username} - {self.job_role} ({self.company})"
