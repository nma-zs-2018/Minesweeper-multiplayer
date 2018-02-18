from django.shortcuts import render

# Create your views here.
from web.models import Student

def students(request):
    students = Student.objects.all()

    return render(request, "students.html", {'students': students})