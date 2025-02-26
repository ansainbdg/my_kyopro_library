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
import json
import toml
from datetime import datetime
from math import log10

def newlog10(x):
    return log10(x+1)


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
    #test_url = f'https://atcoder.jp/contests/abc001/custom_test'
    test_url = f'https://atcoder.jp/contests/abc394/custom_test'
    # test_url = 'https://atcoder.jp/contests/abc172/submit'
    test_info = {
        'csrf_token': get_csrf_token(session, test_url),
        'data.LanguageId': 5078,  # pypy
        #'data.LanguageId': 5031,  # c++
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

def extract_score(s: str) -> float | None:
    scores = []
    score_pattern = re.compile(r"Score\s*=\s*(?P<score>\d+(?:\.\d+)?)")
    # 正規表現で全マッチを反復処理
    for m in score_pattern.finditer(s):
        # "score" という名前のキャプチャグループを取得して数値にパース
        try:
            score = int(m.group("score"))
            scores.append(score)
        except (ValueError, AttributeError):
            continue
    # マッチしたものがあれば最後の値を返す
    return scores[-1] if scores else None



def visualizer(seed, input_file_path, output_file_path):
    if not os.path.isdir("pipeline"):
        os.mkdir("pipeline")
    pipefile = f'pipeline/pipefile_{seed:04}'
    with pipes.Template().open(pipefile, 'w') as p:
        subprocess.run(['cargo', "run", "--release", "--bin",
                       "vis", input_file_path, output_file_path], stdout=p)
    output = open(pipefile).read()
    return extract_score(output)


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
            f'cargo run --release --bin tester python {file} < {input_file_path} > {output_file_path}', stdout=subprocess.PIPE ,stderr=subprocess.PIPE, shell=True, timeout=TL)
    except subprocess.TimeoutExpired:
        return seed, 0, 0,"TimeoutExpired",""
    end_time = time.perf_counter()
    try:
        if "Err" in proc.stderr.decode('utf8'):
            return seed, 0, end_time-start_time,"RuntimeError",proc.stderr.decode('utf8')
    except UnicodeDecodeError:
        if "Err" in proc.stderr.decode('utf8'):
            return seed, 0, end_time-start_time,"RuntimeError",proc.stderr.decode('shift-jis')
    score = extract_score(proc.stderr.decode('utf8'))
    return seed, score, end_time-start_time,"Accepted" if score!=0 else "Wrong Answer",proc.stderr.decode('utf8')



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
                return seed, 0, 0,"TimeoutExpired",""
            end_time = time.perf_counter()
            try:
                if "Err" in proc.stderr.decode('utf8'):
                    return seed, 0, end_time-start_time,"RuntimeError",proc.stderr.decode('utf8')
            except UnicodeDecodeError:
                if "Err" in proc.stderr.decode('utf8'):
                    return seed, 0, end_time-start_time,"RuntimeError",proc.stderr.decode('shift-jis')
            pipefile = f'pipeline/pipefile_{seed:04}'
            with pipes.Template().open(pipefile, 'w') as p:
                subprocess.run(['cargo', "run", "--release", "--bin",
                               "vis", input_file_path, output_file_path], stdout=p)
            output = open(pipefile).read()
            score = extract_score(output)
    return seed, score, end_time-start_time,"Accepted" if score!=0 else "Wrong Answer",proc.stderr.decode('utf8')



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
        return seed, 0, TimeConsumption/1000,"RuntimeError",stderr
    if TimeConsumption/1000 > 10:
        return seed, 0, TimeConsumption/1000,"TimelimitExceed",stderr

    with open(output_file_path, 'w') as fout:
        fout.write(stdout.replace('\\n', '\n'))

    score = visualizer(seed, input_file_path, output_file_path)

    return seed, score, TimeConsumption/1000,"Accepted" if score!=0 else "Wrong Answer",stderr


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
    _, score, time, result,stderr = execute_case_interactive(
        seed, file=f'pipeline/{repfile}', inputdir=inputdir, outputdir=outputdir)
    
    if result!="Accepted":
        return seed,score, time, result,stderr

    with open(f'pipeline/{seed:04}.txt') as fin:
        input_text = fin.read()

    session = requests.session()
    login(session)
    stdout2, _, TimeConsumption = test_code(session, code, input_text)

    if 'Traceback (most recent call last)' in stderr:
        return seed, score, TimeConsumption/1000,"出力結果不一致&error",stderr
    if TimeConsumption/1000 > 10:
        return seed, score, TimeConsumption/1000,"TimelimitExceed",stderr

    with open(f'{outputdir}/{seed:04}.txt') as fout:
        stdout1 = fout.read()
        if stdout1 == stdout2.replace('\\n', '\n'):
            return seed, score, TimeConsumption/1000,result,stderr
        else:
            return seed, score, TimeConsumption/1000,"出力結果不一致",stderr

