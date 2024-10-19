#app/utils.py

def display_grade_backend(combined_grade_value):
    
    if isinstance(combined_grade_value, str):
            try:
                combined_grade_value = int(combined_grade_value)
            except ValueError:
                return "Invalid Grade"  # Return an error message if conversion fails
            
    base_grade_value = combined_grade_value // 10  # Integer division to get the base grade
    decimal_value = int(combined_grade_value % 10)     # Modulo to get the decimal part

    # Map base grade value to climbing grade string
    grade_map = {
            0: "4a", 1: "4a+", 2: "4b", 3: "4b+", 4: "4c", 5: "4c+",
            6: "5a", 7: "5a+", 8: "5b", 9: "5b+", 10: "5c", 11: "5c+",
            12: "6a", 13: "6a+", 14: "6b", 15: "6b+", 16: "6c", 17: "6c+",
            18: "7a", 19: "7a+", 20: "7b", 21: "7b+", 22: "7c", 23: "7c+",
            24: "8a", 25: "8a+", 26: "8b", 27: "8b+", 28: "8c", 29: "8c+",
            30: "9a", 31: "9a+", 32: "9b", 33: "9b+", 34: "9c"
    }
        
    base_grade = grade_map.get(base_grade_value, "N.D.")
    
    return f"{base_grade}.{decimal_value}" if decimal_value >= 0 and base_grade != "N.D." else base_grade