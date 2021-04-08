"""
See problem at: https://oj.dcs.upd.edu.ph/problem/cs12202pa07
"""
from random import random, randint

def solve(inp):
    """Solves test cases for PA 09

    Parameters
    -----------
    inp: Union[list[str], str]
        if None, program will ask for manual user input via input(). Otherwise,
        input stream will be taken from inp. If inp is of type str, split by
        newline first.
    """

    def input_stream(_inp):
        if isinstance(_inp, str):
            _inp = _inp.split('\n')
        for line in _inp:
            yield line

    _input = input_stream(inp)
    prod = lambda a: a[0] * a[1]
    answers = []
    for _ in range(int(next(_input))):
        x: int = 0
        command_queue = [next(_input).strip() for j in range(int(next(_input)))]
        eval_stack = list()
        for command in command_queue:
            if command.startswith('for'):
                eval_stack.append([0, int(command[3:])])
                continue
            change = prod(eval_stack.pop()) if command.startswith('end') else 1
            if eval_stack:
                eval_stack[-1][0] += change
            else:
                x += change
        answers.append(x if x <= 1000 else 'ERROR')
    return answers

def generate(*, N: int = 5, l: int = 20, chance_for: float = 0.4,
             chance_end: float = 0.6, for_limit: int = 8):
    """Generates test cases for PA 09

    chance_add is `(1-chance_for*(1-chance_end))` if there is currently a
    for-end block in the eval_stack. Otherwise, `(1-chance_for)`

    Parameters
    -----------
    N: int
        N is the number of cases that will be generated.
    l: int
        Minimum number of commands in a test case. Once exceeded, program will
        attempt to exit for-end blocks as soon as possible.
    chance_for: float
        The chance that a new for-end block will be generated is `chance_for`
        if there are currently no for-end blocks in the eval_stack. Otherwise,
        chance is `(1-chance_end)*chance_for`
    chance_end: float
        The chance that the testcase will generate an `end` statement, thus
        exiting a for-end block, is chance_end if there is currently a for-end
        block in the eval_stack. Otherwise, it is zero.
    for_limit: int
        Maximum value of `n` in any `for n` statements. High values of `n` are
        liable to render the test cases useless because they multiply the value
        of any `add` commands inside them, thus resulting in the final answer
        being `ERROR` a lot of times.
    """

    generated_tcs = [str(N)]
    eval_stack = list()
    for _ in range(N):
        generated_tc = []
        while len(generated_tc) < l or eval_stack:
            if len(generated_tc) >= l or (eval_stack and random() <= chance_end):
                generated_tc.append('end')
                eval_stack.pop()
                continue
            if random() <= chance_for:
                generated_tc.append(f'for {randint(1, for_limit)}')
                eval_stack.append('for')
            else:
                generated_tc.append('add')
        generated_tcs.append(str(len(generated_tc)))
        generated_tcs.extend(generated_tc)
    return generated_tcs
