import subprocess
import pipes
import multiprocessing
import os
from tqdm import tqdm
import time
import pandas as pd
import config
from bs4 import BeautifulSoup
import requests
import re
import time
import json


def check_stderr(stderr, seed=0):
    # subprocessのstderrからスコアを判定し、デバッグ標準出力をprintする
    if isinstance(stderr, list):
        for s in stderr:
            if not s:
                pass
            elif s.split()[-1].lstrip('-+').isdigit():
                return int(s.split()[-1])
            elif 'Finished' not in s and '.exe' not in s:
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


def visualizer(seed, input_file_path, output_file_path):
    if not os.path.isdir("pipeline"):
        os.mkdir("pipeline")
    pipefile = f'pipeline/pipefile_{seed:04}'
    with pipes.Template().open(pipefile, 'w') as p:
        subprocess.run(['cargo', "run", "--release", "--bin",
                       "vis", input_file_path, output_file_path], stdout=p)
    output = open(pipefile).read()
    assert output
    return check_stderr(output)


def execute_case(args, file="code1.py", TL=None):
    if len(args) == 3:
        seed, inputdir, outputdir, = args
    elif len(args) == 4:
        seed, inputdir, outputdir, file = args
        TL = None
    elif len(args) == 5:
        seed, inputdir, outputdir, file, TL = args
    else:
        raise ValueError('not enough values to unpack')
    if not os.path.isdir(inputdir):
        os.mkdir(inputdir)
    if not os.path.isdir(outputdir):
        os.mkdir(outputdir)
    input_file_path = f'{inputdir}/{seed:04}.txt'
    output_file_path = f'{outputdir}/{seed:04}.txt'
    with open(input_file_path) as fin:
        with open(output_file_path, 'w') as fout:
            start_time = time.perf_counter()
            try:
                proc = subprocess.run(
                    ['python', file], stdin=fin, stdout=fout, stderr=subprocess.PIPE, timeout=TL)
            except subprocess.TimeoutExpired:
                return seed, -1, -1
            end_time = time.perf_counter()
            try:
                if proc.stderr.decode('utf8').split('\n') != ['']:
                    print(proc.stderr.decode('utf8').split('\n'))
                if "Err" in proc.stderr.decode('utf8'):
                    return seed, -1, end_time-start_time
            except UnicodeDecodeError:
                print(proc.stderr)
                return seed, -1, end_time-start_time
            score = visualizer(seed, input_file_path, output_file_path)
    return seed, score, end_time-start_time


def execute_case_interactive(args, file="code1.py", inputdir='in', outputdir='out', TL=None):
    if isinstance(args, int):
        seed = args
    elif len(args) == 1:
        seed = args[0]
    elif len(args) == 2:
        seed, file = args
    elif len(args) == 3:
        seed, file, inputdir = args
    elif len(args) == 4:
        seed, file, inputdir, outputdir = args
        TL = None
    elif len(args) == 5:
        seed, file, inputdir, outputdir, TL = args
    else:
        raise ValueError('not enough values to unpack')
    if not os.path.isdir(inputdir):
        os.mkdir(inputdir)
    if not os.path.isdir(outputdir):
        os.mkdir(outputdir)
    input_file_path = f'{inputdir}/{seed:04}.txt'
    output_file_path = f'{outputdir}/{seed:04}.txt'
    start_time = time.perf_counter()
    try:
        proc = subprocess.run(
            f'cargo run --release --bin tester python {file} < {input_file_path} > {output_file_path}', stderr=subprocess.PIPE, shell=True, timeout=TL)
    except subprocess.TimeoutExpired:
        return seed, -1, -1
    end_time = time.perf_counter()
    try:
        score = check_stderr(proc.stderr.decode('utf8').split('\n'))
        return seed, score, end_time-start_time
    except UnicodeDecodeError:
        print(proc.stderr)
        return seed, -1, end_time-start_time


