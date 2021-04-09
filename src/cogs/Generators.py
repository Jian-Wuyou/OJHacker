import importlib
from os import path, listdir
from typing import Callable, Any, Union

from discord.ext import commands

from utils.config import Config


class Generators(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot
        self.problems: dict[str, dict[int, Any]]

        self.bot = bot
        self.problems = {'LE': dict(), 'PA': dict(), 'MP': dict()}
        self.load_all_problems()

    def has_problem(self, problem_type, problem_id):
        if problem_type not in self.problems or problem_id not in self.problems[problem_type]:
            return False
        return True

    def load_all_problems(self):
        importlib.invalidate_caches()
        problem_path = path.join(Config.base_path, 'problems')
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

    async def generate(self, problem_type: str, problem_id: int, *, ctx: commands.Context = None):
        """
        Parameters
        ----------
        problem_type: str
            Valid problem types are 'LE', 'PA', and 'MP'

        problem_id: Union[str, int]
            Problem ID must either be an integer or a string that is
            convertible to an integer
        """
        problem_id = str(problem_id)

        error_message = None
        if problem_type not in self.problems:
            error_message = 'Invalid problem type given.'

        if not problem_id.isdigit():
            error_message = 'Invalid problem id.'

        if problem_id not in self.problems[problem_type]:
            error_message = 'Problem does not exist yet.'

        if error_message:
            error_message += f' `(type: "{problem_type}", id: "{problem_id}")`'
            if ctx:
                await ctx.send(error_message)
            else:
                print(error_message)
            return None

        problem = self.problems[problem_type][problem_id]

        generate: Callable[..., list[str]]
        solve: Callable[[Union[list[str], str]], list[Union[str, int]]]

        generate = getattr(problem, 'generate', None)
        solve = getattr(problem, 'solve', None)

        if generate is None:
            error_message = (f'The problem exists but does not have a generator. '
                             f'(type: "{problem_type}", id: "{problem_id}")')
            if ctx:
                await ctx.send(error_message)
            else:
                print(error_message)
            return None

        tc_input = generate()
        tc_answer = []
        try:
            if solve is not None:
                tc_answer = solve(tc_input)
        except StopIteration:
            error_message = (f'The problem exists but the solver could not solve the generated'
                             f'input. (type: "{problem_type}", id: "{problem_id}")')

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

        testcase = await self.generate(problem_type, problem_id)
        await ctx.send(f'```{testcase}```')

    @Config.is_allowed_admin_commands()
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

    @Config.is_allowed_admin_commands()
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
