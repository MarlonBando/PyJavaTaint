from src.taint_detector import *

def test_is_tainted_with_matching_signature():
    # Arrange
    test_signature = "java/util/Scanner/nextLine"
    
    # Act
    result = is_tainted(test_signature)
    
    # Assert
    assert result == True

def test_is_tainted_with_non_matching_signature():
    # Arrange 
    test_signature = "some/nonexistent/method"
    
    # Act
    result = is_tainted(test_signature)
    
    # Assert
    assert result == False

def test_is_tainted_with_empty_signature():
    # Arrange
    test_signature = ""
    
    # Act 
    result = is_tainted(test_signature)
    
    # Assert
    assert result == False

