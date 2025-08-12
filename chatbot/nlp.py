# chatbot/nlp.py

def parse_provision_request(text):
    """
    Parses text to extract user intent and VM parameters with improved validation.
    Returns a tuple: (params, error_message).
    """
    text_lower = text.lower()
    all_words = text_lower.split()

    # 1. --- Intent Recognition ---
    # Check if the user wants to create a VM at all.
    intent_keywords = ['provision', 'create', 'build', 'make', 'vm', 'server']
    if not any(keyword in text_lower for keyword in intent_keywords):
        error_msg = "Sorry, I didn't understand that. To create a VM, please use keywords like 'create', 'provision', or 'build'."
        return (None, error_msg)

    # 2. --- Define Supported Parameters ---
    supported_sizes = {
        'small': {'cpu': 1, 'memory_gb': 2},
        'medium': {'cpu': 2, 'memory_gb': 4},
        'large': {'cpu': 4, 'memory_gb': 8},
    }
    
    supported_os = {
        'rhel': 'Template-for-Terraform-Mark',
        # 'ubuntu': 'your-real-ubuntu-template-name',
        # 'centos': 'your-real-centos-template-name',
    }

    # 3. --- NEW: Smarter Parameter Parsing & Validation ---
    
    # -- Handle Size --
    found_size = None
    # Check if any word from the user's message is a potential size keyword.
    for word in all_words:
        # You can add more plausible but unsupported sizes here to catch them
        if word in supported_sizes or word in ['tiny', 'big', 'huge', 'giant', 'gigantic', 'humongous']:
            if word in supported_sizes:
                found_size = word
                break
            else:
                # The user specified a size, but it's not one we support.
                error_msg = f"Sorry, I don't recognize the size '{word}'. Supported sizes are: {', '.join(supported_sizes.keys())}."
                return (None, error_msg)
    # If after checking all words, no size was mentioned, use the default.
    final_size = found_size or 'small'

    # -- Handle OS --
    found_os = None
    for word in all_words:
        if word in supported_os:
            found_os = word
            break
    # If no OS was mentioned, use the default.
    final_os = found_os or 'rhel'

    # 4. --- Build Final Parameters ---
    params = supported_sizes[final_size].copy()
    params['image'] = supported_os[final_os]
    
    print(f"Parsed parameters: {params}")
    return (params, None) # Return params and no error