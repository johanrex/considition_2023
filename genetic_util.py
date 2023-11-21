from starterkit.data_keys import (
    MapNames as MN,
    LocationKeys as LK,
    GeneralKeys as GK,
)
import utils
import math
import genetic


class GeneticUtil:
    def __init__(
        self, map_name, location_names, map_data, general_data, starting_solution
    ) -> None:
        self.map_name = map_name
        self.map_data = map_data
        self.general_data = general_data
        self.location_names = location_names
        self.starting_solution = starting_solution

    def solution_from_int_list(self, individual: list[int]):
        individual_idx = 0
        solution = utils.copy_solution(self.starting_solution)

        # TODO probably can be optimized somehow
        for location_name in self.location_names:
            if individual[individual_idx] == 0 and individual[individual_idx + 1] == 0:
                individual_idx += 2
            else:
                solution[LK.locations][location_name] = {
                    LK.f9100Count: individual[individual_idx],
                    LK.f3100Count: individual[individual_idx + 1],
                }
                individual_idx += 2

        return solution

    def __fitness_callback(self, genome: list[int]):
        solution = self.solution_from_int_list(genome)
        current_score = utils.score_wrapper(
            self.map_name, solution, self.map_data, self.general_data
        )

        return current_score

    def run_evolution(
        self,
        nr_of_evolutions,
        nr_of_generations,
        population_size,
        starting_score,
        starting_solution,
        range_min,
        range_max,
    ):
        best_score = starting_score
        best_solution = starting_solution

        genome_length = len(self.location_names * 2)

        for i in range(nr_of_evolutions):
            print(f"Running evolution {i+1}/{nr_of_evolutions}")

            (
                best_score_single_evolution,
                best_genome_single_evolution,
            ) = genetic.genetic_algorithm(
                population_size=population_size,
                num_generations=nr_of_generations,
                genome_length=genome_length,
                range_min=range_min,
                range_max=range_max,
                start_genome=None,
                fitness_callback=self.__fitness_callback,
            )

            if best_score_single_evolution > best_score:
                print(
                    f"Genetic alg found new best score: {best_score_single_evolution}."
                )

                best_score = best_score_single_evolution
                best_solution = self.solution_from_int_list(
                    best_genome_single_evolution
                )
        return best_score, best_solution
