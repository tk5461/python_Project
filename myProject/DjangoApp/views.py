from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PersonForm
from .models import Task

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == "POST":
        user_form = UserCreationForm(request.POST)
        person_form = PersonForm(request.POST)

        if user_form.is_valid() and person_form.is_valid():
            user = user_form.save()
            person = person_form.save(commit=False)
            person.user = user
            person.save()
            login(request, user)
            return redirect("home")
    else:
        user_form = UserCreationForm()
        person_form = PersonForm()

    return render(request, "Register.html", { "user_form": user_form, "person_form": person_form })

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if hasattr(user, 'person') and user.person is not None:
                    person = user.person
                    user_role = person.role
                    user_team = person.team

                    request.session['user_role'] = user_role
                    request.session['user_team'] = user_team.name if user_team else 'No team assigned'
                else:
                    request.session['user_role'] = 'No role assigned'
                    request.session['user_team'] = 'No team assigned'

                return redirect("home")
            else:
                return render(request, 'Login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = AuthenticationForm()

    return render(request, 'Login.html', {'form': form})

from django.shortcuts import render

def logout_view(request):
    logout(request)



@login_required
def all_task(request):
    tasks = Task.objects.all()
    return render(request, 'tasks.html', {'tasks': tasks})
