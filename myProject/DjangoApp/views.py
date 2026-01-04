from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .forms import PersonForm , TaskForm
from .models import Task, Team, Person
from django.contrib import messages

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
                    # request.session['user_team'] = user_team.name if user_team else 'No team assigned'
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
    return redirect("home")


@login_required
def all_task(request):
    tasks = Task.objects.all()
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def add_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tasks')
    else:
        team = Team.objects.first()
        form = TaskForm(team=team)

    return render(request, 'addTasks.html', {'form': form})


@login_required
def delete_task(request, id):
    task = get_object_or_404(Task, pk=id)
    if task.Executor:
        messages.error(request, "אי אפשר למחוק משימה שיש לה אחראי.")
        return redirect('tasks')

    if request.method == "POST":
        task.delete()
        messages.success(request, "המשימה נמחקה בהצלחה.")
        return redirect('tasks')

    return render(request, 'tasks.html', {'task': task})


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if task.Executor:
        messages.error(request, "לא ניתן לערוך משימה ששויכה לעובד.")
        return redirect('tasks')

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('tasks')
    else:
        form = TaskForm(instance=task)

    return render(request, 'editTask.html', {'form': form, 'task': task})

@login_required
def update_task_status(request, id):
    task = get_object_or_404(Task, pk=id)

    if request.method == "POST":
        new_status = request.POST.get('status')
        task.status = new_status
        task.save()
        messages.success(request, "הסטטוס שונה בהצלחה.")
        return redirect('tasks')

    return redirect('tasks')


@login_required
def update_task_executor(request, id):
    task = get_object_or_404(Task, pk=id)
    person = get_object_or_404(Person, user=request.user)

    if request.method == "POST":
        if task.Executor is not None:
            messages.error(request, "משימה זו כבר משויכת לאחראי.")
            return redirect('tasks')

        task.Executor = person
        task.save()
        messages.success(request, "המשימה הוקצתה בהצלחה.")
        return redirect('tasks')

    return redirect('tasks')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Task

@login_required
def filter_by_status(request):
    status_filter = request.GET.get('status')
    tasks = Task.objects.all()
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    context = {
        'tasks': tasks,
    }

    return render(request, 'tasks.html', context)