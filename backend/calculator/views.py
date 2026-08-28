from django.shortcuts import render
from django.http import JsonResponse
import json
from .services import calculate_salary, calculate_gross_from_net

def index(request):
    return render(request, 'calculator/index.html')

def calculate_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            salary_type = data.get('salary_type', 'gross')
            amount = float(data.get('amount', 0))
            allowances = float(data.get('allowances', 0))
            
            include_nssf = data.get('nssf', False)
            include_pssf = data.get('pssf', False)
            include_nhif = data.get('nhif', False)
            include_heslb = data.get('heslb', False)
            include_paye = data.get('paye', True)
            custom_deductions = data.get('custom_deductions', [])
            
            if salary_type == 'net':
                result = calculate_gross_from_net(
                    target_net=amount,
                    allowances=allowances,
                    include_nssf=include_nssf,
                    include_pssf=include_pssf,
                    include_nhif=include_nhif,
                    include_heslb=include_heslb,
                    include_paye=include_paye,
                    custom_deductions=custom_deductions
                )
            else:
                result = calculate_salary(
                    basic_salary=amount,
                    allowances=allowances,
                    include_nssf=include_nssf,
                    include_pssf=include_pssf,
                    include_nhif=include_nhif,
                    include_heslb=include_heslb,
                    include_paye=include_paye,
                    custom_deductions=custom_deductions
                )
                
            return JsonResponse({'status': 'success', 'data': result})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
