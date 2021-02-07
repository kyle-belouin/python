"""
Title: my_array.py
Purpose: Lab 1 - UNHM COMP525
Author: Kyle Belouin
"""


class MyArray:
    """
    From this class we will process the array
    """

    def __init__(self, nums):
        """
        initialize input1 which is the set of integers
        created in and passed from test.py
        """
        self.num_list = nums

    def find_max(self):
        """
        Input: num_list - array of integers created and passed in from test.py
        Processing: this function loops through the array
        discovering maximum values as it iterates.
        Returns: max_val - the maximum value existing in the set,
        else NULL if there are none. This variable can be called from tests.py.
        See README.md for attribution
        """

        length = len(self.num_list)

        if length == 0:
            return None

        max_val = self.num_list[0]

        for i in self.num_list:
            if i > max_val:
                max_val = i

        return max_val
