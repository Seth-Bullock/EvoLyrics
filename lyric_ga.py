import random       # from the 'random' library, we will use "seed", "choice", "sample", "randrange", "random"
import pickle       # we'll use this library to read in the lyric corpus

import streamlit as st

# Initialise the GA population
#   Fill an empty population array with N = pop_size random individuals
#   Each individual is represented by a Python dictionary with two elements: "solution" and "fitness"
#     each "fitness" is initialised to <None> as the associated solution has not yet been assessed
#     each "solution" is initialised to a string of random symbols from the alphabet
#     if converged is True, each "solution" is the same string of random characters
#     if converged is False, each "solution" is an independent string of random characters
def initialise(pop_size, length, alphabet, converged=False):

    pop = []

    if converged:
        solution = "".join([random.choice(alphabet) for _ in range(length)])
        while len(pop)<pop_size:
            pop.append({"fitness": None, "solution": solution})
    else:
        while len(pop)<pop_size:
            solution = "".join([random.choice(alphabet) for _ in range(length)])
            pop.append({"fitness":None, "solution":solution})

    return pop


# Count the number of locations for which two strings of the same length match.
#   E.g, match for "red", "rod" should be 2.
def match(str1, str2):
    return sum(str1[i]==str2[i] for i in range(len(str1)))


# Assign a fitness score to a solution by finding the line that is the closest
#   match to the solution
#   The score is the number of characters that match
def get_fitness(solution, lines, length):
    fitness = 0
    for line in lines:
        score = match(solution, line)
        if score>fitness:
            fitness=score
    return fitness/length

# Assess the fitness of each individual in the current population
#   For each individual, count the number of symbols in the solution that match the closest matching target string
#   Store this as the fitness of the individual (normalised by the target string length)
#   Maximum fitness is thus 1 (all symbols match); minimum fitness is 0 (no matches).
#   Sort the population by fitness with the best solution at the top of the list
#   This means that pop[0] is the current best scoring individual
#     * this last step is important because it helps us track the best solution and
#       will also be useful when we implement elitism...
def assess(pop, length, lines):

    for i in pop:                                                     # for each individual in the population
        i["fitness"] = get_fitness(i["solution"], lines, length)      # set its fitness score

    return sorted(pop, key = lambda i: i["fitness"], reverse=True)    # <<< *important


# Run tournament selection to pick a parent solution
#   Consider a random sample of tournament_size unique individuals from the current population
#   Return the solution belonging to the winner (the individual with the highest fitness)
def tournament(pop, tournament_size):

    competitors = random.sample(pop, tournament_size)

    winner = competitors.pop()   # by default assume the first competitor is the tournament winner
    while competitors:
        i = competitors.pop()                # consider the next competitor..
        if i["fitness"] > winner["fitness"]: # ..if they have a better fitness..
            winner = i                       # ..set them to be the tournament winner

    return winner["solution"]                # return the tournament winner's solution


# Crossover the solution strings of two parents to make an offspring solution string
#   (This code implements 'one-point crossover')
#   Pick a random point in the solution string
#   Use the mum's string up to this point and the dad's string after it
def cross(mum, dad):
    point = random.randrange(len(mum))
    return mum[:point] + dad[point:]


# Breed a new generation of solutions from the existing population
#   Generate N new offspring solutions
#   Choose parents with a bias towards those with higher fitness
#   We can do this in a few different ways: here we use tournament selection
#   We can opt to employ 'elitism' which means the current best individual
#   always gets copied into the next generation at least once
#   We can opt to use 'crossover' which combines 2 parent genotypes into 1 offspring
def breed(pop, tournament_size, crossover, elitism):

    if elitism:             # if we are using elitism, add a copy of best parent to the offspring population
        offspring_pop = [{"fitness": None, "solution": pop[0]["solution"]}]
    else:                   # otherwise..
        offspring_pop = []  # ..initialise an empty list of offspring

    while len(offspring_pop)<len(pop):  # until our list of offspring is the same length as the list of parents
        mum = tournament(pop, tournament_size)     # pick a mum
        if random.random()<crossover:                                          # if we are doing crossover..
            dad = tournament(pop, tournament_size)                             # ..pick a dad
            offspring_pop.append({"fitness":None, "solution":cross(mum, dad)}) # ..and combine their solutions
        else:                                                                  # otherwise..
            offspring_pop.append({"fitness":None, "solution":mum})             # ..just use the mum's solution

    return offspring_pop


# Apply mutation to the population of new offspring
#   Each symbol in each solution may be replaced by a randomly chosen symbol from the alphabet
#   For each symbol in each solution the chance of this happening is set by the mutation parameter
#   (Python doesn't let us change a character at location i within a string like this: string[i]=new
#   so we splice a new character into the string like this: string = beginning + new + end)
def mutate(pop, mutation, alphabet, elitism, length):

    for i in pop[elitism:]:      # if elitism is True then we skip the first individual
        i["solution"] = "".join([random.choice(alphabet) if random.random() < mutation else letter for letter in i["solution"]])

    return pop


# Write a line of summary stats for population pop at generation gen
#   We write out the max, min, and mean fitness for the population
#   and the best solution string in the current population
def write_fitness(pop, gen):

    fitnesses = [p["fitness"] for p in pop]
    mean = sum(fitnesses)/len(fitnesses)

    print("{:4d}\tmax: {:.3f}\tmin: {:.3f}\tmean: {:.3f}\t best: {}".format(gen,max(fitnesses),min(fitnesses),mean,pop[0]["solution"]))


# Check to see whether the solution string is in the list of lyrics
#   if so, return the title of the source from which the solution originates
def find_line(solution, lyrics):

    for line in lyrics:
        if line[1]==solution:
            return line[0]
    return "...line is not found in any published work :("


