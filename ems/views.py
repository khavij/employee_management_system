from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import EmployeeData
from django.db import DatabaseError
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
from django.db.models import Q
import csv, json

class EmployeePagination(PageNumberPagination):
    page_size = 5 
    page_size_query_param = 'page_size' 
    max_page_size = 50


class Employee(APIView):
    
    def get(self, request):
        try:
            search_query = request.GET.get('search', '')
            emp_data = EmployeeData.objects.all()

            if search_query:
                emp_data = emp_data.filter(emp_name__icontains=search_query)
            emp_data = emp_data.order_by('id')
            export_format = request.GET.get('export', '').lower()
            if export_format == 'csv':
                return self.export_csv(emp_data)
            elif export_format == 'json':
                return self.export_json(emp_data)
            emp_data_values = emp_data.values()

            paginator = EmployeePagination()
            paginated_data = paginator.paginate_queryset(emp_data_values, request)

            return paginator.get_paginated_response({
                'api_status': True,
                'message': 'Data fetched successfully',
                'emp_data': list(paginated_data)
            })

        except DatabaseError as e:
            return Response({'api_status': False,'message': f'Database error: {str(e)}'}, status=500)
        except Exception as e:
            return Response({
                'api_status': False,
                'message': f'Unexpected error: {str(e)}'
            }, status=500)


    def post(self, request):
        try:
            emp_data = request.data.get('emp_data')
            if not emp_data:
                return Response({
                    'api_status': False,
                    'message': 'No employee data provided'
                }, status=400)

            EmployeeData.objects.create(**emp_data)
            return Response({
                'api_status': True,
                'message': 'Data created successfully'
            }, status=201)

        except TypeError as e:
            return Response({
                'api_status': False,
                'message': f'Invalid data format: {str(e)}'
            }, status=400)
        except DatabaseError as e:
            return Response({
                'api_status': False,
                'message': f'Database error: {str(e)}'
            }, status=500)
        except Exception as e:
            return Response({
                'api_status': False,
                'message': f'Unexpected error: {str(e)}'
            }, status=500)

    def put(self, request, id):
        try:
            emp_obj = get_object_or_404(EmployeeData, id=id)
            emp_data = request.data.get('emp_data', {})

            for key, value in emp_data.items():
                setattr(emp_obj, key, value)

            emp_obj.save()

            return Response({
                'api_status': True,
                'message': 'Employee details updated successfully'
            }, status=200)

        except DatabaseError as e:
            return Response({'api_status': False, 'message': f'Database error: {str(e)}'}, status=500)
        except Exception as e:
            return Response({'api_status': False, 'message': f'Unexpected error: {str(e)}'}, status=500)

    def delete(self, request, id):
        try:
            emp_obj = EmployeeData.objects.filter(id=id).first()

            if not emp_obj:
                return Response({
                    'api_status': False,
                    'message': f'Employee with ID {id} not found'
                }, status=404)

            emp_obj.delete()

            return Response({
                'api_status': True,
                'message': 'Employee deleted successfully'
            }, status=200)

        except DatabaseError as e:
            return Response({'api_status': False, 'message': f'Database error: {str(e)}'}, status=500)
        except Exception as e:
            return Response({'api_status': False, 'message': f'Unexpected error: {str(e)}'}, status=500)
        
    def export_csv(self, employees):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="employees.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Email','Age', 'Department' ])

        for emp in employees:
            writer.writerow([
                emp.id, emp.emp_name, emp.email,emp.age, emp.department
            ])
        return response
    
    def export_json(self, queryset):
        data = list(queryset.values()) 
        response = HttpResponse(
            json.dumps(data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="employees.json"'
        return response
