"""
./src/analysis.py
Starter: Mihaela
Developer: Kyle Belouin
Updated: April 3, 2021
"""
# Specifies the absolute path to the current package, src, which has
# analysis.py module
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
)


class Analysis:
    """
    Analyze developer data
    """
    def __init__(self, filename):
        """
        Initializes self.devs list with dictionary objects.
        A dictionary object has:
            keys: strings from the fields in the 1st row of the text file
            values: strings with information corresponding to the keys
        """
        self.devs = []
        try:
            with open(filename, 'r') as fin:
                first_line = fin.readline()[:-1]  # exclude last char, \n
                keys_lst = first_line.split('|')
        except IOError as err:
            print(err)
        try:
            with open(filename, 'r') as fin:
                for line in fin.readlines()[1:]:
                    # exclude last char, '\n', from line before splitting it
                    # by '|' to get the list of strings corresponding to each
                    # cell
                    values_lst = line[:-1].split('|')
                    dev_d = dict(zip(keys_lst, values_lst))
                    self.devs.append(dev_d)
        except IOError as err:
            print(err)

    def race_ethnicity_by_country(self):
        """
        Creates and returns a dictionary that has race/ethnicity information by
        country from analyzing the Country key of the dictionary elements in
        the self.devs
        Returns: dictionary
            keys: country names, of type string
            values: lists of strings, each string corresponding to
                race/ethnicity information associated with a country
        """
        race_ethnicity_by_country_d = {}
        if len(self.devs) == 0:  # if we get an empty list, do nothing.
            return race_ethnicity_by_country_d

        ethnicities = [
            "Black or of African descent",
            "Hispanic or Latino/Latina",
            "White or of European descent",
            "East Asian",
            "South Asian",
            "Middle Eastern",
            "Native American",
            "Pacific Islander",
            "Indigenous Australian"
        ]

        for elem in ethnicities:
            race_ethnicity_by_country_d.setdefault(elem)
            # populates keys based on possible ethnicities

        for student in self.devs:
            ethnicity = student['RaceEthnicity'].split(';')
            for elem in ethnicity:
                get_val = race_ethnicity_by_country_d.get(elem)
                if get_val is None:
                    race_ethnicity_by_country_d.__setitem__(elem, 1)
                else:
                    set_val = (get_val + 1)
                    race_ethnicity_by_country_d.__setitem__(elem, set_val)
        return race_ethnicity_by_country_d

    def salary_and_job_satisfaction(self):
        """
        Creates and returns a dictionary that has stats info regarding
        salaries found based on the JobSatisfaction key in the dictionary
        elements of the self.devs list
        Returns: dictionary
           keys: job satisfaction descriptors, of type string
           values: lists of 3 numbers: min salary, max salary, and mean salary
        """

        salary_by_job_s_d = {}
        if len(self.devs) == 0:  # if we get an empty list, do nothing.
            return salary_by_job_s_d

        ratings = [
            "Extremely dissatisfied",
            "Extremely satisfied",
            "Moderately dissatisfied",
            "Moderately satisfied",
            "Neither satisfied nor dissatisfied",
            "Slightly dissatisfied",
            "Slightly satisfied"
        ]

        for elem in ratings:  # first, set up keys in dict, each with empty lists
            salary_by_job_s_d.setdefault(elem, [])

        for student in self.devs:  # then, iterate through our imported data
            satisfaction = student['JobSatisfaction']  # set our key
            salary = float(student['ConvertedSalary'])  # float, otherwise they are strings
            salary_by_job_s_d[satisfaction].append(salary)  # append salary based on key

        final_dict = {}  # this will contain min, max, and mean values of data.
        for elem in salary_by_job_s_d.keys():
            final_dict.setdefault(elem, [])

        for key in salary_by_job_s_d.keys():
            if len(salary_by_job_s_d.get(key)) == 0:
                final_dict[key].append('Empty data set - no min, max, or mean')
            else:
                final_dict[key].append(min(salary_by_job_s_d[key]))
                final_dict[key].append(max(salary_by_job_s_d[key]))
                final_dict[key].append(  # styling hack :)
                    round(
                        sum(salary_by_job_s_d[key]) / len(salary_by_job_s_d[key]), 2
                    )
                )

        return final_dict

    def language_popularity(self):
        """
        Creates and returns a dictionary that has the frequencies of each
        programming language found based on the LanguageWorkedWith key in
        the dictionary elements of the self.devs list
        Returns: dictionary
           keys: programming language names, of type string
           values integers, representing the frequency of corresponding
            programming language
        """
        prog_lang_d = {}
        if len(self.devs) == 0:  # if we get an empty list, do nothing.
            return prog_lang_d

        languages = [
            "C",
            "C#",
            "CoffeeScript",
            "JavaScript",
            "Objective-C",
            "PHP",
            "Swift",
            "HTML",
            "CSS",
            "Bash/Shell",
            "Ruby",
            "Go",
            "SQL",
            "TypeScript",
            "Groovy",
            "Java",
            "Haskell",
            "Ocaml",
        ]

        for elem in languages:  # first, set up keys in dict from languages list
            prog_lang_d.setdefault(elem)

        for student in self.devs:  # then, iterate through all entries in our data set
            langs_worked_with = student['LanguageWorkedWith'].split(';')
            # ^ splits output received from entry into iterable list
            for elem in langs_worked_with:  # iterates through our nicely split list
                get_val = prog_lang_d.get(elem)  # first, check what value exists with our key
                if get_val is None:
                    # get us started by changing None to 1 if a language count needs to increment
                    prog_lang_d.__setitem__(elem, 1)
                else:  # increment if an integer exists
                    set_val = (get_val + 1)
                    prog_lang_d.__setitem__(elem, set_val)
        return prog_lang_d

    def __str__(self):
        """
        Returns string representation of the list self.devs, which contains
        dictionary elements corresponding the rows in the data file.
        """
        return self.devs.__str__()


def main():
    """
    Testing constructor
    """
    dev_obj = Analysis('../data/stats_10.txt')
    print(f'dev_obj has {len(dev_obj.devs)} elements')
    print(str(dev_obj.devs))


if __name__ == '__main__':
    main()