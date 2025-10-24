import random       # from random, we use "seed", "choice", "choices", "sample", "randrange", "random"
import statistics   # from statistics, we just use "mean", "stdev"
import pickle       # we use the pickle library to read in ("unpickle") the lyrics data

# global parameters that fix the minimum and maximum number of words in a solution
max_length = 30
min_length = 3


# Initialise the GA population
#   Fill an empty population array with N = pop_size random individuals
#   Each individual is represented by a Python dictionary with two elements: "solution" and "fitness"
#     each "fitness" is initialised to <None> as the associated solution has not yet been assessed
#     each "solution" is initialised to a list of random integers between 0 and W (not including W itself)
#     (each of these integers corresponds to a word from the corpus)
#     if converged is True, each "solution" is the same random list of integers
#     if converged is False, each "solution" is an independent random list of integers
def initialise(pop_size, genome_length, W, converged=False):

    pop = []

    if converged:
        solution = [random.randrange(W) for _ in range(genome_length)]

    while len(pop)<pop_size:
        if not converged:
            solution = [random.randrange(W) for _ in range(genome_length)]
        pop.append({"fitness":None, "solution":solution.copy()})

    return pop


# if a set of mutation operator rates are supplied, use them
def set_mutation_operator_rates(mutation_operator_rates):

    # default rates of different types of mutation
    default_mutation_operator_rates = {
        "insert_rate":   0,
        "delete_rate":   0,
        "point_rate" : 100,
        "extend_rate":   0
    }

    for operator, rate in mutation_operator_rates.items():
        if operator in default_mutation_operator_rates:
            default_mutation_operator_rates[operator] = rate

    operators = []
    rates = []
    for operator, rate in default_mutation_operator_rates.items():
        operators.append(operator.split("_")[0])
        rates.append(rate)

    return operators, rates


# if a set of crossover operator rates are supplied, use them
def set_crossover_operator_rates(crossover_operator_rates):

    # default rates of different types of crossover
    default_crossover_operator_rates = {
        "one-pt":  0,
        "two-pt":  0,
        "four-pt": 0
    }

    for operator, rate in crossover_operator_rates.items():
        if operator in default_crossover_operator_rates:
            default_crossover_operator_rates[operator] = rate

    operators = []
    rates = []
    for operator, rate in default_crossover_operator_rates.items():
        operators.append(operator)
        rates.append(rate)

    return operators, rates


# if a set of fitness recipe weights are supplied, use them
def set_fitness_recipe(fitness_recipe):

    # fitness weights for the...
    recipe = {
        "LP": 20,    # ..no. Legal Pairs in solution
        "IP": -25,   # ..no. Illegal Pairs in solution
        "CP": 50,    # ..no. Consecutive legal Pairs in solution

        "LT": 100,   # ..no. Legal Triples in solution
        "IT": 0,     # ..no. Illegal Triples in solution
        "CT": 200,   # ..no. Consecutive legal Triples in solution

        "MF": -10,   # ..Mean of word Frequencies in solution
        "SF": 10,    # ..St.dev. of word Frequencies in solution
        "RF": 10     # ..Range of word Frequencies in solution
    }
    # if a weight is zero for an aspect, fitness is not influenced that aspect
    # a large positive weight for an aspect (e.g., +100), means that it has a positive influence on fitness
    # a larger negative weight for an aspect (e.g., -100), means that it has a negative influence on fitness

    for aspect, weight in fitness_recipe.items():
        if aspect in recipe:
            recipe[aspect] = weight

    return recipe


