# chatbot/nlp.py

def parse_provision_request(text):
    # Let's make your RHEL template the new default
    params = {
        'cpu': 1,
        'memory_gb': 2,
        'image': 'Template-for-Terraform-Mark'  # <-- UPDATED to your template name
    }
    
    # This map allows you to use keywords like "medium" or "large"
    size_map = {
        'tiny': {'cpu': 1, 'memory_gb': 1},
        'small': {'cpu': 1, 'memory_gb': 2},
        'medium': {'cpu': 2, 'memory_gb': 4},
        'large': {'cpu': 4, 'memory_gb': 8},
    }
    
    # This map allows you to use keywords for different OS templates in the future
    os_map = {
        # The 'rhel' keyword now correctly points to your template
        'rhel': 'Template-for-Terraform-Mark',   # <-- UPDATED to your template name
        # 'ubuntu': 'your-real-ubuntu-template-name', # You can add other templates here later
        # 'centos': 'your-real-centos-template-name',
    }
    
    # Process the text with our simple parser
    doc = text.lower() # No need for a complex NLP model here yet
    
    # Extract entities and update parameters
    for keyword, size_params in size_map.items():
        if keyword in doc:
            params.update(size_params)
            
    for keyword, image_name in os_map.items():
        if keyword in doc:
            params['image'] = image_name
            
    print(f"Parsed parameters: {params}")
    return params