def factorial(num:int)-> int:
    ''' 
    Calculate n! useing recursion

    args:
        num(int): user input tha int number

    return:
        num(int):return the factorial

    '''
    if num == 0:
        return 1
    return num * factorial(num-1)

def is_prime(num:int)-> bool:
    '''
    Check for the number is prime or not

    args:
        num(int): number for check

    return:
        bool: True if the number is prime, False otherwise
    '''
    if num < 2:
        return False
        return False
    for i in range(2,num):
        if num % i == 0:
            return False
    return True

def common_divisor(num1:int,num2:int)-> list[int]:

    '''
    this function help to calc the common divisor

    args:
        num1(int): first number
        num2(int): second number

    return:
        list[int]: return the common divisor of two numbers

    '''
    limit = min(num1,num2)
    divisors = []
    for divisor in range(1, limit+1):
        if num1 % divisor == 0 and num2 % divisor == 0:
            divisors.append(divisor)
    return divisors
          