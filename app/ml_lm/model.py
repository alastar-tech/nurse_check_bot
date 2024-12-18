# predict.py

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

# Define the path to your saved model
# Get the current file's directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up one level to the app directory and then into saved_model
MODEL_PATH = os.path.join(os.path.dirname(CURRENT_DIR), 'ml_lm', 'saved_model')

# Load the tokenizer and model once when the script is imported
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    local_files_only=True
)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_PATH,
    local_files_only=True
)

# Set the model to evaluation mode
model.eval()

# If you have a GPU available and want to use it, uncomment the following lines
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model.to(device)

def analyze_text(text: str) -> int:
    """
    Predicts the label for a given text string.

    Args:
        text (str): The input text to classify.

    Returns:
        int: The predicted label (1 or 0).
    """
    # Tokenize the input text
    inputs = tokenizer(
        text,
        padding='max_length',       # Pad to max_length
        truncation=True,            # Truncate if longer than max_length
        max_length=512,             # Define max_length as per your training
        return_tensors="pt"         # Return PyTorch tensors
    )

    # If using GPU, move inputs to the same device as the model
    # inputs = {key: val.to(device) for key, val in inputs.items()}

    with torch.no_grad():
        # Get the model outputs
        outputs = model(**inputs)
        logits = outputs.logits

    # Apply softmax to get probabilities (optional)
    probabilities = torch.softmax(logits, dim=-1)

    # Get the predicted class
    predicted_class = torch.argmax(probabilities, dim=-1).item()

    return predicted_class

# Example usage
if __name__ == "__main__":
    sample_text = input("Your example text goes here.")
    prediction = analyze_text(sample_text)
    print(f"Input Text: {sample_text}")
    print(f"Predicted Label: {prediction}")
