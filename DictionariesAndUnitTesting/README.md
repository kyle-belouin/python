### race_ethnicity_by_country()
```
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
```
Several steps must occur to break down the data we need to process, to be able to return the desired output.

First - A list of possible ethnicities, pertinent to our data set, is defined.
(derived by hand from source files) as `ethnicities`.
This list is iterated through and on each iteration, we start populating the keys of our dictionary
(`race_ethnicity_by_country_d`) from this list using built-in `dict` methods.

Second - For each entry in our `self.devs` list of dictionaries, we will iterate. On each iteration:
  1. We get a semi-colon delimited list of languages used/known for a given student.
     This is 'split' using python built-in string method `split` into an easily workable, simple python built-in list.
     This populates a new list, named `ethnicity`.
  2. With a workable list, it is then iterated through. The list only includes the list of ethnicities in our data set,
     so this list can be used to iterate through our dictionary, using the known languages
     as keys - in other terms, we have identified the keys that we need to work with and will only work with them.
  3. Now with this all set up, conditionals check each key that will be iterated through to see if the associated value
     is None or not. If it is none, none is replaced by one, otherwise for all future iterations, the value simply increments.
  4. Upon completion of these loops, we return the now populated dictionary with all student's data aggregated together.

### salary_and_job_satisfaction()
```
def salary_and_job_satisfaction(self):
    """
    Creates and returns a dictionary that has stats info regarding
    salaries found based on the JobSataisfaction key the dictionary
    elements of the self.devs list

    Returns: dictionary
       keys: job satisfaction descriptors, of type string
       values: lists of 3 numbers: min salary, max salary, and mean salary
    """
```
This method requires a several operations.
1) First, keys are populated in the `salary_by_job_s_d` dictionary by iterating over defined items in list `ratings`.
2) Our source data is iterated through, and we discover each student's job satisfaction and converted salary.
  * each of these is an int and float respectively, and named `satisfaction` and `salary` respectively.
  * After defining these variables, our `salary_by_job_s_d` dictionary receives appended values in its list,
  based on key.
3) A `final_dict` dictionary is created and its purpose is to aggregate the data we have entered into
   `salary_by_job_s_d`. It's output will be minimum, maximum, and mean values derived from the lists of data that exist
   with each key.
   * A special check is done to see if a data set for any particular key is empty, if it is, we cannot
   compute the mathematical output required. As such, a string is appended to the list on the key in
   the `salary_by_job_s_d` dictionary noting that no relevant data existed.
   * If data does exist in our lists in the dictionary, our math outputs are derived using built-in operators for `min`
     and `max`, `mean` is a calculation of the sum of all values in the list per a given key,
     divided by the list's length.
4) Finally, the `final_dict` object is returned containing the min, max, and mean values,
   per key of `salary_by_job_s_d`, that we need.

### language_popularity()
```
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
```
Several steps must occur to break down the data we need to process, to be able to return the desired output.

First - A list of possible languages is defined, (derived by hand from source files) as `languages`.
This list is iterated through and on each iteration, we will start populating the keys of our dictionary (`prog_lang_d`)
from this list using built-in `dict` methods.

Second - For each entry in our `self.devs` list of dictionaries, we will iterate. On each iteration:
  1. We get a semi-colon delimited list of languages used/known for a given student.
     This is 'split' using python built-in string method `split` into an easily workable, simple python built-in list.
     This populates a new _intrinsically_ typed variable, a list, named `langs_worked_with`.
  2. With a workable list, it is then iterated through. The list only includes the list of languages
     that a student has used, so this list can be used to iterate through our dictionary, using the known languages
     as keys - in other terms, we have identified the keys that we need to work with and will only work with them.
  3. Now with this all set up, conditionals check each key that will be iterated through to see if the associated value
     is None or not. If it is none, incrementation is performed here, otherwise the value simply increments.
  4. Upon completion of these loops, we return the now populated dictionary with all student's data aggregated together.

### __str__()
```
def __str_(self):
    """
    Returns string representation of the list self.devs, which contains
    dictionary elements corresponding the rows in the data file.
    """
```
This method simply returns the string representation of `self.devs` upon being called.

<br>

Attribution:
* string splitting: https://python-reference.readthedocs.io/en/latest/docs/str/split.html
* working with dictionaries within a list:
https://canvas.instructure.com/courses/1133362/pages/book-5-dot-4-python-combining-lists-and-dictionaries