def execute_case_main(args,file="code1.py",interactive=False,atcoder=False,inputdir='in', outputdir='out'):
    if not interactive and not atcoder:
        _,score,times,result,stderr = execute_case(args,file,inputdir,outputdir)
    elif not interactive and atcoder:
        _,score,times,result,stderr = execute_case_atcoder(args,file,inputdir,outputdir)
    elif interactive and not atcoder:
        _,score,times,result,stderr = execute_case_interactive(args,file,inputdir,outputdir)
    else:
        _,score,times,result,stderr = execute_case_atcoder_interactive(args,file,inputdir,outputdir)
    print(f"result: {result}")
    print(f"score: {score}")
    print(f"time: {times}")
    return re.split(r'\r\n|\n|\r|\x85|\u2028|\u2029', stderr)



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
            for seed, score, execution_time, state, _ in pool.imap_unordered(execute, [(i, file, indir, outdir, TL) for i in range(CASE)]):
                if score is not None:
                    scores.append([seed, score,newlog10(score),state,execution_time])
                else:
                    return
    else:
        for i in tqdm(range(CASE)):
            seed, score, execution_time,state, _ = execute(
                i, file=file, inputdir=indir, outputdir=outdir, TL=TL)
            if score is not None:
                scores.append([seed, score,newlog10(score),state,execution_time])
            else:
                return
    df = pd.DataFrame(scores).set_index(0).sort_index()
    timestamp = datetime.now().strftime("%d%H%M")
    df.index.name = 'case'
    df.columns = [f'score_{timestamp}_{file[:-3]}',f'log10_{timestamp}_{file[:-3]}',f'state_{timestamp}_{file[:-3]}', f'time_{timestamp}_{file[:-3]}']
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


def run_pahcer_init(problem: str, objective: str, language: str, interactive: bool = False):
    """
    `pahcer init` コマンドを実行する。

    Args:
        problem (str): コンテスト名（必須）
        objective (str): "max" または "min"（必須）
        language (str): "cpp", "python", "rust", "go" のいずれか（必須）
        interactive (bool): インタラクティブ問題の場合に指定（オプション）

    Returns:
        subprocess.CompletedProcess: 実行結果
    """
    # コマンドの基本部分
    cmd = ["pahcer", "init", "-p", problem, "-o", objective, "-l", language]

    # インタラクティブオプションが指定されている場合
    if interactive:
        cmd.append("-i")

    # コマンドを実行
    result = subprocess.run(cmd, capture_output=True, text=True)

    # 実行結果を返す
    return result


def update_pahcer_config(program_name: str, config_path: str = "pahcer_config.toml"):
    """
    `pahcer_config.toml` の `args` の値を指定されたプログラム名に更新する。

    Args:
        program_name (str): 実行するプログラムの名前（例: "my_script.py"）
        config_path (str): 設定ファイルのパス（デフォルトは "pahcer_config.toml"）
    """

    try:
        # 設定ファイルを読み込む
        with open(config_path, "r", encoding="utf-8") as file:
            config_data = toml.load(file)

        # `test.test_steps` の `program = "py"` を探して `args` を更新
        for step in config_data.get("test", {}).get("test_steps", []):
            if step.get("program") == "py" or step.get("program") == "python":
                step["program"] = "python"
                step["args"] = [f"{program_name}"]
                step["stdin"] = step["stdin"].replace("tools/","").replace("./","")
                step["stdout"] = step["stdout"].replace("tools/","").replace("./","")
                step["stderr"] = step["stderr"].replace("tools/","").replace("./","")
            if step.get("program") == "cargo":
                step["args"] = [ "run", "--bin", "vis", "--release", "in/{SEED04}.txt", "out/{SEED04}.txt",]
                step["current_dir"] = "."

        # 更新した設定をファイルに書き戻す
        with open(config_path, "w", encoding="utf-8") as file:
            toml.dump(config_data, file)
    
    except FileNotFoundError:
        print(f"Error: 設定ファイル '{config_path}' が見つかりません。")


def run_pahcer_run(
    program_name: str,
    comment: str = None, 
    json_output: bool = False, 
    shuffle: bool = False, 
    setting_file: str = "pahcer_config.toml", 
    freeze_best_scores: bool = False, 
    no_result_file: bool = False, 
    no_compile: bool = False
):
    """
    `pahcer run` コマンドを実行する前に `pahcer_config.toml` の `args` を更新する。

    Args:
        program_name (str): 実行するプログラム名。
        comment (str, optional): テストケースへのコメント。
        json_output (bool, optional): JSON形式で結果を出力する場合に指定。
        shuffle (bool, optional): テストケースの実行順をシャッフルする場合に指定。
        setting_file (str, optional): 読み込む設定ファイルのパス。
        freeze_best_scores (bool, optional): ベストスコアの更新を防ぐ場合に指定。
        no_result_file (bool, optional): 実行結果のファイル出力を行わない場合に指定。
        no_compile (bool, optional): 起動時のコンパイル処理をスキップする場合に指定。

    Returns:
        subprocess.CompletedProcess: 実行結果
    """
    # 設定ファイルの args を更新
    update_pahcer_config(program_name, setting_file)

    # コマンドの基本部分
    cmd = ["pahcer", "run"]

    # 各オプションの処理
    if comment:
        cmd.extend(["-c", comment])
    if json_output:
        cmd.append("-j")
    if shuffle:
        cmd.append("--shuffle")
    if setting_file:
        cmd.extend(["--setting-file", setting_file])
    if freeze_best_scores:
        cmd.append("--freeze-best-scores")
    if no_result_file:
        cmd.append("--no-result-file")
    if no_compile:
        cmd.append("--no-compile")

    # コマンドを実行
    result = subprocess.run(cmd, capture_output=True, text=True,encoding="utf-8")

    # 実行結果を返す
    return result.stdout
