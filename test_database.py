import pytest
from database import Database


@pytest.fixture
def setup_database():
    db = Database(":memory:")
    yield db


def test_insert(setup_database):
    setup_database.insert("map1", 100.0, "algorithm1", "solution1")


def test_get_best_solution(setup_database):
    setup_database.insert("map1", 100.0, "algorithm1", "solution1")
    setup_database.insert("map1", 200.0, "algorithm1", "solution2")
    total_score, solution = setup_database.get_best_solution("map1")
    assert abs(total_score - 200.0) < 1e-9
    assert solution == "solution2"


def test_get_best_unsubmitted_solution(setup_database):
    # Insert some data
    setup_database.insert("map1", 100.0, "algorithm1", "solution1")
    setup_database.insert("map1", 200.0, "algorithm1", "solution2")
    setup_database.insert("map1", 300.0, "algorithm1", "solution3")

    # Test the method
    total_score, unsubmitted_solution = setup_database.get_best_unsubmitted_solution(
        "map1"
    )

    assert unsubmitted_solution == "solution3"
    assert abs(total_score - 300.0) < 1e-9


def test_mark_solution_as_submitted(setup_database):
    # Insert some data
    setup_database.insert("map1", 100.0, "algorithm1", "solution1")
    setup_database.insert("map1", 200.0, "algorithm1", "solution2")

    # Mark a solution as submitted
    result = setup_database.mark_solution_as_submitted("map1", "solution1")

    # Check that the method returned True
    assert result is True

    # Check that the solution is now marked as submitted in the database
    setup_database.cur.execute(
        """
        SELECT is_submitted
        FROM solutions
        WHERE map_name=:map_name AND solution=:solution
        """,
        {
            "map_name": "map1",
            "solution": "solution1",
        },
    )
    is_submitted = bool(setup_database.cur.fetchone()[0])
    assert is_submitted is True


def __count_solutions(setup_database, map_name):
    setup_database.cur.execute(
        "SELECT count(*) FROM solutions WHERE map_name=:map_name",
        {
            "map_name": map_name,
        },
    )
    count = setup_database.cur.fetchone()[0]
    return count


def test_keep_only_best_solution(setup_database):
    setup_database.insert("map1", 100.0, "algorithm1", "solution1")
    setup_database.insert("map1", 200.0, "algorithm1", "solution2")
    setup_database.insert("map1", 300.0, "algorithm1", "solution3")

    assert 3 == __count_solutions(setup_database, "map1")
    setup_database.keep_only_best_solution("map1")
    assert 1 == __count_solutions(setup_database, "map1")

    total_score, _ = setup_database.get_best_solution("map1")

    assert abs(total_score - 300.0) < 1e-9


if __name__ == "__main__":
    db = Database(":memory:")
    # db.insert("map1", 100.0, "algorithm1", "solution1")
    # result = db.get_best_unsubmitted_solution("map1")
    # result = db.get_best_algorithm_raw_data("map1", "algorithm1")

    test_keep_only_best_solution(db)

    pass
