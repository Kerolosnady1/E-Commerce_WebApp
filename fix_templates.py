import os

templates_dir = r'e:\Projects\E-Commerce_WebApp\templates'
files_to_fix = [
    'bulk_purchase_confirm.html', 'category_form.html', 'customer_form.html', 
    'inventory_form.html', 'notification_form.html', 'privacy_policy.html', 
    'product_form.html', 'purchase_order_form.html', 'supplier_form.html', 
    'support.html', 'tax_confirm_delete.html', 'tax_form.html', 
    'terms_of_service.html', 'user_edit_form.html', 'user_form.html'
]

for filename in files_to_fix:
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the incorrectly escaped version with the correct version
    bad_include = "{% include \\'_navbar.html\\' %}"
    good_include = '{% include "_navbar.html" %}'
    
    if bad_include in content:
        new_content = content.replace(bad_include, good_include)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed quotes in {filename}')
