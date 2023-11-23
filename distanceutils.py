from starterkit.scoring import distanceBetweenPoint
from starterkit.data_keys import (
    LocationKeys as LK,
    ScoringKeys as SK,
    CoordinateKeys as CK,
    GeneralKeys as GK,
)


class MapDistance:
    def __init__(self, map_data):
        # initialize distance_matrix
        self.distance_matrix = {}

        location_names = list(map_data[LK.locations].keys())

        for i in range(len(location_names)):
            location_a = location_names[i]
            self.distance_matrix[location_a] = {}
            for j in range(i, len(location_names)):
                location_b = location_names[j]
                if location_a == location_b:
                    d = 0
                else:
                    location_a_data = map_data[LK.locations][location_a]
                    location_b_data = map_data[LK.locations][location_b]

                    lat_a = location_a_data[CK.latitude]
                    long_a = location_a_data[CK.longitude]
                    lat_b = location_b_data[CK.latitude]
                    long_b = location_b_data[CK.longitude]

                    d = distanceBetweenPoint(lat_a, long_a, lat_b, long_b)

                self.distance_matrix[location_a][location_b] = d
                if location_a != location_b:
                    if location_b not in self.distance_matrix:
                        self.distance_matrix[location_b] = {}
                    self.distance_matrix[location_b][location_a] = d

    # TODO remove not used.
    def distance(self, localtion_a: str, location_b: str) -> float:
        return self.distance_matrix[localtion_a][location_b]

    def locations_within_radius(self, location: str, radius: float) -> frozenset[str]:
        return frozenset(
            {
                location_b
                for location_b, distance in self.distance_matrix[location].items()
                if distance < radius
            }
        )
