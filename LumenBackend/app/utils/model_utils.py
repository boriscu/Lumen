from typing import Optional, Any
import os
from joblib import load


def load_model(model_path: Optional[str] = "models/model.joblib") -> Optional[Any]:
    """
    Loads a machine learning model from the specified path.

    This function attempts to load a machine learning model from a .joblib file
    located at the specified path. If the file does not exist, it logs an error message
    and returns None.

    Parameters:
    - model_path (str, optional): The path to the .joblib file containing the model.
                                  Defaults to "models/model.joblib".

    Returns:
    - The loaded model if the file exists and is successfully loaded; otherwise, None.
    """
    if not os.path.exists(model_path):
        print(f"Error: The model file at {model_path} does not exist.")
        return None

    try:
        model = load(model_path)
        return model
    except Exception as e:
        print(f"Error loading the model: {e}")
        return None
