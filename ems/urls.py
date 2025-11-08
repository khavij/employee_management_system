from django.urls import path
from .views import *

urlpatterns =[
    path('employees/', Employee.as_view(), name='employees'),
    path('employees/<int:id>', Employee.as_view(), name='employee_detail'),
]