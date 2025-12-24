from django.contrib.auth.models import User
from django.db import models
from enum import Enum

class role(Enum):
    ADMIN = "admin"
    USER = "user"

class status(Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f' Author : {self.firstName} ({self.lastName})'


    def __str__(self):
        return f' Author : {self.title} ({self.status})'

class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=100,
        choices=[(role.value, role.name) for  role in role],
        default=role.USER.value
    )
    team = models.ForeignKey(Team , on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f' Author : {self.user.username} ({self.role})'

class Task(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    date_end =  models.DateTimeField()
    Executor =  models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(
        max_length=100,
        choices=[(status.value , status.name) for status in status],
        default=status.NEW.value
    )
    team = models.ForeignKey(Team , on_delete=models.CASCADE)

