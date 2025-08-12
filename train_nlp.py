# train_nlp.py
import spacy
import random
from spacy.training.example import Example

# Define your training data. The more examples you add, the smarter the model will be.
# Format: (text, {"entities": [(start_character, end_character, "ENTITY_LABEL")]})
TRAIN_DATA = [
    ("provision a small rhel server", {"entities": [(14, 19, "VM_SIZE"), (20, 24, "VM_OS")]}),
    ("I need a medium rhel vm", {"entities": [(9, 15, "VM_SIZE"), (16, 20, "VM_OS")]}),
    ("build a large rhel machine", {"entities": [(8, 13, "VM_SIZE"), (14, 18, "VM_OS")]}),
    ("can you make a small rhel instance", {"entities": [(15, 20, "VM_SIZE"), (21, 25, "VM_OS")]}),
    ("I want a medium rhel server please", {"entities": [(9, 15, "VM_SIZE"), (16, 20, "VM_OS")]}),
    ("create a large rhel virtual machine", {"entities": [(9, 14, "VM_SIZE"), (15, 19, "VM_OS")]}),
    ("a small rhel vm is what I need", {"entities": [(2, 7, "VM_SIZE"), (8, 12, "VM_OS")]}),
    ("let's build a medium rhel box", {"entities": [(13, 19, "VM_SIZE"), (20, 24, "VM_OS")]}),
    ("get me a large rhel instance", {"entities": [(9, 14, "VM_SIZE"), (15, 19, "VM_OS")]}),
    ("I'd like a small rhel server", {"entities": [(11, 16, "VM_SIZE"), (17, 21, "VM_OS")]}),
    ("provision one medium rhel machine", {"entities": [(14, 20, "VM_SIZE"), (21, 25, "VM_OS")]}),
    ("make a large redhat enterprise linux server", {"entities": [(7, 12, "VM_SIZE"), (13, 37, "VM_OS")]}),
    ("a request for a small rhel vm", {"entities": [(16, 21, "VM_SIZE"), (22, 26, "VM_OS")]}),
    ("spin up a medium rhel server", {"entities": [(11, 17, "VM_SIZE"), (18, 22, "VM_OS")]}),
    ("build me a large rhel environment", {"entities": [(11, 16, "VM_SIZE"), (17, 21, "VM_OS")]}),
    ("I just need a small redhat instance", {"entities": [(15, 20, "VM_SIZE"), (21, 27, "VM_OS")]}),
    ("can I get a medium server using rhel", {"entities": [(12, 18, "VM_SIZE"), (30, 34, "VM_OS")]}),
    ("a large vm running redhat", {"entities": [(2, 7, "VM_SIZE"), (19, 25, "VM_OS")]}),
    ("please provision a small rhel", {"entities": [(19, 24, "VM_SIZE"), (25, 29, "VM_OS")]}),
    ("create a medium rhel system", {"entities": [(9, 15, "VM_SIZE"), (16, 20, "VM_OS")]}),
]

def train_spacy_ner(data, iterations=30):
    """Creates, trains, and saves a custom spaCy NER model."""
    # Start with a blank English model
    nlp = spacy.blank("en")
    
    # Create a new NER component and add it to the pipeline
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    
    # Add the custom entity labels to the NER component
    for _, annotations in data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    print("Starting training...")
    # Training the NER component
    with nlp.disable_pipes(*[pipe for pipe in nlp.pipe_names if pipe != "ner"]):
        optimizer = nlp.begin_training()
        for itn in range(iterations):
            random.shuffle(data)
            losses = {}
            for text, annotations in data:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                nlp.update([example], drop=0.35, sgd=optimizer, losses=losses)
            print(f"Iteration {itn+1}/{iterations}, Losses: {losses}")

    # Save the trained model to a directory
    output_dir = "./nlp_model"
    nlp.to_disk(output_dir)
    print(f"✅ Model saved to '{output_dir}'")

if __name__ == "__main__":
    train_spacy_ner(TRAIN_DATA)