# get a fitness score for a solution encoded in a genotype by summing a set
# of measures weighted by the fitness recipe weights
def get_fitness(genotype, word_dict, word_indices, word_pairs, word_triples, fitness_recipe, verbose=False):

    pairs = []
    triples = []
    word_frequencies = []

    pre_previous = None
    previous = 0                         # the "start" symbol precedes the first word

    solution = genotype
    if solution[-1]==0:
        solution=solution[:-1]

    for word in solution+[0]:              # for each word in the solution genotype
        if word:
            word_frequencies.append(word_dict[word]["freq"])

        pair = (previous, word)              # make a pair of the previous word and the current word
        if pair in word_pairs:               # if the pair is in the pair dictionary
            pairs.append(True)
        else:
            pairs.append(False)

        if previous:
            triple = (pre_previous, previous, word) # make a pair of the previous word and the current word
            if triple in word_triples:               # if the pair is in the pair dictionary
                triples.append(True)
            else:
                triples.append(False)

        pre_previous = previous              # current word becomes the previous word
        previous = word                      # current word becomes the previous word

    consecutive_pairs = sum([ True for p, pair in enumerate(pairs[:-1]) if pair and pairs[p+1] ])
    legal_pairs = pairs.count(True)
    illegal_pairs = len(pairs)-legal_pairs

    consecutive_triples = sum([ True for t, triple in enumerate(triples[:-1]) if triple and triples[t+1] ])
    legal_triples = triples.count(True)
    illegal_triples = len(triples)-legal_triples

    mean_word_frequency  = 0.001 * sum(word_frequencies)/len(word_frequencies)
    try:
        sdev_word_frequency  = 0.001 * statistics.stdev(word_frequencies)
    except:
        sdev_word_frequency = 0
    range_word_frequency = 0.001 * (max(word_frequencies)-min(word_frequencies))

    fitness = (fitness_recipe["LP"] * legal_pairs)         + \
              (fitness_recipe["IP"] * illegal_pairs)       + \
              (fitness_recipe["CP"] * consecutive_pairs)   + \
              (fitness_recipe["LT"] * legal_triples)       + \
              (fitness_recipe["IT"] * illegal_triples)     + \
              (fitness_recipe["CT"] * consecutive_triples) + \
              (fitness_recipe["MF"] * mean_word_frequency) + \
              (fitness_recipe["SF"] * sdev_word_frequency) + \
              (fitness_recipe["RF"] * range_word_frequency)

    if verbose:
        return "".join(["  ", str(fitness), " :\n",
                "    LP = ", str(legal_pairs),               "\t* ", str(fitness_recipe["LP"]), "\n",
                "  + IP = ", str(illegal_pairs),             "\t* ", str(fitness_recipe["IP"]), "\n",
                "  + CP = ", str(consecutive_pairs),         "\t* ", str(fitness_recipe["CP"]), "\n",
                "  + LT = ", str(legal_triples),             "\t* ", str(fitness_recipe["LT"]), "\n",
                "  + IT = ", str(illegal_triples),           "\t* ", str(fitness_recipe["IT"]), "\n",
                "  + CT = ", str(consecutive_triples),       "\t* ", str(fitness_recipe["CT"]), "\n",
                "  + MF = ", str(int(mean_word_frequency)),  "\t* ", str(fitness_recipe["MF"]), "\n",
                "  + SF = ", str(int(sdev_word_frequency)),  "\t* ", str(fitness_recipe["SF"]), "\n",
                "  + RF = ", str(int(range_word_frequency)), "\t* ", str(fitness_recipe["RF"]), "\n"])

    return fitness  #/(len(solution)-solution.count(0))



# Assess the fitness of each individual in the current population
#   For each individual, consider how often each word and pair of words occurs in the corpus,
#   Store this as the fitness of the individual (normalised by the target string length)
#   Maximum fitness is thus 1; minimum fitness is 0.
#   Sort the population by fitness with the best solution at the top of the list
#     * this last step is important because it helps us track the best solution and
#       will also be useful when we implement elitism...
def assess(pop, word_dict, word_indices, word_pairs, word_triples, fitness_recipe):

    for i in pop:
        i["fitness"] = get_fitness(i["solution"], word_dict, word_indices, word_pairs, word_triples, fitness_recipe)

    return sorted(pop, key = lambda i: i["fitness"], reverse=True)    # <<< *important


# Run tournament selection to pick a parent solution
#   Consider a sample of tournament_size unique individuals from the current population
#   Return the solution belonging to the winner (the individual with the highest fitness)
def tournament(pop, tournament_size):

    competitors = random.sample(pop, tournament_size)

    winner = competitors.pop()
    while competitors:
        i = competitors.pop()
        if i["fitness"] > winner["fitness"]:
            winner = i

    return winner["solution"].copy()


