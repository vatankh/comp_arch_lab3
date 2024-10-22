def sum_of_multiples(upper_limit):
    """
    Returns the sum of all numbers below the upper limit
    that are divisible by 3 or 5.
    """
    total_sum = 0
    for number in range(1, upper_limit):
        if number % 3 == 0 or number % 5 == 0:
            total_sum += number
    return total_sum

# Test with an upper limit
upper_limit = 1000  # You can change this value to test other cases
result = sum_of_multiples(upper_limit)
print(f"The sum of multiples of 3 or 5 below {upper_limit} is {result}")