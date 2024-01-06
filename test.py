def convert_string_to_number(string):
    """
    This function takes a string representing a number in the specific format "Current Digit 100, Current Digit 10, 
    Current Digit 1, Current Digit 0.1" and converts it back to the original number (float or int).

    The input string is expected to be 4 characters long, representing the digits at the 100s, 10s, 1s, and 0.1s places respectively.

    :param string: The string to be converted
    :return: The original number as a float or int
    """
    # Extract the digits from the string
    digit_100 = int(string[0]) * 100
    digit_10 = int(string[1]) * 10
    digit_1 = int(string[2])
    digit_01 = int(string[3]) / 10

    # Sum the values to get the original number
    original_number = digit_100 + digit_10 + digit_1 + digit_01

    # Return the number as an integer if it is a whole number, otherwise return as float
    return int(original_number) if original_number.is_integer() else original_number

# Example usage
example_string = "0321"
reconverted_number = convert_string_to_number(example_string)
reconverted_number