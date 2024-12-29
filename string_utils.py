def reverse_string(text):
    """Reverse a string."""
    return text[::-1]

def count_words(text):
    """Count words in a text."""
    return len(text.split())

def capitalize_words(text):
    """Capitalize first letter of each word."""
    return ' '.join(word.capitalize() for word in text.split())