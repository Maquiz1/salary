def calculate_paye(taxable_income):
    if taxable_income <= 270000:
        return 0
    elif taxable_income <= 520000:
        return (taxable_income - 270000) * 0.09
    elif taxable_income <= 760000:
        return 22500 + (taxable_income - 520000) * 0.20
    elif taxable_income <= 1000000:
        return 70500 + (taxable_income - 760000) * 0.25
    else:
        return 130500 + (taxable_income - 1000000) * 0.30

def calculate_salary(basic_salary, allowances=0, include_nssf=False, include_pssf=False, include_nhif=False, include_heslb=False, include_paye=True, custom_deductions=None):
    if custom_deductions is None:
        custom_deductions = []
    
    # Total earnings
    gross_pay = basic_salary + allowances
    
    # Statutory deductions are usually based on basic salary
    nssf = basic_salary * 0.10 if include_nssf else 0
    pssf = basic_salary * 0.05 if include_pssf else 0
    nhif = basic_salary * 0.03 if include_nhif else 0
    heslb = basic_salary * 0.15 if include_heslb else 0
    
    # Taxable income is Gross Pay minus pension contributions (NSSF or PSSF)
    taxable_income = gross_pay - nssf - pssf
    
    paye = calculate_paye(taxable_income) if include_paye else 0
    
    # Calculate custom deductions total
    custom_deductions_total = sum(d.get('amount', 0) for d in custom_deductions)
    
    total_deductions = nssf + pssf + nhif + heslb + paye + custom_deductions_total
    net_pay = gross_pay - total_deductions
    
    return {
        'basic_salary': basic_salary,
        'allowances': allowances,
        'gross_pay': gross_pay,
        'taxable_income': taxable_income,
        'nssf': nssf,
        'pssf': pssf,
        'nhif': nhif,
        'heslb': heslb,
        'paye': paye,
        'custom_deductions': custom_deductions,
        'custom_deductions_total': custom_deductions_total,
        'total_deductions': total_deductions,
        'net_pay': net_pay
    }

def calculate_gross_from_net(target_net, allowances=0, include_nssf=False, include_pssf=False, include_nhif=False, include_heslb=False, include_paye=True, custom_deductions=None):
    """
    Reverse calculates the basic salary required to reach a specific target net pay.
    Uses a simple binary search algorithm since the tax function is monotonically increasing.
    """
    low = 0
    high = target_net * 3  # Safe upper bound
    epsilon = 0.01
    
    # Binary search for the correct basic salary
    while high - low > epsilon:
        mid_basic = (low + high) / 2
        result = calculate_salary(
            basic_salary=mid_basic,
            allowances=allowances,
            include_nssf=include_nssf,
            include_pssf=include_pssf,
            include_nhif=include_nhif,
            include_heslb=include_heslb,
            include_paye=include_paye,
            custom_deductions=custom_deductions
        )
        
        if result['net_pay'] < target_net:
            low = mid_basic
        else:
            high = mid_basic
            
    return calculate_salary(
        basic_salary=(low + high) / 2,
        allowances=allowances,
        include_nssf=include_nssf,
        include_pssf=include_pssf,
        include_nhif=include_nhif,
        include_heslb=include_heslb,
        include_paye=include_paye,
        custom_deductions=custom_deductions
    )
