import subprocess
import pipes
import multiprocessing
import os

from execute_case import execute_case,execute_case_interactive

def main(CASE=100,interactive=False):
    scores = []
    count = 0
    if interactive:execute = execute_case_interactive
    else:execute = execute_case
    if not os.path.isdir("in"):os.mkdir("in") 
    if not os.path.isdir("out"):os.mkdir("out")
    if not os.path.isdir("pipeline"):os.mkdir("pipeline")
    if len([d for d in os.listdir("in") if len(d)==8]) < CASE:
        with open("seeds.txt", mode='w') as f:
            for i in range(CASE):f.write(str(i)+"\n")
        subprocess.run('cargo run --release --bin gen seeds.txt',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    with multiprocessing.Pool(max(1, multiprocessing.cpu_count()-2)) as pool:
        for seed, score in pool.imap_unordered(execute, range(CASE)):
            print(count%10, end='', flush=True)
            try:
                scores.append((int(score.split()[-1]), f'{seed:04}'))
            except ValueError:
                print(seed, "ValueError", flush=True)
                print(score, flush=True)
                return
            except IndexError:
                print(seed, "IndexError", flush=True)
                print(f"error: {score}", flush=True)
                return 
            count += 1
    print()
    scores.sort()
    total = sum([s[0] for s in scores])
    ave = total / CASE
    print(f'total: {total}')
    print(f'max: {scores[-1]}')
    print(f'ave: {ave}')
    print(f'min: {scores[0]}')

if __name__ == '__main__':
    main()