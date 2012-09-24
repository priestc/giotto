class Http11Controller(object):
    def __init__(self, request):
        self.dd


def f1(s):
    s = s.replace(' ', '')
    return s[::-1] == s

def f2(s):
    pos1 = 0
    pos2 = len(s) - 1
    for i in enumerate(range((len(s) / 2) + 1)):
        char1 = s[pos1]
        char2 = s[pos2]
        print char1, char2
        if char1 != ' ':
            pos1 += 1
        if char2 != ' ':
            pos2 -= 1

import time
import random as pyrand

def make_data(size):
    chars = 'abcdefghijklmnopqrstuvwxyz'
    s = ''
    for _ in range(0, size):
        r = pyrand.choice(chars)
        spaces1 = ' ' * pyrand.choice([0,1,2])
        spaces2 = ' ' * pyrand.choice([0,1,2])
        s = r + spaces2 + s + spaces1 + r
        yield s

def compare_complexity(functions, data_generator, iterations, trials=1):
    for f in functions:
        times = {}
        for i, d in enumerate(data_generator(iterations)):
            tries = []
            for x in range(trials):
                start = time.time()
                result = f(d)
                end = time.time()
                tries.append(end - start)
            trial_avg = sum(tries) / trials
            times[i] = trial_avg * 1000
    
    print times
    do_plot(times)

from pylab import *
def do_plot(times):
    t = times.keys()
    s = times.values()
    plot(t, s, linewidth=1.0)

    xlabel('input data size')
    ylabel('time in miliseconds')
    title('Time complexity')
    grid(True)
    show()