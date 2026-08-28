from django.test import TestCase
from .services import calculate_salary, calculate_paye, calculate_gross_from_net

class CalculatorServiceTest(TestCase):
    def test_paye_calculation(self):
        self.assertEqual(calculate_paye(250000), 0)
        self.assertEqual(calculate_paye(370000), 9000)
        self.assertEqual(calculate_paye(620000), 42500)
        self.assertEqual(calculate_paye(860000), 95500)
        self.assertEqual(calculate_paye(1500000), 280500)

    def test_calculate_salary(self):
        result = calculate_salary(
            basic_salary=1000000, 
            allowances=200000, 
            include_nssf=True, 
            include_paye=True
        )
        self.assertEqual(result['gross_pay'], 1200000)
        self.assertEqual(result['nssf'], 100000)
        self.assertEqual(result['taxable_income'], 1100000)
        self.assertEqual(result['paye'], 160500)
        self.assertEqual(result['net_pay'], 1200000 - 100000 - 160500)

    def test_calculate_salary_with_custom_deductions(self):
        result = calculate_salary(
            basic_salary=1500000, 
            allowances=375000, 
            include_nssf=True, 
            include_paye=True,
            custom_deductions=[{'name': 'MAAFA FUND', 'amount': 20000}]
        )
        self.assertEqual(result['custom_deductions_total'], 20000)
        
        # Gross = 1,875,000
        # nssf = 150,000
        # taxable = 1,725,000
        # paye = 130,500 + 725,000 * 0.3 = 348,000
        # total_deductions = 150000 + 348000 + 20000 = 518000
        # net = 1,875,000 - 518,000 = 1,357,000
        self.assertEqual(result['gross_pay'], 1875000)
        self.assertEqual(result['total_deductions'], 518000)
        self.assertEqual(result['net_pay'], 1357000)

    def test_calculate_gross_from_net(self):
        # We know from previous test: basic=1M, allow=200k, nssf=true, paye=true -> net=939500
        # Wait, if basic is known, gross is known. Net-to-Gross needs basic. 
        # If we specify net=939500, allowances=200000, it should find basic=1000000
        result = calculate_gross_from_net(
            target_net=939500,
            allowances=200000,
            include_nssf=True,
            include_paye=True
        )
        self.assertAlmostEqual(result['basic_salary'], 1000000, places=2)
