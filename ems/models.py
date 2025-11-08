from django.db import models

# Create your models here.
class EmployeeData(models.Model):
    id = models.AutoField(primary_key=True)
    emp_name = models.CharField(max_length=70,null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    age = models.IntegerField(null=True,blank=True)
    department =models.CharField(max_length=150,null=True,blank=True)

    def __str__(self):
        return self.emp_name or f"Employee:{id}"
 
 