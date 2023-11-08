import sqlite3


class Database:
    def __init__(self, db_file_name="db.sqlite3"):
        self.conn = sqlite3.connect(db_file_name)
        self.cur = self.conn.cursor()

        # Create table if not exists
        create_table_if_not_exists = """
        create table
        if not exists solutions
        (
            id integer primary key autoincrement,
            map_name text not null,
            total_score real not null,
            algorithm text not null,
            solution text not null,
            is_submitted boolean default false
        );
        """

        self.cur.execute(create_table_if_not_exists)
        self.conn.commit()

    def insert(self, map_name, total_score, algorithm, solution):
        # Insert data into table
        self.cur.execute(
            """
            INSERT INTO solutions
            (
                map_name,
                total_score,
                algorithm,
                solution
            )
            VALUES 
            (
                :map_name, 
                :total_score, 
                :algorithm, 
                :solution
            )
            """,
            {
                "map_name": map_name,
                "total_score": total_score,
                "algorithm": algorithm,
                "solution": solution,
            },
        )
        self.conn.commit()

    def mark_solution_as_submitted(self, map_name, solution):
        self.cur.execute(
            """
            UPDATE solutions
            SET is_submitted=true
            WHERE map_name=:map_name AND solution=:solution
            """,
            {
                "map_name": map_name,
                "solution": solution,
            },
        )
        self.conn.commit()

        return self.cur.rowcount == 1

    def get_best_unsubmitted_solution(self, map_name):
        self.cur.execute(
            "select total_score, solution FROM solutions where map_name=? and is_submitted=false order by total_score desc limit 1",
            (map_name,),
        )
        rows = self.cur.fetchall()

        if len(rows) == 0:
            return (None, None)
        else:
            total_score = rows[0][0]
            solution = rows[0][1]
            return (total_score, solution)

    def get_best_solution(self, map_name):
        self.cur.execute(
            """
            SELECT total_score, solution 
            FROM solutions 
            WHERE map_name=:map_name
            ORDER BY total_score DESC 
            LIMIT 1
            """,
            {"map_name": map_name},
        )
        rows = self.cur.fetchall()

        if len(rows) == 0:
            return (None, None)
        else:
            total_score = rows[0][0]
            solution = rows[0][1]
            return (total_score, solution)

    def keep_only_best_solution(self, map_name):
        # Keep only the best solution with the highest total_score
        sql = """
            delete from solutions 
            where 
                map_name = :map_name
                and 
                id != (
                    select id from solutions 
                    where map_name = :map_name
                    order by total_score desc
                    limit 1
                )
            ;
        """

        self.cur.execute(sql, {"map_name": map_name})
        self.conn.commit()

    def __del__(self):
        # Close connection
        self.conn.close()