def execute_case(args, file="code1.py", inputdir='in', outputdir='out', TL=None):
    if isinstance(args, int):
        seed = args
    elif len(args) == 1:
        seed = args[0]
    elif len(args) == 2:
        seed, file = args
    elif len(args) == 3:
        seed, file, inputdir = args
    elif len(args) == 4:
        seed, file, inputdir, outputdir = args
        TL = None
    elif len(args) == 5:
        seed, file, inputdir, outputdir, TL = args
    else:
        raise ValueError('not enough values to unpack')
    if not os.path.isdir(inputdir):
        os.mkdir(inputdir)
    if not os.path.isdir(outputdir):
        os.mkdir(outputdir)
    if not os.path.isdir("pipeline"):
        os.mkdir("pipeline")
    input_file_path = f'{inputdir}/{seed:04}.txt'
    output_file_path = f'{outputdir}/{seed:04}.txt'
    with open(input_file_path) as fin:
        with open(output_file_path, 'w') as fout:
            start_time = time.perf_counter()
            try:
                proc = subprocess.run(
                    ['python', file], stdin=fin, stdout=fout, stderr=subprocess.PIPE, timeout=TL)
            except subprocess.TimeoutExpired:
                return seed, -1, -1
            end_time = time.perf_counter()
            try:
                if proc.stderr.decode('utf8').split('\n') != ['']:
                    print(proc.stderr.decode('utf8').split('\n'))
                if "Err" in proc.stderr.decode('utf8'):
                    return seed, -1, end_time-start_time
            except UnicodeDecodeError:
                print(proc.stderr)
                return seed, -1, end_time-start_time
            pipefile = f'pipeline/pipefile_{seed:04}'
            with pipes.Template().open(pipefile, 'w') as p:
                subprocess.run(['cargo', "run", "--release", "--bin",
                               "vis", input_file_path, output_file_path], stdout=p)
            output = open(pipefile).read()
            assert output
            score = check_stderr(output)
    return seed, score, end_time-start_time