# The main function for the GA
#  The function takes a number of arguments specifying various parameters and options
#  Each argument has a default value which can be overridden in the function call..
#
#  The steps are:
#
#  Seed the pseudo-random number generator (using the system clock)
#    so no two runs will have the same sequence of pseudo-random numbers
#  Set the length of the solution strings to be the length of the target string
#  Set the mutation rate to be equivalent to "on average 1 mutation per offspring"
#  Initialise a population of individuals
#  Assess each member of the initial population using the fitness function and sort pop by fitness
#  Run a maximum of max_gen generations of evolution
#    (stopping early if we find the perfect solution)
#  Each generation of evolution comprises:
#    increment the generation counter
#    breed a new population of offspring
#    mutate the new offspring
#    assess each member of the new population using the fitness function and sort pop by fitness
#    track the best (highest fitness) solution in the current population (the 0th member of pop)
#    if we are writing stats and we want to write stats this generation:
#      write out some stats
#  Return the final generation count and the best individual from the final population
def do_the_ga(author="Shakespeare", pop_size=100, pressure=1, crossover=0.0,
              elitism=False, max_gen=2000, converged=False, write_every=1, length=25,
              target="Ham. Methinks it is like a weasel."):

    # check which author we are using and set filename to point to their lyrics file
    if "taylor" in author.lower() or "swift" in author.lower():
        file = "taytay-lyrics.pkl"
    elif "beatles" in author.lower():
        file = "beatles-lyrics.pkl"
    else:
        file = "shakes-lyrics.pkl"

    # try to load in their lyrics
    try:
        with open(file, 'rb') as f:
            alphabet, lyrics = pickle.load(f)
    except: # if it doesn't work print an error and finish
        print("Sorry - I couldn't find the corpus file:",file)
        print("Make sure it's in the same directory as the python code...")
        return None

    random.seed()   # seed the random number generator using the system clock

    if target:               # if we have a specific target..
        lines = [target]     # .. then that's the only line that we care about
        length = len(target) # .. and our solutions should all be the same length as the target
    else:                    # otherwise we care about all lines that are the right length
        lines = [line[1] for line in lyrics if len(line[1]) == length]

    # mutation rate is set to result in approx. one mutation per offspring
    mutation = 1.0/length

    # we will use tournaments to select parents - the size of each tournament reflects the strength of selection pressure
    tournament_size = int(pressure+1)

    pop = initialise(pop_size, length, alphabet, converged)  # initialise the population with random solutions
    pop = assess(pop, length, lines)                         # assess the members of the initial population

    generation = 0                                           # initialise the generation counter
    best = pop[0]                                            # set best to be the first (best) member of the population

    if write_every:                                          # if we are writing out progress
        write_fitness(pop, generation)                       # then we write it out

    # while we haven't done max_gen generations yet, and we haven't found a perfect solution yet...
    while generation < max_gen and best["fitness"] < 1:
        generation += 1                                         # increment the generation counter
        pop = breed(pop, tournament_size, crossover, elitism)   # breed a new population
        pop = mutate(pop, mutation, alphabet, elitism, length)  # mutate the offspring
        pop = assess(pop, length, lines)                        # assess the new population
        best = pop[0]                                           # set best to be the first (best) member of the population
        if write_every and generation % write_every==0:         # if we are writing out progress and it's time to write it out
            write_fitness(pop, generation)                      # then we write it out

    # print out the final situation
    #print("{:4d} generations yielded: '{}' (fitness = {:.3f})\n".format(generation, best["solution"], best["fitness"]))
    print("")
    print("  generations   : {:4d} ".format(generation))
    print('  best solution : {}'.format(best["solution"]))
    print('  best fitness  : {:.3f}'.format(best["fitness"]))
    print('  found in...   : {}'.format(find_line(best["solution"], lyrics)))

"""
In its basic form the GA probably won't quite manage to solve the problem completely.

By passing different arguments to the function we can try to improve its performance.

The full list of arguments that the function can take is listed below.
The Tasks on each tab within the Google Sheet walk you through exploring what they do.

The "vanilla" version of the GA executes a genetic algorithm with:
- a population of 100 strings, each of length 29
- that evolves for 2000 generations
- with a fixed target; the string: "Ham. methinks it is like a weasel."
- (which is a line from Shakespeare's play, Hamlet)

The arguments and their default values for the do_the_ga() function in lyric_ga.py:

  do_the_ga(author="Shakespeare", target="Ham. Methinks it is like a weasel.",
            length=29, pop_size=100, max_gen=2000, write_every=1, 
            pressure=1, crossover=0.0, elitism=False, converged=False)

  author: can be set to "swift", "beatles" or "shakespeare" (the default)

  target: can either be None or a specific string (like "Ham. Methinks it is like a weasel.")
          (if target is None, the GA will try to evolve *any* line by the specified author)

  length: if target=None, length sets the length of the strings being evolved (default=29)
          (very small or large lengths might not work very well; between 10 and 30 should be ok)

  pop_size: defines the number of individuals in each generation during evolution (default=100)

  max_gen: defines how many generations of evolution should take place (default is 2000)

  write_every: progress so far is written every write_every generations (default=1; write every generation)

  elitism: True or False (default is False) - specifies whether the GA uses elitism or not

  crossover: the probability (between 0.0 and 1.0) that offspring result from sexual crossover (default=0.0)

  pressure: an integer between 0 and pop_size-1 (default is 1) - controls the "strength of selection"
            (pressure=0 means no selection for fitter parents; pressure=10 means very strong selection)

  converged: True or False - specifies if the initial generation should contain identical solutions or not 


"""
