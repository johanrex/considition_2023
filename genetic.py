import random


def fitness(genome) -> float:
    return 0.0  # Placeholder fitness function


# TODO it's possible but unlikely to create a genome with only zeroes. It can not be scored. Perhaps handle this by assigning a max negative score?
def create_random_genome(length, range_min, range_max):
    return [random.randint(range_min, range_max) for _ in range(length)]


def mutate(genome, min_val, max_val):
    index = random.randint(0, len(genome) - 1)
    genome[index] = random.randint(min_val, max_val)


def crossover(parent1, parent2):
    crossover_index = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_index] + parent2[crossover_index:]
    child2 = parent2[:crossover_index] + parent1[crossover_index:]
    return child1, child2


def genetic_algorithm(
    population_size,
    num_generations,
    genome_length,
    range_min,
    range_max,
    start_genome=None,
    fitness_callback=fitness,
):
    fitness = fitness_callback

    population = [
        create_random_genome(genome_length, range_min, range_max)
        for _ in range(population_size)
    ]

    # if we have a starting genome, replace one of the random starts with this one.
    # slightly hacky but should be fine
    if start_genome is not None:
        population[0] = start_genome

    for _ in range(num_generations):
        population.sort(key=fitness, reverse=True)

        # Selection
        parents = population[:2]

        # Crossover
        children = crossover(*parents)

        # Mutation
        for child in children:
            mutate(child, range_min, range_max)

        # Replace worst genome with new children
        population[-2:] = children

    # Return the best genome from the final population
    tmp = sorted([(fitness(genome), genome) for genome in population], reverse=True)
    best_score, best_genome = tmp[0]
    return best_score, best_genome
