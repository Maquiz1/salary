document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('calculator-form');
    const nssfToggle = document.getElementById('nssf');
    const pssfToggle = document.getElementById('pssf');
    const toggleCards = document.querySelectorAll('.toggle-input');

    // Handle mutually exclusive NSSF and PSSF
    nssfToggle.addEventListener('change', (e) => {
        if (e.target.checked) {
            pssfToggle.checked = false;
            updateToggleCardStyling();
        }
    });

    pssfToggle.addEventListener('change', (e) => {
        if (e.target.checked) {
            nssfToggle.checked = false;
            updateToggleCardStyling();
        }
    });

    // Handle styling for active toggle cards
    toggleCards.forEach(toggle => {
        toggle.addEventListener('change', updateToggleCardStyling);
    });

    function updateToggleCardStyling() {
        toggleCards.forEach(toggle => {
            const card = toggle.closest('.toggle-card');
            if (toggle.checked) {
                card.classList.add('active-card');
            } else {
                card.classList.remove('active-card');
            }
        });
    }

    // Initial styling setup
    updateToggleCardStyling();

    // Custom Deductions Logic
    const addDeductionBtn = document.getElementById('add-deduction-btn');
    const customDeductionsContainer = document.getElementById('custom-deductions-container');

    addDeductionBtn.addEventListener('click', () => {
        const row = document.createElement('div');
        row.className = 'custom-deduction-row';
        row.innerHTML = `
            <input type="text" class="custom-deduction-name" placeholder="Deduction Name (e.g. MAAFA)" required>
            <div class="input-with-icon" style="flex: 1;">
                <div class="icon">TZS</div>
                <input type="number" class="custom-deduction-amount" placeholder="Amount" required min="0">
            </div>
            <button type="button" class="btn-remove" aria-label="Remove">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
        `;
        customDeductionsContainer.appendChild(row);

        row.querySelector('.btn-remove').addEventListener('click', () => {
            row.remove();
        });
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btn = document.getElementById('submit-btn');
        const btnText = btn.querySelector('span');
        const loader = btn.querySelector('.loader');
        
        // Show loading state
        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        btn.disabled = true;

        const formData = new FormData(form);
        const customDeductions = [];
        document.querySelectorAll('.custom-deduction-row').forEach(row => {
            const name = row.querySelector('.custom-deduction-name').value;
            const amount = parseFloat(row.querySelector('.custom-deduction-amount').value) || 0;
            if (name && amount > 0) {
                customDeductions.push({ name, amount });
            }
        });

        const data = {
            salary_type: formData.get('salary_type'),
            amount: parseFloat(formData.get('amount')) || 0,
            allowances: parseFloat(formData.get('allowances')) || 0,
            nssf: formData.get('nssf') === 'on',
            pssf: formData.get('pssf') === 'on',
            paye: formData.get('paye') === 'on',
            heslb: formData.get('heslb') === 'on',
            nhif: formData.get('nhif') === 'on',
            custom_deductions: customDeductions
        };

        try {
            const response = await fetch('/api/calculate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                displayResults(result.data);
            } else {
                alert('An error occurred during calculation: ' + (result.message || 'Unknown error'));
            }
        } catch (error) {
            alert('Failed to connect to the server.');
            console.error(error);
        } finally {
            // Restore button state
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            btn.disabled = false;
        }
    });

    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-TZ', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount) + ' TZS';
    }

    function displayResults(data) {
        const resSection = document.getElementById('result-section');
        
        // Update DOM elements
        document.getElementById('res-net-pay').textContent = formatCurrency(data.net_pay);
        document.getElementById('res-basic').textContent = formatCurrency(data.basic_salary);
        document.getElementById('res-allowances').textContent = formatCurrency(data.allowances);
        document.getElementById('res-gross').textContent = formatCurrency(data.gross_pay);
        document.getElementById('res-taxable').textContent = formatCurrency(data.taxable_income);
        
        // Deductions (show/hide based on whether they were > 0)
        updateDeductionRow('nssf', data.nssf);
        updateDeductionRow('pssf', data.pssf);
        updateDeductionRow('paye', data.paye);
        updateDeductionRow('heslb', data.heslb);
        updateDeductionRow('nhif', data.nhif);
        // Custom Deductions
        const customContainer = document.getElementById('res-custom-deductions');
        customContainer.innerHTML = '';
        if (data.custom_deductions && data.custom_deductions.length > 0) {
            data.custom_deductions.forEach(deduction => {
                const row = document.createElement('div');
                row.className = 'breakdown-item';
                row.innerHTML = `<span>${deduction.name}</span><span>${formatCurrency(deduction.amount)}</span>`;
                customContainer.appendChild(row);
            });
        }
        
        document.getElementById('res-total-deductions').textContent = formatCurrency(data.total_deductions);
        
        // Show result section if hidden, otherwise re-trigger animation
        resSection.classList.remove('hidden');
        resSection.style.animation = 'none';
        resSection.offsetHeight; // trigger reflow
        resSection.style.animation = null;
        
        // Scroll to results on mobile
        if (window.innerWidth < 768) {
            resSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    function updateDeductionRow(id, amount) {
        const row = document.getElementById(`row-${id}`);
        const valSpan = document.getElementById(`res-${id}`);
        
        if (amount > 0 || (id === 'paye' && document.getElementById('paye').checked)) {
            row.style.display = 'flex';
            valSpan.textContent = formatCurrency(amount);
        } else {
            row.style.display = 'none';
        }
    }
});
