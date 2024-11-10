from src.utils.full_path import get_full_path
import platform

def test_get_full_path_with_valid_relative_path():
    # Arrange
    relative_path = "src/utils/full_path.py"

    bando_absolute_path = "C:\\Users\\miche\\SecondBrain\\2_Projects\\02242_Program_Analysis\\PyJavaTaint\\src\\utils\\full_path.py"
    mathias_absolute_path = ""
    
    # Get the operating system
    if platform.system() == "Windows":
        absolute_path = bando_absolute_path
    elif platform.system() == "Linux":
        absolute_path = mathias_absolute_path
    
    # Assert
    assert get_full_path(relative_path) == absolute_path