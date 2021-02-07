"""
Title: tests.py
Purpose: Lab 1 - UNHM COMP525
Author: Kyle Belouin
"""

import random
from my_array import MyArray


def main():
    """ This will be our main function.
    Includes python's random module: for the first test,
    this module will be used to generate random integers for the program,
    and also random size for our data set, from 1 to 1000 elements.
    In this function, a random list of integer values will be
    generated into array nums.
    Array class will be initialized with input1 as an argument.
    See README.md for attribution
    """

    #####
    # TEST1 - generate random data set and find max value.
    # Prints max value to the user.
    #####

    # set generation
    nums = []
    i = random.randint(1, 1000)
    while i < 1000:
        nums.append(random.randint(-1000, 1000))
        i += 1

    # class instantiation
    arr_object = MyArray(nums)

    # function calls
    arr_object.find_max()

    print(f"Test 1 - Maximum Value: {MyArray.max_val}")

    #####
    # TEST2 - pass an empty list into the MyArray class
    # and ensure graceful handling
    #####

    nums = []
    arr_object = MyArray(nums)
    arr_object.find_max()
    print(f"Test 2 - Empty set passed in and program handled it successfully")


if __name__ == '__main__':
    main()