def main(CASE=100, file='code1.py', interactive=False, to_csv=False, use_koteiseed=False, multi=False, print_score=True, TL=None, **option):
    scores = []
    if interactive:
        execute = execute_case_interactive
    else:
        execute = execute_case
    optionstr = ''
    indir = 'in'
    outdir = 'out'
    for key, value in option.items():
        optionstr += f' --{key}={value}'
        indir += f'{key}{value}'
        outdir += f'{key}{value}'
    if not os.path.isdir(indir):
        os.mkdir(indir)
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    if not os.path.isdir("pipeline"):
        os.mkdir("pipeline")
    # if casenum:=len([d for d in os.listdir(indir) if len(d)==8]) < CASE:
    if not use_koteiseed:
        with open("seedstmp.txt", mode='w') as f:
            for i in range(CASE):
                f.write(str(i)+"\n")
        subprocess.run(
            f'cargo run --release --bin gen seedstmp.txt --dir={indir}{optionstr}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        os.remove("seedstmp.txt")
    else:
        subprocess.run(
            f'cargo run --release --bin gen seeds.txt --dir={indir}{optionstr}', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        casenum = len([d for d in os.listdir(indir) if len(d) == 8])
        CASE = min(CASE, casenum)
    if multi:
        with multiprocessing.Pool(max(1, multiprocessing.cpu_count()-2)) as pool:
            for seed, score, execution_time in pool.imap_unordered(execute, [(i, file, indir, outdir, TL) for i in range(CASE)]):
                if score is not None:
                    scores.append([seed, score, execution_time])
                else:
                    return
    else:
        for i in tqdm(range(CASE)):
            seed, score, execution_time = execute(
                i, file=file, inputdir=indir, outputdir=outdir, TL=TL)
            if score is not None:
                scores.append([seed, score, execution_time])
            else:
                return
    df = pd.DataFrame(scores).set_index(0).sort_index()
    df.index.name = 'case'
    df.columns = [f'score_{file[:-3]}', f'time_{file[:-3]}']
    desc = df.describe()
    if print_score:
        print(df)
    # df.to_csv('score.csv')
    if to_csv:
        if os.path.isfile('score.csv'):
            df2 = pd.read_csv('score.csv', index_col=0)
            df = pd.merge(df2, df, left_index=True,
                          right_index=True, how='outer')
        df.to_csv('score.csv')
    return desc
    # print(f'maxtime: {sorted(scores,key=lambda x:x[2],reverse=True)[0]}')


def login(session):
    LOGIN_URL = 'https://atcoder.jp/login'
    login_info = {
        "csrf_token": get_csrf_token(session, LOGIN_URL),
        "username": config.USERNAME,
        "password": config.PASSWORD
    }
    result = session.post(LOGIN_URL, data=login_info)
    # print(result.text)


def get_csrf_token(session, url):
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    csrf_token = soup.find(attrs={'name': 'csrf_token'}).get('value')
    return csrf_token


def test_code(session, code, input_txt):
    test_url = f'https://atcoder.jp/contests/abc001/custom_test'
    # test_url = 'https://atcoder.jp/contests/abc172/submit'
    test_info = {
        'csrf_token': get_csrf_token(session, test_url),
        'data.LanguageId': 5078,  # pypy
        'sourceCode': code,
        'input': input_txt
        # "data.TaskScreenName": 'abc172_a'
    }
    result = session.post(test_url+'/submit/json', data=test_info)

    time.sleep(20)

    response = session.get(test_url)
    soup = BeautifulSoup(response.content, "html.parser")
    for script in soup.find_all('script'):
        if 'var result =' in script.text:
            target_text = script.text
            break
    else:
        raise ValueError

    # Regular expressions for extracting variables
    result_pattern = r"var result = ({.*?});"
    stdout_pattern = r"var stdout = \"(.*?)\";"
    stderr_pattern = r"var stderr = \"(.*?)\";"

    # Searching for matches
    result_match = re.search(result_pattern, target_text, re.DOTALL)
    stdout_match = re.search(stdout_pattern, target_text, re.DOTALL)
    stderr_match = re.search(stderr_pattern, target_text, re.DOTALL)

    # Extracting the matched groups
    result = result_match.group(1) if result_match else None
    stdout = stdout_match.group(1) if stdout_match else None
    stderr = stderr_match.group(1) if stderr_match else None

    # 必要な値を取り出す
    result_data = json.loads(result)
    TimeConsumption = result_data.get("TimeConsumption")
    return stdout, stderr, TimeConsumption


def execute_case_atcoder(args, file="code1.py", inputdir='in', outputdir='out'):
    if isinstance(args, int):
        seed = args
    elif len(args) == 1:
        seed = args[0]
    elif len(args) == 2:
        seed, file = args
    elif len(args) == 3:
        seed, file, inputdir, = args
    elif len(args) == 4:
        seed, file, inputdir, outputdir = args
    else:
        raise ValueError('not enough values to unpack')
    if not os.path.isdir(inputdir):
        os.mkdir(inputdir)
    if not os.path.isdir(outputdir):
        os.mkdir(outputdir)
    input_file_path = f'{inputdir}/{seed:04}.txt'
    output_file_path = f'{outputdir}/{seed:04}.txt'
    with open(input_file_path) as fin:
        input_text = fin.read()
    with open(file, encoding='UTF8') as fin:
        code = fin.read()

    session = requests.session()
    login(session)
    stdout, stderr, TimeConsumption = test_code(session, code, input_text)

    if 'Traceback (most recent call last)' in stderr:
        return seed, -1, TimeConsumption/1000
    if TimeConsumption/1000 > 10:
        return seed, -1, TimeConsumption/1000

    with open(output_file_path, 'w') as fout:
        fout.write(stdout.replace('\\n', '\n'))

    score = visualizer(seed, input_file_path, output_file_path)

    return seed, score, TimeConsumption/1000


def execute_case_atcoder_interactive(args, file="code1.py", inputdir='in', outputdir='out'):
    if isinstance(args, int):
        seed = args
    elif len(args) == 1:
        seed = args[0]
    elif len(args) == 2:
        seed, file = args
    elif len(args) == 3:
        seed, file, inputdir, = args
    elif len(args) == 4:
        seed, file, inputdir, outputdir = args
    else:
        raise ValueError('not enough values to unpack')
    if not os.path.isdir(inputdir):
        os.mkdir(inputdir)
    if not os.path.isdir(outputdir):
        os.mkdir(outputdir)
    if not os.path.isdir("pipeline"):
        os.mkdir("pipeline")
    with open(file, encoding='UTF8') as fin:
        code = fin.read()
    pastinput = 'def input2(): return sys.stdin.readline().rstrip()'
    newinput = f'def input2():\n    input_txt = input()\n    with open(\'pipeline/{seed:04}.txt\', mode=\'a\') as f:\n        f.write(input_txt+\'\\n\')\n    return input_txt.rstrip()\n\n'
    newcode = code.replace('input()', 'input2()')
    if pastinput in newcode:
        newcode = newcode.replace(pastinput, newinput)
    else:
        newcode = newinput + newcode
    repfile = file.replace('.py', f'{seed:04}.py')
    with open(f'pipeline/{repfile}', 'w', encoding='UTF8') as fout:
        fout.write(newcode)
    if os.path.exists(f'pipeline/{seed:04}.txt'):
        os.remove(f'pipeline/{seed:04}.txt')
    _, score, time = execute_case_interactive(
        seed, file=f'pipeline/{repfile}', inputdir=inputdir, outputdir=outputdir)
    with open(f'pipeline/{seed:04}.txt') as fin:
        input_text = fin.read()

    session = requests.session()
    login(session)
    stdout2, _, TimeConsumption = test_code(session, code, input_text)

    with open(f'{outputdir}/{seed:04}.txt') as fout:
        stdout1 = fout.read()
        print('出力一致:', stdout1 == stdout2[4].replace('\\n', '\n'))

    return seed, score, time,TimeConsumption/1000
