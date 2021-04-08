"""Database Functions

The functions that interacts with replit's builtin database named "db".
"""

from replit import db
import discord
from discord.ext import commands


class TestCasesReplit(commands.Cog, name="Database"):
    def __init__(self, bot):
        self.bot = bot
        self.db = db

    def insert_testcase(self, uid, typ, idx, name, tc_in, tc_out):
        """Inserts the test case into the database.

        Parameters
        uid : int
        The unique identification number of the test case
        typ : str
        Can either be "LE", "PA", or "MP" and tells the type of problem
        idx : int
        The problem number. It should be typecasted to str (for some reason related sa db)
        name : str
        The label / description for the inserted test case
        tc_in, tc_out : str
        Contains information on the test cases
        """
        idx = str(idx)

        if typ not in db.keys():
            print(f"ADDING {typ} TO DB")
            db[typ] = dict()
        temp_db = db[typ]

        if idx not in temp_db.keys():
            print(f"ADDING {idx} to {typ}")
            temp_db[idx] = [[name, tc_in, tc_out, uid]]
            db[uid] = (typ, idx)
            db[typ] = temp_db
            temp_db = db[typ]
            if idx not in temp_db.keys():
                print(
                    f"SHIIIIIIIIT. Database cannot insert {uid} {typ} {idx} {name}.")
            else:
                print("NICEEEEEEEEEEE. Testcase successfully inserted!")
        else:
            temp_db = db[typ]
            temp_db[idx].append([name, tc_in, tc_out, uid])
            db[uid] = (typ, idx)
            db[typ] = temp_db

    def erase_db(self):
        keys = [*db.keys()]
        for x in keys:
        del db[x]

    def get_all(self, typ, idx):
        idx = str(idx)
        if typ not in db.keys():
            print(f"NO TYP {typ} in DB")
            return []

        temp_db = db[typ]
        if idx not in temp_db.keys():
            print(f"NO IDX {idx} in {typ}")
            return []

        return temp_db[idx]

    def get_id(self):
        if "id" not in db.keys():
            db["id"] = 0
        res = db["id"]
        db["id"] += 1
        return res

    def get_entry(self, uid):
        try:
            typ, idx = db[uid]
        except Exception:
            print(f"Test case with UID {uid} has no typ or idx.")
            return
        try:
            temp_db = db[typ]
            for x in temp_db[idx]:
                if x[3] == uid:
                    io = x
                    break
            return typ, idx, io
        except Exception:
            print(f"Cannot access problem {uid} but it exists.")
            return

    def delete_entry(self, uid):
        print(*db.keys())
        try:
            typ, idx = db[uid]
            print(f"AT {typ}{idx}")
            for i, problem  in enumerate(db[typ][idx]):
                if problem[3] == uid:
                    temp_db = db[typ]
                    del temp_db[idx][i]
                    db[typ] = temp_db
                    del db[uid]
                    return True
        except Exception:
            print(f"Can't find {uid} in UID Database")
            for typ in ['LE', 'PA']:
                if typ not in db.keys():
                    continue
                temp_db = db[typ]
                for idx in range(9):
                    if str(idx) not in temp_db:
                        continue
                    print(typ, idx, temp_db[str(idx)])
                    print(type(uid))
                    for i, problem in enumerate(temp_db[str(idx)]):
                        if problem[i][3] == uid:
                            del problem[i]
                            db[typ] = temp_db
                            return True
            return False
        return False

    def delete_row(self, typ, idx):
        try:
            temp_db = db[typ]
            for x in temp_db[idx]:
                del db[x[3]]
            del temp_db[idx]
            db[db] = temp_db
        except Exception:
            raise IndexError

def setup(bot):
    bot.add_cog(ReplitDatabase(bot))
