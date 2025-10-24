# Evolving Lyrics - A Genetic Algorithm Session in Python
# (c) Seth Bullock, Nov 2024

"""
Open this Google sheet in your browser:
https://docs.google.com/spreadsheets/d/1p3ki5l2rhcYwEzAx8xBEOTjqZGm4IWhGv1l7QBTdPG8/
or: https://tinyurl.com/EvolvingLyrics for short

Read the instructions in the "Instructions" tab of the Google Sheet.
Notice that there are a series of Tasks to complete - each in its own tab.
"""

# ----------------------------------------------------------------------------------------

# Our genetic algorithm (GA) is executed by calling ..
#       do_the_ga()
# .. which we import from lyric_ga.py:

from lyric_ga import do_the_ga

# Calling do_the_ga() with no arguments runs a "vanilla" version of the genetic algorithm
# which tries to evolve a specific line of Shakespeare: "Ham. Methinks it is like a weasel."

do_the_ga()                         # this calls the Python code that runs the GA
exit()                              # this halts the execution of code in this file

# To run the code in this file, use the command:
#        python3.9 evolving_lyrics.py
# on the Linux terminal command line

"""
In its basic form the GA probably won't quite manage to solve the problem completely.

By passing different arguments to the function we can try to improve its performance.

The full list of arguments that the function can take is listed below.

The Tasks on each tab within the Google Sheet walk you through exploring what they do.
"""

# ----------------------------------------------------------------------------------------

"""
The "vanilla" version of the GA executes a genetic algorithm with:
- a population of 100 strings, each of length 34
- that evolves for 2000 generations
- with a fixed target, the string: "Ham. methinks it is like a weasel."
- (which is a line from Shakespeare's play, Hamlet)

The arguments and their default values for the do_the_ga() function in lyric_ga.py:

  do_the_ga(author="Shakespeare", target="Ham. Methinks it is like a weasel.",
            length=25, pop_size=100, max_gen=2000, write_every=1, 
            pressure=1, crossover=0.0, elitism=False, converged=False)

  author: can be set to "swift", "beatles" or "shakespeare" (the default)

  target: can either be None or a specific string (like "Ham. Methinks it is like a weasel.")
          (if target is None, the GA will try to evolve *any* line by the specified author)
  
  length: if target=None, length sets the length of the strings being evolved (default=25)
          (very small or large lengths might not work very well; between 10 and 35 should be ok)
  
  pop_size: defines the number of individuals in each generation during evolution (default=100)
  
  max_gen: defines how many generations of evolution should take place (default is 2000)

  write_every: progress so far is written every write_every generations (default=1; write every generation)

  elitism: True or False (default is False) - specifies whether the GA uses elitism or not
  
  crossover: the probability (between 0.0 and 1.0) that offspring result from sexual crossover (default=0.0)

  pressure: an integer between 0 and pop_size-1 (default is 1) - controls the "strength of selection"
            (pressure=0 means no selection for fitter parents; pressure=10 means extremely strong selection)

  converged: True or False - specifies if the initial generation should contain identical solutions or not 
"""

# this evolves a 25-character Taylor Swift lyric using Elitism + Crossover + higher than usual Selection Pressure
do_the_ga(author="taylor", target=None, length=25, elitism=True, crossover=0.5, pressure=3)
exit() # this exits the code - nothing below this line will be executed

'''
  Tasks 1, 2, 3, 4, and 5 can *all* be achieved by editing the do_the_ga() call above
  and running the Python script from the Linux command line using the command:

  python3.9 evolving_lyrics.py
'''

# ----------------------------------------------------------------------------------------

'''
You don't need to scroll down here until Task 6!

When you are ready for Task 6, comment out all the lines of active Python above this line...

'''

# ----------------------------------------------------------------------------------------

# Our new lyrics genetic algorithm (GA) is also executed by calling ..
#       do_the_ga()
# .. which we import from a different file: new_lyric_ga.py

# from new_lyric_ga import do_the_ga

# Before calling do_the_ga() we can design the fitness function that the code will use and
# also specify the mix of genetic operators (mutation and crossover) that the code will use.

# The my_fitness_recipe dictionary's key-value pairs control how fitness is influenced by...
my_fitness_recipe = {
    "LP": 20,   # ...the no. Legal Pairs in solution
    "IP": -25,  # ...the no. Illegal Pairs in solution
    "CP": 100,   # ...the no. Consecutive legal Pairs in solution

    "LT": 100,  # ...the no. Legal Triples in solution
    "IT": -1,    # ...the no. Illegal Triples in solution
    "CT": 50,  # ...the no. Consecutive legal Triples in solution

    "MF": 0,    # ...the Mean Frequency of the words in the solution
    "SF": 0,    # ...the St.dev. of word Frequencies in the solution
    "RF": 0     # ...the Range of word Frequencies in the solution
}
# nb. weights can be given any numeric value, positive or negative, e.g., 10, 100, -1, 0.5
#     a weight value of zero means that that factor doesn't influence fitness at all

# If you are interested in changing the genetic operators to try to get better lyrics,
# set the rates in the following two dictionaries...
my_mutation_operator_rates = {
    "point_rate" : 100, # the rate of (standard) point mutations
    "insert_rate":   0, # the rate of word insertion* mutations
    "delete_rate":   0, # the rate of word deletion* mutations
    "extend_rate":   0  # the rate of string extension* mutations
}

my_crossover_operator_rates = {
    "one-pt" : 50, # the rate of one-point crossover
    "two-pt" : 0, # the rate of two-point crossover
    "four-pt": 0  # the rate of four-point crossover*
}
# nb. rates can be given any positive numeric value, e.g., 10, 100, 1, 0
#     *this genetic operator changes the length of the offspring solution...

do_the_ga()                         # this runs the vanilla version of the new do_the_ga()
exit()                              # this exits the code - nothing below this line will be executed

# this runs the new do_the_ga using your own fitness recipe, and genetic operators
do_the_ga(author="taylor", length=10,
          fitness_recipe=my_fitness_recipe,
          mutation_operator_rates = my_mutation_operator_rates,
          crossover_operator_rates = my_crossover_operator_rates)
exit()                              # this exits the code - nothing below this line will be executed

# you can also set the initial length of the lyric, and specify elitism, etc., as before
# the default arguments are:
#  author="taylor", pop_size=100, pressure=3,
#  crossover=0.0, length=15, elitism=False,
#  max_gen=500, converged=False, write_every=1

# Experiment with different fitness recipes and different mies of genetic operators
# to try to evolve the most convincing/interesting lyrics
