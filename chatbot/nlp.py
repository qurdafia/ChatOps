# chatbot/nlp.py
import spacy
import os

# Load our custom-trained model from the 'nlp_model' directory
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'nlp_model')
NLP_MODEL = spacy.load(MODEL_PATH)

def parse_provision_request(text):
    """
    Parses text using a custom spaCy NER model to extract intent and parameters,
    while also handling simple conversational phrases.
    Returns a tuple: (params, message).
    """
    text_lower = text.lower().strip()

    # 1. --- NEW: Handle Conversational Keywords First ---
    if text_lower in ["hello", "hi", "hey"]:
        reply = "Hi, I hope you're doing well! Please let me know what size or OS of server you want me to provision."
        return (None, reply)

    if "thank you" in text_lower or "thanks" in text_lower:
        reply = "You're welcome! It's my pleasure to help you. Have a nice day."
        return (None, reply)
    # ---------------------------------------------------

    # 2. --- Intent Recognition for Provisioning ---
    intent_keywords = ['provision', 'create', 'build', 'make', 'vm', 'server']
    if not any(keyword in text_lower for keyword in intent_keywords):
        error_msg = "Sorry, I didn't understand that. To create a VM, please use keywords like 'create', 'provision', or 'build'."
        return (None, error_msg)

    # 3. --- Define Supported Parameters ---
    size_map = {
        'small': {'cpu': 1, 'memory_gb': 2},
        'medium': {'cpu': 2, 'memory_gb': 4},
        'medium-sized': {'cpu': 2, 'memory_gb': 4},
        'large': {'cpu': 4, 'memory_gb': 8},
        'big': {'cpu': 4, 'memory_gb': 8},
        'tiny': {'cpu': 1, 'memory_gb': 1},
    }
    os_map = {
        'rhel': 'Template-for-Terraform-Mark',
        'redhat': 'Template-for-Terraform-Mark',
        'red hat enterprise linux': 'Template-for-Terraform-Mark',
        # 'ubuntu': 'your-real-ubuntu-template-name',
        # 'centos': 'your-real-centos-template-name',
    }

    # 4. --- Use the spaCy model to find entities ---
    doc = NLP_MODEL(text_lower)
    
    found_size = None
    found_os = None

    for ent in doc.ents:
        print(f"Found entity: '{ent.text}', Label: '{ent.label_}'")
        if ent.label_ == "VM_SIZE":
            found_size = ent.text
        elif ent.label_ == "VM_OS":
            found_os = ent.text

    # 5. --- Validate and Build Parameters ---
    if found_size and found_size not in size_map:
        error_msg = f"Sorry, I don't support the size '{found_size}'. Supported sizes are: {', '.join(size_map.keys())}."
        return (None, error_msg)
        
    if found_os and found_os not in os_map:
        error_msg = f"Sorry, I don't support the OS '{found_os}'. Supported OS are: {', '.join(os_map.keys())}."
        return (None, error_msg)

    # Use found entities or fall back to defaults
    final_size_key = found_size or 'small'
    final_os_key = found_os or 'rhel'

    params = size_map[final_size_key].copy()
    params['image'] = os_map[final_os_key]

    print(f"Parsed parameters: {params}")
    return (params, None)