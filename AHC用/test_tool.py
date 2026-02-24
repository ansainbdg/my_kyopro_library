import subprocess
import os
import sys
import re
import json

def generate_cases(start_seed, num_cases):
    """
    指定された範囲のシードに対してテストケースを生成します。
    
    Args:
        start_seed (int): 開始シード。
        num_cases (int): 生成するケース数。
    """
    seeds = [str(start_seed + i) for i in range(num_cases)]
    with open("seeds.txt", "w") as f:
        f.write("\n".join(seeds))
    
    print(f"Generating {num_cases} cases starting from seed {start_seed}...")
    
    # gen.exeが存在するか確認し、なければcargoを使用する
    if os.path.exists("./gen.exe"):
        cmd = ["./gen.exe", "seeds.txt"]
    else:
        cmd = ["cargo", "run", "-r", "--bin", "gen", "seeds.txt"]
        
    subprocess.run(cmd, check=True, encoding="utf-8")
    print("Generation complete.")

def test_case_interactive(seed, program_path, debug=False, debug_in_only=False):
    """
    指定されたプログラムを使用してテストケースを対話的に実行します。
    
    Args:
        seed (int): 実行するテストケースのシード。
        program_path (str): プログラムへのパス (例: 'code01.py' や 'a.exe')。
        
    Returns:
        tuple: (score (int), stderr (str))
    """
    input_file = f"in/{seed:04d}.txt"
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found. Generating it...")
        generate_cases(seed, 1)
        
    # ユーザープログラムを実行するコマンドを決定する
    if program_path.endswith(".py"):
        user_cmd = f"python {program_path}" 
    elif program_path.endswith(".cpp"):
        # C++ファイルの場合、コンパイルしてから実行する
        exe_path = program_path.replace(".cpp", ".exe")
        print(f"Compiling {program_path}...")
        compile_result = subprocess.run(
            ["g++", "-O2", "-std=c++23", "-o", exe_path, program_path],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if compile_result.returncode != 0:
            print(f"Compilation failed:\n{compile_result.stderr}")
            return -1, f"Compilation failed:\n{compile_result.stderr}\n{compile_result.stdout}"
        print("Compilation successful.")
        user_cmd = f"./{exe_path}"
    elif program_path.endswith(".rs"):
        # Rustファイルの場合、Cargo経由でコンパイルしてから実行する
        import shutil
        basename = os.path.basename(program_path)
        bin_name = os.path.splitext(basename)[0]
        os.makedirs(os.path.join("src", "bin"), exist_ok=True)
        target_path = os.path.join("src", "bin", basename)
        if os.path.abspath(program_path) != os.path.abspath(target_path):
            shutil.copy2(program_path, target_path)

        print(f"Compiling {bin_name} via cargo...")
        compile_result = subprocess.run(
            ["cargo", "build", "--release", "--bin", bin_name],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if compile_result.returncode != 0:
            print(f"Compilation failed:\n{compile_result.stderr}")
            return -1, f"Compilation failed:\n{compile_result.stderr}\n{compile_result.stdout}"
        print("Compilation successful.")
        exe_path = f"target/release/{bin_name}.exe"
        user_cmd = f"./{exe_path}"
    elif program_path.endswith(".exe"):
        # .exeファイルの場合、./を付ける（testerがパスを見つけられるようにする）
        if not program_path.startswith("./") and not program_path.startswith(".\\") and not os.path.isabs(program_path):
            user_cmd = f"./{program_path}"
        else:
            user_cmd = program_path
    else:
        user_cmd = program_path
    
    # デバッグモードの場合、debug_proxy.py経由でユーザーコマンドを実行する
    if debug or debug_in_only:
        log_file = f"debug/{seed:04d}.log"
        os.makedirs("debug", exist_ok=True)
        in_only_flag = " --in-only" if debug_in_only else ""
        user_cmd = f'python debug_proxy.py --log {log_file}{in_only_flag} --cmd "{user_cmd}"'
        
    # テスターコマンドを特定する
    tester_cmd = []
    if os.path.exists("./tester.exe"):
         tester_cmd = ["./tester.exe"]
    else:
         tester_cmd = ["cargo", "run", "-r", "--bin", "tester"]
    
    # テスターの引数にユーザーコマンドを追加する
    # 使用法: tester cmd < in.txt
    # パイプ入力はsubprocessで行うため、'cmd'はtesterへの引数となります。
    
    # tester引数のためにユーザーコマンドを正しく分割する必要がある
    # 例: "python code01.py" -> ["python", "code01.py"]
    
    import shlex
    user_cmd_parts = shlex.split(user_cmd)
    
    full_cmd = tester_cmd + user_cmd_parts
    
    # Windowsでは文字列コマンドでshell=Trueを使うとパイプ処理が簡単かもしれないが、
    # subprocessはstdinファイルオブジェクトを渡すことができる。
    
    print(f"Running case seed={seed} with command: {' '.join(full_cmd)}")
    
    try:
        with open(input_file, "r") as inf:
            # 出力をキャプチャする
            result = subprocess.run(
                full_cmd,
                stdin=inf,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False # 失敗時でもstderrを取得したいので直ちにはraiseしない
            )
            
        stderr_output = result.stderr
        
        # スコアを抽出する。通常、stderrの最終行などに"Score = X"のような形式で出力される。
        
        score = -1
        # スコアのパースを試みる。正規表現で "Score = 12345" のような形式を探す（大文字小文字区別なし、空白許容）
        # 行ごとに検索して、最後に見つかったものを採用する（途中経過が出力される場合を考慮）
        score_pattern = re.compile(r"score\s*=\s*(\d+)", re.IGNORECASE)
        for line in stderr_output.splitlines():
            match = score_pattern.search(line)
            if match:
                score = int(match.group(1))
        
        return score, stderr_output

    except Exception as e:
        return -1, f"Error running test: {e}"

def generate_pahcer_config_file(program_path, start_seed, num_cases, score_max=True, config_path="pahcer_config.toml"):
    """pahcerの設定ファイルを生成します"""
    problem_name = os.path.basename(os.getcwd())
    end_seed = start_seed + num_cases
    objective = "Max" if score_max else "Min"
    
    if program_path.endswith(".py"):
        lang = "python"
    elif program_path.endswith(".cpp"):
        lang = "cpp"
    elif program_path.endswith(".rs"):
        lang = "rust"
    else:
        raise ValueError(f"Unsupported file type: {program_path}")

    config_content = f"""[general]
version = "0.3.1"

[problem]
problem_name = "{problem_name}"
objective = "{objective}"
score_regex = '(?m)^\\s*Score\\s*=\\s*(?P<score>\\d+)\\s*$'

[test]
start_seed = {start_seed}
end_seed = {end_seed}
threads = 0
out_dir = "./pahcer"

"""

    compile_steps = "compile_steps = []\n\n"
    if lang == "cpp":
        exe_path = program_path.replace(".cpp", ".exe")
        compile_steps = f"""[[test.compile_steps]]
program = "g++"
args = ["-O2", "-std=c++23", "-o", "{exe_path}", "{program_path}"]

"""
    elif lang == "rust":
        import shutil
        basename = os.path.basename(program_path)
        bin_name = os.path.splitext(basename)[0]
        os.makedirs(os.path.join("src", "bin"), exist_ok=True)
        target_path = os.path.join("src", "bin", basename)
        if os.path.abspath(program_path) != os.path.abspath(target_path):
            shutil.copy2(program_path, target_path)

        exe_path = f"target/release/{bin_name}.exe"
        compile_steps = f"""[[test.compile_steps]]
program = "cargo"
args = ["build", "--release", "--bin", "{bin_name}"]

"""

    if os.path.exists("./tester.exe"):
        tester_program = "./tester.exe"
        if lang == "python":
            tester_args_str = f'args = ["python", "{program_path}"]'
        else:
            tester_args_str = f'args = ["./{exe_path}"]'
    else:
        tester_program = "cargo"
        if lang == "python":
            tester_args_str = f'args = ["run", "--release", "--bin", "tester", "python", "{program_path}"]'
        else:
            tester_args_str = f'args = ["run", "--release", "--bin", "tester", "./{exe_path}"]'

    config_content += f"""{compile_steps}[[test.test_steps]]
program = "{tester_program}"
{tester_args_str}
stdin = "./in/{{SEED04}}.txt"
stdout = "./out/{{SEED04}}.txt"
stderr = "./err/{{SEED04}}.txt"
measure_time = true
"""

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)
    
    return lang


def run_pahcer(program_path, num_cases=100, interactive=True, score_max=True, start_seed=0,
               comment="", env=None, json_output=False, shuffle=False,
               no_result_file=False, freeze_best=False, no_compile=False):
    """
    pahcerを使ってテストケースを一括実行します。

    Args:
        program_path (str): 実行コードファイル (例: 'code04.py', 'code01.cpp')
        num_cases (int): テストケース数
        interactive (bool): インタラクティブ問題かどうか
        score_max (bool): スコアが大きい方が良いか
        start_seed (int): 開始シード
        comment (str): pahcer runに付与するコメント
        env (dict): 実行時に追加する環境変数 (ハイパーパラメータ等)
        json_output (bool): --json フラグ (stdoutにJSON出力)
        shuffle (bool): --shuffle フラグ (ケース順シャッフル)
        no_result_file (bool): --no-result-file フラグ
        freeze_best (bool): --freeze-best-scores フラグ
        no_compile (bool): --no-compile フラグ

    Returns:
        dict or None: json_output=True の場合はパースしたJSON辞書、それ以外はNone
    """
    # 問題名 = カレントディレクトリ名
    problem_name = os.path.basename(os.getcwd())

    # 既存のpahcer_config.tomlを削除
    config_path = "pahcer_config.toml"
    if os.path.exists(config_path):
        os.remove(config_path)
        print(f"Removed existing {config_path}")

    # 言語判定
    if program_path.endswith(".py"):
        lang = "python"
    elif program_path.endswith(".cpp"):
        lang = "cpp"
    elif program_path.endswith(".rs"):
        lang = "rust"
    else:
        print(f"Unsupported file type: {program_path}")
        return

    # pahcer init
    objective = "max" if score_max else "min"
    init_cmd = ["pahcer", "init", "-p", problem_name, "-o", objective, "-l", lang]
    if interactive:
        init_cmd.append("-i")

    print(f"Running: {' '.join(init_cmd)}")
    result = subprocess.run(init_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print(f"pahcer init failed:\\n{result.stderr}")
        return
    print("pahcer init complete.")

    try:
        lang = generate_pahcer_config_file(program_path, start_seed, num_cases, score_max, config_path)
        print(f"Updated {config_path} for {lang} with {program_path}")
    except ValueError as e:
        print(e)
        return

    end_seed = start_seed + num_cases
    # テストケースが足りなければ生成
    missing = []
    for s in range(start_seed, end_seed):
        if not os.path.exists(f"in/{s:04d}.txt"):
            missing.append(s)
    if missing:
        print(f"Generating {len(missing)} missing test cases...")
        generate_cases(start_seed, num_cases)

    # pahcer run
    run_cmd = ["pahcer", "run"]
    if comment:
        run_cmd += ["-c", comment]
    if json_output:
        run_cmd.append("--json")
    if shuffle:
        run_cmd.append("--shuffle")
    if no_result_file:
        run_cmd.append("--no-result-file")
    if freeze_best:
        run_cmd.append("--freeze-best-scores")
    if no_compile:
        run_cmd.append("--no-compile")
    print(f"Running pahcer run... (comment: {comment[:80] if comment else 'none'})")
    run_env = os.environ.copy()
    if env:
        run_env.update({k: str(v) for k, v in env.items()})
    run_result = subprocess.run(
        run_cmd,
        capture_output=json_output,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=run_env
    )
    if run_result.returncode != 0:
        print(f"pahcer run failed with exit code {run_result.returncode}")
        if json_output:
            print(f"Error output:\n{run_result.stderr}")
        return None

    if json_output:
        cases = []
        for line in run_result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError:
                # pahcerの進捗メッセージやエラーメッセージが混ざる可能性があるためスキップ
                continue
        return {"cases": cases}
    return None


if __name__ == "__main__":
    # ツール自体のテスト用簡易CLI
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "gen":
            generate_cases(int(sys.argv[2]), int(sys.argv[3]))
        elif cmd == "test":
            debug_flag = "--debug" in sys.argv
            debug_in_flag = "--debug-in" in sys.argv
            args = [a for a in sys.argv[2:] if a not in ("--debug", "--debug-in")]
            s, e = test_case_interactive(int(args[0]), args[1], debug=debug_flag, debug_in_only=debug_in_flag)
            print(f"Score: {s}")
            print(f"Stderr: {e}")
            if debug_flag or debug_in_flag:
                print(f"Debug log: debug/{int(args[0]):04d}.log")
        elif cmd == "pahcer":
            # python test_tool.py pahcer <program> [num_cases] [--no-interactive] [--min] [--start-seed N]
            args = [a for a in sys.argv[2:] if not a.startswith("--")]
            program = args[0]
            num_cases = int(args[1]) if len(args) > 1 else 100
            interactive = "--no-interactive" not in sys.argv
            score_max = "--min" not in sys.argv
            start_seed = 0
            for i, a in enumerate(sys.argv):
                if a == "--start-seed" and i + 1 < len(sys.argv):
                    start_seed = int(sys.argv[i + 1])
            comment = ""
            for i, a in enumerate(sys.argv):
                if a == "--comment" and i + 1 < len(sys.argv):
                    comment = sys.argv[i + 1]
            run_pahcer(program, num_cases, interactive, score_max, start_seed, comment=comment)

