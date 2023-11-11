from utils import MapDistance


def test_map_distance():
    map_data = {
        "locations": {
            "location1": {
                "latitude": 58.4369439,
                "longitude": 15.6512949,
            },
            "location2": {
                "latitude": 58.3882479,
                "longitude": 15.5652542,
            },
            "location3": {
                "latitude": 58.41507,
                "longitude": 15.609358,
            },
        }
    }

    map_distance = MapDistance(map_data)

    assert abs(map_distance.distance("location1", "location2") - 7378.0) < 1e-6
    assert abs(map_distance.distance("location1", "location3") - 3446.0) < 1e-6
    assert abs(map_distance.distance("location2", "location3") - 3937.0) < 1e-6


def test_locations_within_radius():
    map_data = {
        "locations": {
            "location1": {
                "latitude": 58.4369439,
                "longitude": 15.6512949,
            },
            "location2": {
                "latitude": 58.3882479,
                "longitude": 15.5652542,
            },
            "location3": {
                "latitude": 58.41507,
                "longitude": 15.609358,
            },
        }
    }
    map_distance = MapDistance(map_data)

    assert map_distance.locations_within_radius("location1", 8000) == {
        "location1",
        "location2",
        "location3",
    }
    assert map_distance.locations_within_radius("location1", 3000) == {"location1"}


if __name__ == "__main__":
    test_map_distance()
    test_locations_within_radius()