# Breed a new generation of solutions from the existing population
#   Generate N offspring solutions from a population of N individuals
#   Choose parents with a bias towards those with higher fitness
#   We can do this in a few different ways: here we use tournament selection
#   We can opt to employ 'elitism' which means the current best individual
#   always gets copied into the next generation at least once
#   We can set the chance of using 'crossover' which combines
#   two parent genotypes into one offspring
def breed(pop, tournament_size, crossover, elitism, crossover_operators, operator_rates):

    offspring_pop = []

    if elitism:
        elite_solution = pop[0]["solution"]
        offspring_pop.append({"fitness": None, "solution": elite_solution.copy()})

    while len(offspring_pop)<len(pop):
        mum = tournament(pop, tournament_size)
        if random.random()<crossover:
            dad = tournament(pop, tournament_size)
            offspring_pop.append({"fitness":None, "solution":cross(mum, dad, crossover_operators, operator_rates)})
        else:
            offspring_pop.append({"fitness":None, "solution":mum})

    return offspring_pop


# Apply mutation to the population of new offspring
#   Each symbol in each solution may be replaced by a randomly chosen symbol from the alphabet
#   For each symbol in each solution the chance of this happening is set by the mutation parameter
def mutate(pop, W, elitism, operators, rates):

    for child in pop[elitism:]:
        length = len(child["solution"])
        m = min(1,sum(random.random() < 1.0/length for _ in range(length)))       # how many mutations will be applied?

        for _ in range(m):   # for each mutation...
            mutation_type = random.choices(operators, rates)[0]                   # pick a type based on the rates supplied
            if mutation_type == "point":
                w = random.randrange(len(child["solution"]))                      # choose a random point in the genotype
                child["solution"][w] = random.randrange(W)                        # replace the word there with a random word
            elif mutation_type == "insert" and len(child["solution"])<max_length: # if the solution is short enough...
                w = random.randint(0,len(child["solution"]))                      # choose a random point in the genotype
                child["solution"] = child["solution"][:w]+[random.randrange(W)]+child["solution"][w:] # insert a random word there
            elif mutation_type == "extend" and len(child["solution"])<max_length-2*length: # if the solution is short enough..
                child["solution"] += [0]+[random.randrange(W) for _ in range(length)] #[0, random.randrange(W)] # extend it with some random words
            elif mutation_type == "delete" and len(child["solution"])>min_length: # if the solution is long enough..
                w = random.randrange(len(child["solution"]))                      # choose a random point in the genotype
                child["solution"] = child["solution"][:w]+child["solution"][w+1:] # and remove it
    return pop


# Crossover the solution string of two parents to make an offspring
#   (This code implements 'one-point crossover')
#   Pick a random point in the solution string,
#   Use the mum's string up to this point and the dad's string after it
def one_pt_cross(mum, dad):
    point = random.randint(0,min([len(mum),len(dad)]))
    return mum[:point] + dad[point:]

def two_pt_cross(mum, dad):
    point1 = random.randint(0,len(mum))
    point2 = random.randint(0,len(dad))
    return mum[:min(point1,point2)] + dad[min(point1,point2):max(point1, point2)] + mum[max(point1,point2):]

def four_pt_cross(mum, dad):
    point1 = random.randint(0,len(mum))
    point2 = random.randint(0,len(dad))
    point3 = random.randint(0,len(dad))
    point4 = random.randint(0,len(mum))
    return mum[:min(point1,point4)] + dad[min(point2,point3):max(point2,point3)] + mum[max(point1,point4):]


def cross(mum, dad, operators, rates):

    if len(mum)!=len(dad):
        return mum

    crossover_type = random.choices(operators, rates)[0]

    if crossover_type == "one-pt":
        new =  one_pt_cross(mum, dad)
    elif crossover_type == "two-pt":
        new =  two_pt_cross(mum, dad)
    elif crossover_type == "four-pt":
        new = four_pt_cross(mum, dad)

    if min_length <= len(new) <= max_length:
        return new
    else:
        return mum

# make a string of words based on a genotype solution
def make_solution(solution, word_dict):
    solution = " ".join([word_dict[word]["word"] for word in solution])
    #while "/ /" in solution:
    #    solution = solution.replace("/ /","/")
    return solution
    return solution.strip(" /")

# Write a line of summary stats for population pop at generation gen
#   if File is None we write to the standard out, otherwise we write to the File
def write_fitness(pop, gen, word_dict):

    fitness = [p["fitness"] for p in pop]

    line = "{:4d}: max:{:.3f}, min:{:.3f}, mean:{:.3f} best: {}".format(gen, max(fitness), min(fitness), statistics.mean(fitness), make_solution(pop[0]["solution"], word_dict))

    print(line)

