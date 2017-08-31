#!/usr/bin/python3
# Auto-tuner prototype
# Built for INE5540 robot overlords

import subprocess # to run stuff
import sys # for args, in case you want them
import time # for time


def closure(xs):
    from itertools import combinations
    for i in range(len(xs) + 1):
        for p in combinations(xs, i):
            yield p


def tuner(argv):
    exec_file = 'matmult'
    compilation_line = ['gcc','-o',exec_file,'mm.c']
    steps = ['-DSTEP=2']

    opt_levels = ['-O2', '-O3', '-Ofast']
    opt_flags = [
            '-march=native', '-ffp-contract=on', '-fgcse-sm', '-fgcse-las',
            '-fipa-pta', '-flto'
            ]

    times = []
    for level in opt_levels:
        for flags in closure(opt_flags):
            # Compile code
            line = compilation_line + [level] + list(flags) + steps
            print(' '.join(line))
            compilation_try = subprocess.run(line)
            if (compilation_try.returncode == 0):
                # print("Happy compilation")
                pass
            else:
                print("Sad compilation")

            # Run code
            input_size = str(8)
            t_begin = time.time() # timed run
            for i in range(25):
                run_trial = subprocess.run(['./'+exec_file, input_size], stdout=subprocess.DEVNULL)
            t_end = time.time()
            if (run_trial.returncode == 0):
                times.append((t_end-t_begin, ' '.join([level, *flags])))
                print("Happy execution in "+str(t_end-t_begin))
                pass
            else:
                print("Sad execution")

            print()

    times.sort(key=lambda e: e[0])
    for i in range(3):
        print(f'{i}: {times[i][0]} - {times[i][1]}')


if __name__ == "__main__":
    tuner(sys.argv[1:]) # go auto-tuner
