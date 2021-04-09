"""Database Functions

The functions that interacts with replit's builtin database named "db".
"""


from replit import db
from discord.ext import commands


class ReplitDatabase(commands.Cog, name="Database"):
    """Database cog for use with repl.it

    Required methods:
        insert_testcase(
            uid: int,
            problem_type: str,
            problem_id: int,
            description: str,
            testcase_input: str,
            testcase_output: str
        )

        erase_db()

        get_problem(
            problem_type: str,
            problem_id: int
        )

        delete_problem(
            problem_type: str,
            problem_id: int
        )

        get_entry(uid: int)
        delete_entry(uid: int)

        get_id()
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = db
        self.problem_types = {'LE', 'PA', 'MP'}

    def insert_testcase(
        self,
        uid: int,
        problem_type: str,
        problem_id: int,
        description: str,
        testcase_input: str,
        testcase_output: str
    ):
        """Inserts the test case into the database.

        Parameters
        uid : int
        The unique identification number of the test case
        problem_type : str
        Can either be "LE", "PA", or "MP" and tells the type of problem
        problem_id : int
        The problem number. It should be typecasted to str (for some reason related sa db)
        description : str
        The label / description for the inserted test case
        testcase_input, testcase_output : str
        Contains information on the test cases
        """
        problem_id = str(problem_id)
        if problem_type not in self.problem_types:
            print(f"Invalid problem type '{problem_type}'.")
            return

        if problem_type not in db:
            print(f"Adding problem type '{problem_type}' to db.")

        problems = db.setdefault(problem_type, dict())

        if problem_id not in problems:
            print(f"Adding problem id '{problem_type}{problem_id}' to db.")

        problem = problems.setdefault(problem_id, list())
        problem.append([description, testcase_input, testcase_output, uid])
        db[uid] = (problem_type, problem_id)
        print(
            f"Successfully added testcase {problem_type}{problem_id} (uid: {uid}) '{description}'")

    def erase_db(self):
        for i in db:
            del db[i]

    def get_problem(self, problem_type: str, problem_id: int):
        problem_id = str(problem_id)

        if problem_type not in db or problem_id not in db[problem_type]:
            print(f"Problem '{problem_type}{problem_id}' is not in db.")
            return None

        return db[problem_type][problem_id]

    def delete_problem(self, problem_type, problem_id):
        if problem_type not in db or problem_id not in db[problem_type]:
            return

        for testcase in db[problem_type][problem_id]:
            # delete UID from database
            del db[testcase[3]]
        del db[problem_type][problem_id]

    def get_entry(self, uid):
        if uid not in db:
            print(f"UID#{uid} is not in the database.")
            return None

        problem_type, problem_id = db[uid]
        if problem_type not in db or problem_id not in db[problem_type]:
            print(f"UID#{uid} references a non-existent testcase, deleting...")
            del db[uid]
            return None

        for testcase in db[problem_type][problem_id]:
            if testcase[3] == uid:
                return [problem_type, problem_id, testcase]

        print(f"UID#{uid} references a non-existent testcase, deleting...")
        del db[uid]
        return None

    def delete_entry(self, uid):
        if uid not in db:
            print(f"UID#{uid} is not in the database.")
            return False

        problem_type, problem_id = db[uid]
        if problem_type not in db or problem_id not in db[problem_type]:
            print(f"UID#{uid} references a non-existent testcase, deleting...")
            del db[uid]
            return False

        for i, testcase in enumerate(db[problem_type][problem_id]):
            if testcase[3] == uid:
                del db[problem_type][problem_id][i]
                return True
        return False

    def get_id(self):
        res = db.setdefault('id', 0)
        db['id'] += 1
        return res


def setup(bot):
    bot.add_cog(ReplitDatabase(bot))
