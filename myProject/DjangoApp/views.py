from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

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
def TaskFilterByStatus(request):
     if request.method == "POST":
         selected_status = request.POST.get('status')
         if selected_status == 'all':
             return redirect('tasks')
         filtered_tasks = Task.objects.filter(status=selected_status)
         return render(request, 'tasks.html', {'tasks': filtered_tasks})
     return redirect('tasks')


# def employee_list(request):
#     form = PersonForm(request.GET or None)
#     executor = Task.objects.all()
#
#     # קבלת שם המשתמש (username) מתוך ה-GET
#     name = request.GET.get('name', None)
#
#     if name:
#         # סינון לפי שם המשתמש של ה-Executor (User)
#         executor = executor.filter(Executor__user__username__icontains=name)
#
#     # סינון לפי סטטוס (אם זה קיים)
#     status = request.GET.get('status', None)
#     if status and status != 'all':
#         executor = executor.filter(status=status)
#
#     return render(request, 'tasks.html', {'form': form, 'executor': executor})
#@login_required
#def all_task(request):
#   tasks = Task.objects.all()
#    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def all_task(request):
    # 1. קבלת המשתמש המחובר והצוות שלו
    user_person = request.user.person
    user_team = user_person.team

    # 2. שליפת משימות השייכות לצוות של המשתמש בלבד
    tasks = Task.objects.filter(team=user_team)

    # 3. קבלת ערכי הסינון מה-URL
    status_filter = request.GET.get('status_filter')
    executor_filter = request.GET.get('executor_filter')

    # 4. החלת הסינונים (אם נבחרו)
    if status_filter and status_filter != "":
        tasks = tasks.filter(status=status_filter)

    if executor_filter and executor_filter != "":
        tasks = tasks.filter(Executor_id=executor_filter)

    # 5. שליפת חברי הצוות הנוכחי בלבד עבור ה-Dropdown
    team_members = Person.objects.filter(team=user_team)

    return render(request, 'tasks.html', {
        'tasks': tasks,
        'team_members': team_members,
    })