# search for a lyric in the corpus of lyrics
def find_line(lyric, lyrics):

    for line in lyrics:
        if line[1]==lyric["solution"]:
            return line[0]
    return None # "Not Found :("


# The main function for the GA
#  The function takes a number of arguments specifying various parameters and options
#  each argument has a default value which can be overloaded in the function call..
#   Seed the pseudo-random number generator (using the system clock)
#     so no two runs will have the same sequence of pseudo-random numbers
#   Set the length of the solution strings to be the length of the target string
#   Initialise a population of individuals
#   Assess each member of the initial population using the fitness function
#   Run a maximum of max_gen generations of evolution
#   Each generation of evolution comprises:
#     increment the generation counter
#     breed a new population of offspring
#     mutate the new offspring
#     assess each member of the new population using the fitness function and sort pop by fitness
#     track the best (highest fitness) solution in the current population (the 0th item in the list)
#     if we are writing stats, and we want to write stats this generation:
#       write out some stats
#   Return the final generation count and the best individual from the final population
def do_the_ga(author="taylor", pop_size=100, pressure=3, crossover=0.0, length=15, elitism=False,
              max_gen=500, converged=False, write_every=1, fitness_recipe={}, mutation_operator_rates={}, crossover_operator_rates={}):

    # check which author we are using and set filename to point to their lyrics file
    if "taylor" in author.lower() or "swift" in author.lower():
        file = "taytay"
    else:
        file = "beatles"

    # try to load in their lyrics
    try:
        with open(file+"-lyrics.pkl", 'rb') as f:
            _, lyrics = pickle.load(f)
    except:
        print("Sorry - I couldn't find the corpus file:", file+"-lyrics.pkl")
        print("Make sure it's in the same directory as the python code...")
        return (None)

    # try to load in their word frequencies, word pair frequencies and word triplet frequencies
    try:
        with open(file+"-words.pkl", 'rb') as f:
            word_dict, word_indices, word_pairs, word_triples = pickle.load(f)
    except:
        print("Sorry - I couldn't find the corpus file:", file+"-words.pkl")
        print("Make sure it's in the same directory as the python code...")
        return (None)

    W = len(word_dict)         # the number of unique words that we can build solutions from

    # set the genetic operator frequencies and the weight of the different aspects of fitness
    mutation_operators, mutation_rates = set_mutation_operator_rates(mutation_operator_rates)
    crossover_operators, crossover_rates = set_crossover_operator_rates(crossover_operator_rates)
    fitness_recipe = set_fitness_recipe(fitness_recipe)

    random.seed()   # seed the random number generator using the system clock

    # we will use tournaments to select parents - the size of each tournament reflects the strength of selection pressure
    tournament_size = int(pressure+1)

    pop = initialise(pop_size, length, W, converged)                                     # initialise the population with random solutions
    pop = assess(pop, word_dict, word_indices, word_pairs, word_triples, fitness_recipe) # assess the members of the initial population

    generation = 0                                           # initialise the generation counter
    best = pop[0]                                            # set best to be the first (best) member of the population

    if write_every:                                          # if we are writing out progress
        write_fitness(pop, generation, word_dict)            # then we write it out

    #print(get_fitness(best["solution"], word_dict, word_indices, word_pairs, word_triples, verbose=True))

    # while we haven't done max_gen generations of evolution..
    while generation < max_gen:
        generation += 1                                                                              # increment the generation counter
        pop = breed(pop, tournament_size, crossover, elitism, crossover_operators, crossover_rates)  # breed a new population
        pop = mutate(pop, W, elitism, mutation_operators, mutation_rates)                            # mutate the offspring
        pop = assess(pop, word_dict, word_indices, word_pairs, word_triples, fitness_recipe)         # assess the new population

        best = pop[0]                                                        # set best to be the first (best) member of the population
        if write_every and generation % write_every==0:                      # if we are writing out progress and it's time to write it out
            write_fitness(pop, generation, word_dict)                        # then we write it out

    # print out the final situation
    print("")
    print("{:4d} generations yielded:\n    '{}' ({:.3f})".format(generation, make_solution(best["solution"], word_dict), best["fitness"]))
    source = find_line(best, lyrics)
    if source:
        print("\n    from", find_line(best, lyrics))

    #print("")
    #print(get_fitness(best["solution"], word_dict, word_indices, word_pairs, word_triples, verbose=True))
    #print(best["solution"])

