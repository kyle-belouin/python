"""
File: ./tests/test_salary_stats_by_job_satisfaction.py
Starter: Mihaela
Developer: Kyle Belouin
Updated : April 3, 2021
"""
import unittest
import os
import sys
from src.analysis import Analysis

# Specifies the absolute path to the src package
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)


class TestSalaryStatsByJobSatisfaction(unittest.TestCase):
    """
    Tests programming_language_popularity() method
    """
    def test_multiple_entries(self):
        """
        Test case 1 using stats.txt.
        Will verify that three elements return for key Ext. dissatisfied
        """
        input1 = '../data/stats_10.txt'
        devs_obj = Analysis(input1)
        print(f'{devs_obj.salary_and_job_satisfaction()}')

    def test_ten_entries(self):
        """
        Test case 2 using stats_10.txt with ten rows
        """
        input1 = '../data/stats_10.txt'
        devs_obj = Analysis(input1)
        actual_result = len(
            devs_obj.salary_and_job_satisfaction().__getitem__(
                'Extremely satisfied'
            )
        )
        expected_result = 3
        print(f'{devs_obj.salary_and_job_satisfaction()}')
        self.assertEqual(actual_result, expected_result)

    def test_empty_file(self):
        """
        Test case 3 using stats_empty.txt
        """
        input1 = '../data/stats_empty.txt'
        devs_obj = Analysis(input1)
        actual_result = devs_obj.salary_and_job_satisfaction()
        expected_result = {}
        self.assertEqual(actual_result, expected_result)

    def test_one_entry(self):
        """
        Test case 4 using stats_1.txt with one row
        """
        input1 = '../data/stats_1.txt'
        devs_obj = Analysis(input1)
        actual_result = (
            len(
                devs_obj.salary_and_job_satisfaction().__getitem__(
                    'Moderately satisfied'
                )
            )
        )
        expected_result = 3
        self.assertEqual(actual_result, expected_result)


if __name__ == '__main__':
    unittest.main()