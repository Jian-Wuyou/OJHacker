import importlib
from os import path, listdir
from typing import Callable, Any, Union

from discord.ext import commands

from config import Config


class Generators(commands.Cog):
    config = Config()

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot
        self.problems: dict[str, dict[int, Any]]

        self.bot = bot
        self.config = Config()
        self.problems = {'LE': dict(), 'PA': dict(), 'MP': dict()}
        self.load_all_problems()

    def load_all_problems(self):
        importlib.invalidate_caches()
        problem_path = path.join(self.config.base_path, 'problems')
        for filename in listdir(problem_path):
            if not filename.endswith('.py'):
                continue
            if filename[:2] not in self.problems:
                continue
            if not filename[2:-3].isdigit():
                continue
            problem_type = filename[:2]
            problem_id = int(filename[2:-3])
            module = f'problems.{filename[:-3]}'
            try:
                self.problems[problem_type][problem_id] = importlib.import_module(module)
                print('Loaded:', module)
            except (ModuleNotFoundError, ImportError):
                print('Failed:', module)
                continue


    def generate(self, problem_type: str, problem_id: Union[str, int])\
                -> Union[None, tuple[list[str], list[str]]]:
        """
        Parameters
        ----------
        problem_type: str
            Valid problem types are 'LE', 'PA', and 'MP'

        problem_id: Union[str, int]
            Problem ID must either be an integer or a string that is
            convertible to an integer
        """
        if isinstance(problem_id, str) and not problem_id.isdigit():
            print(f'Invalid problem ID given. (type: "{problem_type}", id: "{problem_id}")')
            return
        problem_id = int(problem_id)

        problem = self.problems.get(problem_type, None)
        if problem is None:
            print(f'Invalid problem type given. (type: "{problem_type}", id: "{problem_id}")')
            return

        problem = problem.get(problem_id, None)
        if problem is None:
            print(f'Problem does not yet exist. (type: "{problem_type}", id: "{problem_id}")')
            return

        generate: Callable[..., list[str]]
        solve: Callable[[Union[list[str], str, None]], list[Union[str, int]]]

        generate = getattr(problem, 'generate', None)
        solve = getattr(problem, 'solve', None)

        if generate is None:
            print(f'There is an internal issue with the problem.'
                  f'(type: "{problem_type}", id: "{problem_id}")')
            return

        tc_input = generate()
        tc_answer = []
        if solve is not None:
            tc_answer = solve(tc_input)

        return (tc_input, tc_answer)

    @commands.command()
    async def generate_testcases(self, ctx: commands.Context, *arg: str):
        arg = ''.join(arg).strip()
        problem_type = arg[:2].upper()
        problem_id = arg[2:]
        if problem_type not in self.problems or not problem_id.isdigit():
            await ctx.send('Invalid problem type given.')
            return
        problem_id = int(problem_id)

        testcase = self.generate(problem_type, problem_id)
        await ctx.send(f'```{testcase}```')

    @config.is_allowed_admin_commands()
    @commands.command(aliases=['load_testcase'])
    async def load_problem(self, ctx: commands.Context, *arg: str):
        """Invoke to load testcases added on runtime.

        Parameters
        ----------
        arg
            Input can be in the format `<type><id>` or `<type> <id>`.
            (e.g. `PA05`, `Pa5`, `pa 05`)
        """
        arg = ''.join(arg).strip()
        problem_type = arg[:2].upper()
        problem_id = arg[2:]
        problems = self.problems.get(problem_type, None)
        if problems is None or not problem_id.isdigit():
            await ctx.send('Invalid problem type given.')
            return
        problem_id = int(problem_id)
        problem_name = f'{problem_type}{problem_id:02}'

        # Avoid loading a testcase module more than once
        if problems.get(problem_id, None) is not None:
            await ctx.send(f'Testcases for {problem_name} have already been loaded. '
                           f'Please use {ctx.prefix}reload_testcase instead.')
            return

        importlib.invalidate_caches()
        module = f'problems.{problem_name}'
        print('Loading:', module)
        try:
            problems[problem_id] = importlib.import_module(module)
        except (ModuleNotFoundError, ImportError) as e:
            print(e)
            await ctx.send(f'Was not able to load testcases for {problem_name}.')
            return
        await ctx.send(f'Testcases for {problem_name} successfully loaded.')

    @config.is_allowed_admin_commands()
    @commands.command(aliases=['reload_testcase'])
    async def reload_problem(self, ctx: commands.Context, *arg: str):
        """Invoke to reload testcases modified on runtime.

        Parameters
        ----------
        arg
            Input can be in the format `<type><id>` or `<type> <id>`.
            (e.g. `PA05`, `Pa5`, `pa 05`)
        """
        arg = ''.join(arg).strip()
        problem_type = arg[:2].upper()
        problem_id = arg[2:]
        problems = self.problems.get(problem_type, None)
        if problems is None or not problem_id.isdigit():
            await ctx.send('Invalid problem type given.')
            return
        problem_id = int(problem_id)
        problem_name = f'{problem_type}{problem_id:02}'

        # Avoid loading a testcase module more than once
        if problems.get(problem_id, None) is None:
            await ctx.send(f'Testcases for {problem_name} have not yet been loaded. '
                           f'Please use {ctx.prefix}load_testcase instead.')
            return

        message = ''
        try:
            importlib.reload(problems[problem_id])
            message = f'Testcases for {problem_name} successfully reloaded.'
        except TypeError:
            message = 'For some reason, the module was not a module object.'
        except ModuleNotFoundError:
            message = 'The module object exists but the script from which it was loaded no '\
                      'longer does.'
        except ImportError:
            message = 'For some reason, the module object exists but it is not in sys.modules.'

        print(message)
        await ctx.send(message)


def setup(bot: commands.Bot):
    bot.add_cog(Generators(bot))
