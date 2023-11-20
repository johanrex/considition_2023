import utils


def test_merge_clusters_with_common_locations():
    clusters = [frozenset(["A", "B"]), frozenset(["B", "C"]), frozenset(["D", "E"])]
    expected_result = [frozenset(["A", "B", "C"]), frozenset(["D", "E"])]
    result = utils.merge_clusters_with_common_locations(clusters)
    assert result == expected_result
