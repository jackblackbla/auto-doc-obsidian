def calculate_sum(numbers):
    """Calculate the sum of a list of numbers."""
    return sum(numbers)

def calculate_average(numbers):
    """Calculate the average of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def format_currency(amount):
    """Format a number as currency."""
    return f"${amount:,.2f}"