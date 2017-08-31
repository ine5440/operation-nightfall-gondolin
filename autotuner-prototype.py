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

    opt_levels = ['-O2', '-O3']
    opt_flags = [
            '-ffast-math',
            '-ffp-contract=on',
            '-fgcse-las',
            '-fgcse-sm',
            '-fipa-pta',
            '-flto',
            '-march=native',
            ]

    line = compilation_line + ['-O2'] + steps
    print(' '.join(line))
    compilation_try = subprocess.run(line)
    if (compilation_try.returncode != 0):
        print('Sad compilation')
        return

    # Run code
    iterations = int(argv[0]) if len(argv) > 0 else 100
    input_size = argv[1] if len(argv) > 1 else "8"
    t_begin = time.time() # timed run
    for i in range(iterations):
        run_trial = subprocess.run(['./'+exec_file, input_size], stdout=subprocess.DEVNULL)
    t_end = time.time()
    threshold = float(argv[2]) if len(argv) > 2 else 0.99
    print(t_end-t_begin)
    expected_time = (t_end - t_begin) * threshold

    s = 2
    while True:
        s *= 2
        print(f'Checking STEP={s}... ', end='')
        line = compilation_line + ['-O2', f'-DSTEP={s}']
        compilation_try = subprocess.run(line)
        if (compilation_try.returncode != 0):
            continue

        # Run code
        t_begin = time.time() # timed run
        for i in range(iterations):
            run_trial = subprocess.run(['./'+exec_file, input_size], stdout=subprocess.DEVNULL)
        t_end = time.time()
        print(t_end-t_begin)
        if run_trial.returncode == 0 and t_end-t_begin < expected_time:
            steps = [f'-DSTEP={s}']
            expected_time = (t_end - t_begin) * threshold
        else:
            break
    print(f'Chose {steps[0]}')

    useful_flags = []
    for flag in opt_flags:
        print(f'Checking flag {flag}... ', end='')
        line = compilation_line + ['-O2', flag] + steps
        compilation_try = subprocess.run(line)
        if (compilation_try.returncode != 0):
            continue

        # Run code
        t_begin = time.time() # timed run
        for i in range(iterations):
            run_trial = subprocess.run(['./'+exec_file, input_size], stdout=subprocess.DEVNULL)
        t_end = time.time()
        print(t_end-t_begin)
        if run_trial.returncode == 0 and t_end-t_begin < expected_time:
            useful_flags.append(flag)
    print(f'Flags that might be useful: {", ".join(useful_flags)}\n')

    times = []
    for level in opt_levels:
        for flags in closure(useful_flags):
            # Compile code
            line = compilation_line + [level] + list(flags) + steps
            print(' '.join(line))
            compilation_try = subprocess.run(line)
            if (compilation_try.returncode == 0):
                # print("Happy compilation")
                pass
            else:
                print("Sad compilation\n")
                continue

            # Run code
            t_begin = time.time() # timed run
            for i in range(iterations):
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
    for i in range(5):
        print(f'{i+1}: {times[i][0]} - {times[i][1]}')

    print(f'Suggested compilation line: {" ".join(compilation_line)} {times[0][1]} {steps[0]}')


if __name__ == "__main__":
    tuner(sys.argv[1:]) # go auto-tuner
