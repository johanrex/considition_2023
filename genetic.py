import random


def fitness(individual):
    return 0  # Placeholder fitness function


# TODO it's possible but unlikely to create an individual with only zeroes. It can not be scored. Perhaps handle this by assigning a max negative score?
def create_individual(length, min_val, max_val):
    return [random.randint(min_val, max_val) for _ in range(length)]


def mutate(individual, min_val, max_val):
    index = random.randint(0, len(individual) - 1)
    individual[index] = random.randint(min_val, max_val)


def crossover(parent1, parent2):
    crossover_index = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_index] + parent2[crossover_index:]
    child2 = parent2[:crossover_index] + parent1[crossover_index:]
    return child1, child2


def genetic_algorithm(
    population_size,
    num_generations,
    individual_length,
    min_val,
    max_val,
    start_individual=None,
    fitness_callback=fitness,
):
    fitness = fitness_callback

    population = [
        create_individual(individual_length, min_val, max_val)
        for _ in range(population_size)
    ]

    # if we have a starting individual, replace one of the random starts with this one.
    # slightly hacky but should be fine
    if start_individual is not None:
        population[0] = start_individual

    for _ in range(num_generations):
        population.sort(key=fitness, reverse=True)

        # Selection
        parents = population[:2]

        # Crossover
        children = crossover(*parents)

        # Mutation
        for child in children:
            mutate(child, min_val, max_val)

        # Replace worst individuals with new children
        population[-2:] = children

    # Return the best individual from the final population
    return max(population, key=fitness)
