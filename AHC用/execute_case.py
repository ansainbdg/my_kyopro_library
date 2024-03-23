import subprocess
import pipes
import multiprocessing
import os
from tqdm import tqdm

def check_stderr(stderr,seed=0):
    # subprocessのstderrからスコアを判定し、デバッグ標準出力をprintする
    if isinstance(stderr,list):
        for s in stderr:
            if not s:
                pass
            elif s.split()[-1].lstrip('-+').isdigit():
                return int(s.split()[-1])
            elif  'Finished' not in s and '.exe' not in s:
                print(s, flush=True)
        else:
            print(f'error seed2: {seed:04}', flush=True)
            print(stderr, flush=True)
    else:
        if stderr.split()[-1].lstrip('-+').isdigit():
            return int(stderr.split()[-1])
        else:
            print(f'error seed: {seed:04}', flush=True)
            print(stderr, flush=True)

def execute_case(args,file="code1.py",TL=None):
    if isinstance(args,list) or isinstance(args,tuple):
        if len(args)==1:
            seed,file,TL= args[0],"code1.py",None
        elif len(args)==2:
            seed,file= args
            TL=None
        elif len(args)==3:
            seed,file,TL= args
        else:
            raise ValueError('not enough values to unpack')
    else:
        seed = args
    input_file_path = f'in/{seed:04}.txt'
    output_file_path = f'out/{seed:04}.txt'
    with open(input_file_path) as fin:
        with open(output_file_path, 'w') as fout:
            proc = subprocess.run(['python',file], stdin=fin, stdout=fout, stderr=subprocess.PIPE,timeout=TL)
            try:
                if proc.stderr.decode('utf8').split('\n')!=['']:
                    print(proc.stderr.decode('utf8').split('\n'))
                if "Err" in proc.stderr.decode('utf8'):
                    return seed,None
            except UnicodeDecodeError:
                print(proc.stderr)
                return seed,None
            pipefile = f'pipeline/pipefile_{seed:04}'
            with pipes.Template().open(pipefile, 'w') as p:
                subprocess.run(['cargo', "run", "--release","--bin", "vis", input_file_path, output_file_path], stdout=p, timeout=TL)
            output = open(pipefile).read()
            assert output
            score = check_stderr(output)
    return seed, score

def execute_case_interactive(args,file="code1.py",TL=None):
    if isinstance(args,list) or isinstance(args,tuple):
        if len(args)==1:
            seed,file,TL= args[0],"code1.py",None
        elif len(args)==2:
            seed,file= args
            TL=None
        elif len(args)==3:
            seed,file,TL= args
        else:
            raise ValueError('not enough values to unpack')
    else:
        seed = args
    input_file_path = f'in/{seed:04}.txt'
    output_file_path = f'out/{seed:04}.txt'
    proc = subprocess.run(f'cargo run --release --bin tester python {file} < {input_file_path} > {output_file_path}',stderr=subprocess.PIPE,shell=True,timeout=TL)
    """
    if proc.stderr.decode('utf8').split('\n')!=['']:
        print(proc.stderr.decode('utf8').split('\n'))
    if "Err" in proc.stderr.decode('utf8'):
        raise
    pipefile = f'pipeline/pipefile_{seed:04}'
    with pipes.Template().open(pipefile, 'w') as p:
        subprocess.run(['cargo', "run", "--release","--bin", "vis", input_file_path, output_file_path], stderr=p, timeout=TL)
    output = open(pipefile).read()
    assert output
    return seed, output
    """
    try:
        score = check_stderr(proc.stderr.decode('utf8').split('\n'))
        return seed,score
    except UnicodeDecodeError:
        print(proc.stderr)
        return seed,None

def main(CASE=100,file ='code1.py',interactive=False,multi=False,print_score=True):
    scores = []
    if interactive:execute = execute_case_interactive
    else:execute = execute_case
    if not os.path.isdir("in"):os.mkdir("in") 
    if not os.path.isdir("out"):os.mkdir("out")
    if not os.path.isdir("pipeline"):os.mkdir("pipeline")
    if len([d for d in os.listdir("in") if len(d)==8]) < CASE:
        with open("seeds.txt", mode='w') as f:
            for i in range(CASE):f.write(str(i)+"\n")
        subprocess.run('cargo run --release --bin gen seeds.txt',stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    if multi:
        with multiprocessing.Pool(max(1, multiprocessing.cpu_count()-2)) as pool:
            for seed, score in pool.imap_unordered(execute, [(i,file) for i in range(CASE)]):
                if score is not None:
                    scores.append([score, f'{seed:04}'])
                else:
                    return
    else:
        for i in tqdm(range(CASE)):
            seed,score = execute(i,file=file)
            if score is not None:
                scores.append([score, f'seed:{seed:04}'])
            else:
                return
    if print_score:
        for score,s in scores:
            print(s,' score:',score)
    scores.sort()
    total = sum([s[0] for s in scores])
    ave = total / CASE
    print(f'total: {total}')
    print(f'max: {scores[-1]}')
    print(f'ave: {ave}')
    print(f'min: {scores[0]}')