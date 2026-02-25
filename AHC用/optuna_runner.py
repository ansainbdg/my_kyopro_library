"""
Optuna連携ハイパーパラメータ最適化ランナー

使い方:
  # 絶対スコアモード
  python optuna_runner.py code01.cpp --mode absolute --n-trials 50 --num-cases 100

  # 相対スコアモード（ウォームアップ3回付き）
  python optuna_runner.py code01.cpp --mode relative --n-trials 50 --num-cases 100 --n-random-warmup 3

  # Jupyter Notebook から:
  from optuna_runner import run_optuna
  run_optuna("code01.cpp", param_defs={...}, mode="absolute", n_trials=50)
"""

import json
import os
import pickle
import random
import subprocess
import signal
import sys
import glob
from datetime import datetime

import optuna
import optunahub
import pandas as pd

from test_tool import run_pahcer, generate_cases, generate_pahcer_config_file

# ============================================================
# デフォルトのハイパーパラメータ定義（CLIテスト用）
# Jupyter等から呼ぶ場合は run_optuna() の引数で上書き可能
# ============================================================
DEFAULT_PARAM_DEFS = {
    "HP_RND_LMAX": ("int", 8000, 10000),
    "HP_RND_MIN":  ("int", 0, 2000),
}

BEST_SCORES_PATH = os.path.join("pahcer", "best_scores.json")
STUDY_PKL_PATH = "study.pkl"
STUDY_CSV_PATH = "study.csv"


# ============================================================
# ハイパラ生成ユーティリティ
# ============================================================
def generate_params_for_trial(trial, param_defs):
    """Optuna trial からハイパラを生成し、環境変数用の dict を返す。"""
    params = {}
    for name, spec in param_defs.items():
        kind = spec[0]
        if kind == "int":
            params[name] = str(trial.suggest_int(name, spec[1], spec[2]))
        elif kind == "float":
            params[name] = str(trial.suggest_float(name, spec[1], spec[2]))
        elif kind == "categorical":
            params[name] = str(trial.suggest_categorical(name, spec[1]))
        else:
            raise ValueError(f"Unknown param type: {kind}")
    return params


def generate_params_random(param_defs):
    """ランダムにハイパラを生成し、環境変数用の dict を返す。"""
    params = {}
    for name, spec in param_defs.items():
        kind = spec[0]
        if kind == "int":
            params[name] = str(random.randint(spec[1], spec[2]))
        elif kind == "float":
            params[name] = str(random.uniform(spec[1], spec[2]))
        elif kind == "categorical":
            params[name] = str(random.choice(spec[1]))
        else:
            raise ValueError(f"Unknown param type: {kind}")
    return params


# ============================================================
# best_scores.json の読み込み
# ============================================================
def load_best_scores():
    """best_scores.json を読み込んで {seed_int: score} の dict を返す。"""
    if not os.path.exists(BEST_SCORES_PATH):
        return {}
    with open(BEST_SCORES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {int(k): v for k, v in data.items()}


# ============================================================
# pahcer run を Popen で起動し、リアルタイムに結果を返すジェネレータ
# ============================================================
def run_pahcer_streaming(env=None, no_compile=False):
    """
    pahcer run --json --shuffle --no-result-file --freeze-best-scores を実行し、
    1ケースずつ結果をyieldするジェネレータ。

    Yields:
        dict: {"seed": int, "score": int, "relative_score": float, ...}
    
    Returns (via generator close or StopIteration):
        None
    """
    cmd = [
        "pahcer", "run",
        "--json",
        "--shuffle",
        "--no-result-file",
        "--freeze-best-scores",
    ]
    if no_compile:
        cmd.append("--no-compile")

    run_env = os.environ.copy()
    if env:
        run_env.update({k: str(v) for k, v in env.items()})

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,  # stderrは読まないのでDEVNULLにしてパイプデッドロックを防ぐ
        env=run_env,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    try:
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                result = json.loads(line)
            except json.JSONDecodeError:
                continue

            if result.get("error_message", ""):
                _kill_process(process)
                raise RuntimeError(f"pahcer error (seed={result.get('seed')}): {result['error_message']}")

            yield result
    finally:
        # ジェネレータが途中で閉じられた場合もプロセスをクリーンアップ
        _kill_process(process)


def _kill_process(process):
    """プロセスを確実に終了させる。"""
    try:
        process.terminate()
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    except Exception:
        try:
            process.kill()
        except Exception:
            pass


# ============================================================
# Objective クラス
# ============================================================
class AbsoluteObjective:
    """絶対スコアモードの目的関数。"""

    def __init__(self, param_defs, first_trial_number=0):
        self.param_defs = param_defs
        self.first_trial_number = first_trial_number

    def __call__(self, trial):
        params = generate_params_for_trial(trial, self.param_defs)
        no_compile = (trial.number != self.first_trial_number)

        scores = []
        gen = run_pahcer_streaming(env=params, no_compile=no_compile)

        try:
            for result in gen:
                score = result["score"]
                seed = result["seed"]
                scores.append(score)
                trial.report(score, seed)

                if trial.should_prune():
                    print(f"  Trial {trial.number} pruned at {len(scores)} cases.")
                    gen.close()
                    return _handle_prune(trial, scores)
        except RuntimeError as e:
            print(f"  Trial {trial.number} error: {e}")
            raise optuna.TrialPruned()

        avg = sum(scores) / len(scores) if scores else 0
        print(f"  Trial {trial.number} finished: avg_score={avg:.2f} ({len(scores)} cases)")
        return avg


class RelativeObjective:
    """相対スコアモードの目的関数。best_scores を事前にメモリ保持。"""

    def __init__(self, param_defs, best_scores, score_max=True, first_trial_number=0):
        self.param_defs = param_defs
        self.best_scores = best_scores
        self.score_max = score_max
        self.first_trial_number = first_trial_number

    def _relative(self, score, seed):
        best = self.best_scores.get(seed)
        if best is None or best == 0:
            return 0.0
        if score == 0:
            return 0.0
        if self.score_max:
            return score / best
        else:
            return best / score

    def __call__(self, trial):
        params = generate_params_for_trial(trial, self.param_defs)
        no_compile = (trial.number != self.first_trial_number)

        rel_scores = []
        gen = run_pahcer_streaming(env=params, no_compile=no_compile)

        try:
            for result in gen:
                score = result["score"]
                seed = result["seed"]
                rel = self._relative(score, seed)
                rel_scores.append(rel)
                trial.report(rel, seed)

                if trial.should_prune():
                    print(f"  Trial {trial.number} pruned at {len(rel_scores)} cases.")
                    gen.close()
                    return _handle_prune(trial, rel_scores)
        except RuntimeError as e:
            print(f"  Trial {trial.number} error: {e}")
            raise optuna.TrialPruned()

        avg = sum(rel_scores) / len(rel_scores) if rel_scores else 0
        print(f"  Trial {trial.number} finished: avg_relative={avg:.4f} ({len(rel_scores)} cases)")
        return avg


def _handle_prune(trial, scores):
    """枝刈り時の処理：ベストより良ければ TrialPruned、そうでなければ平均値を返す。"""
    objective_value = sum(scores) / len(scores) if scores else 0

    try:
        best_value = trial.study.best_value
        is_better = (
            (trial.study.direction == optuna.study.StudyDirection.MINIMIZE
             and objective_value < best_value)
            or
            (trial.study.direction == optuna.study.StudyDirection.MAXIMIZE
             and objective_value > best_value)
        )
        if is_better:
            raise optuna.TrialPruned()
    except ValueError:
        # まだベスト値がない場合
        pass

    return objective_value


# ============================================================
# pahcer 初期設定（最初の1回だけ）
# ============================================================
def setup_pahcer(program_path, num_cases, start_seed, interactive, score_max):
    """pahcer init + config生成 + テストケース生成を行う。"""
    problem_name = os.path.basename(os.getcwd())
    config_path = "pahcer_config.toml"

    # 既存config削除
    if os.path.exists(config_path):
        os.remove(config_path)

    # 言語判定
    if program_path.endswith(".py"):
        lang = "python"
    elif program_path.endswith(".cpp"):
        lang = "cpp"
    elif program_path.endswith(".rs"):
        lang = "rust"
    else:
        raise ValueError(f"Unsupported file type: {program_path}")

    # pahcer init
    objective = "max" if score_max else "min"
    init_cmd = ["pahcer", "init", "-p", problem_name, "-o", objective, "-l", lang]
    if interactive:
        init_cmd.append("-i")

    print(f"Running: {' '.join(init_cmd)}")
    result = subprocess.run(init_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"pahcer init failed: {result.stderr}")
    print("pahcer init complete.")

    # config生成
    generate_pahcer_config_file(program_path, start_seed, num_cases, score_max, interactive, config_path)
    print(f"Generated {config_path}")

    # テストケース生成
    end_seed = start_seed + num_cases
    missing = [s for s in range(start_seed, end_seed) if not os.path.exists(f"in/{s:04d}.txt")]
    if missing:
        print(f"Generating {len(missing)} missing test cases...")
        generate_cases(start_seed, num_cases)


# ============================================================
# Study の保存・読み込み
# ============================================================
def save_study(study, path=STUDY_PKL_PATH):
    with open(path, "wb") as f:
        pickle.dump(study, f)


def load_study(path=STUDY_PKL_PATH):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None


# ============================================================
# ランダムウォームアップ（相対モード用）
# ============================================================
def run_random_warmup(program_path, param_defs, num_cases, start_seed,
                      interactive, score_max, n_warmup):
    """
    ランダムハイパラで n_warmup 回 run_pahcer を実行し、
    best_scores.json を更新する。結果を study.csv に保存。
    既存の study.csv があればそこから再開する。
    
    total_relative は全ウォームアップ完了後に最終 best_scores.json で
    まとめて計算する（各ラン後に best_scores が変わるため）。
    
    Returns:
        list[dict]: 各ウォームアップの {params, scores_by_seed, total_relative} のリスト
    """
    warmup_results = []
    
    # 既存CSVからの再開
    completed_count = 0
    if os.path.exists(STUDY_CSV_PATH):
        existing_df = pd.read_csv(STUDY_CSV_PATH, encoding="utf-8")
        completed_count = len(existing_df)
        print(f"\nFound existing {STUDY_CSV_PATH} with {completed_count} warmup runs.")
        
        if completed_count >= n_warmup:
            print(f"All {n_warmup} warmups already completed. Skipping warmup phase.")
            # 既存データから warmup_results を復元
            return _rebuild_warmup_results_from_csv(existing_df, param_defs, score_max, num_cases, start_seed)
        
        # 既存データから途中結果を復元
        for _, row in existing_df.iterrows():
            params = {}
            scores_by_seed = {}
            for col in row.index:
                if col in param_defs:
                    params[col] = str(row[col])
                elif col.startswith("seed_"):
                    seed = int(col.replace("seed_", ""))
                    scores_by_seed[seed] = int(row[col])
            warmup_results.append({
                "params": params,
                "scores_by_seed": scores_by_seed,
                "total_relative": None,  # 後で計算
            })
        print(f"Resuming from warmup {completed_count + 1}/{n_warmup}...")

    # 未完了分のウォームアップを実行
    for i in range(completed_count, n_warmup):
        params = generate_params_random(param_defs)
        print(f"\n=== Random Warmup {i+1}/{n_warmup} ===")
        print(f"  Params: {params}")

        # run_pahcer で実行（freeze_best=False でベストスコア更新あり）
        result = run_pahcer(
            program_path,
            num_cases=num_cases,
            interactive=interactive,
            score_max=score_max,
            start_seed=start_seed,
            comment=f"warmup_{i}",
            env=params,
            json_output=True,
            shuffle=False,
            no_result_file=False,
            freeze_best=False,
            no_compile=(i > 0),
        )

        # スコアを取得
        scores_by_seed = {}
        if result and "cases" in result:
            for case in result["cases"]:
                scores_by_seed[case["seed"]] = case["score"]

        warmup_results.append({
            "params": params,
            "scores_by_seed": scores_by_seed,
            "total_relative": None,  # 後で計算
        })

        # CSVに即座に保存（インクリメンタル）
        _save_warmup_csv(warmup_results, param_defs, start_seed, num_cases)
        print(f"  Scores saved to {STUDY_CSV_PATH} ({i+1}/{n_warmup})")

    # 全ウォームアップ完了後、最終 best_scores.json で total_relative をまとめて計算
    best_scores = load_best_scores()
    for wr in warmup_results:
        total_relative = 0.0
        for seed, score in wr["scores_by_seed"].items():
            best = best_scores.get(seed, 0)
            if best > 0 and score > 0:
                if score_max:
                    total_relative += score / best
                else:
                    total_relative += best / score
        wr["total_relative"] = total_relative

    # total_relative 付きでCSVを最終保存
    _save_warmup_csv(warmup_results, param_defs, start_seed, num_cases)
    
    print(f"\nWarmup complete. Results saved to {STUDY_CSV_PATH}")
    for i, wr in enumerate(warmup_results):
        print(f"  Warmup {i}: total_relative={wr['total_relative']:.4f}")

    return warmup_results


def _save_warmup_csv(warmup_results, param_defs, start_seed, num_cases):
    """ウォームアップ結果をCSVに保存する。"""
    csv_rows = []
    for wr in warmup_results:
        row = dict(wr["params"])
        for seed in range(start_seed, start_seed + num_cases):
            row[f"seed_{seed:04d}"] = wr["scores_by_seed"].get(seed, 0)
        if wr["total_relative"] is not None:
            row["total_relative"] = wr["total_relative"]
        csv_rows.append(row)
    
    df = pd.DataFrame(csv_rows)
    df.to_csv(STUDY_CSV_PATH, index=False, encoding="utf-8")


def _rebuild_warmup_results_from_csv(df, param_defs, score_max, num_cases, start_seed):
    """既存CSVからwarmup_resultsを復元し、最終best_scoresでtotal_relativeを再計算する。"""
    warmup_results = []
    for _, row in df.iterrows():
        params = {}
        scores_by_seed = {}
        for col in row.index:
            if col in param_defs:
                params[col] = str(row[col])
            elif col.startswith("seed_"):
                seed = int(col.replace("seed_", ""))
                scores_by_seed[seed] = int(row[col])
        warmup_results.append({
            "params": params,
            "scores_by_seed": scores_by_seed,
            "total_relative": None,
        })
    
    # 最終 best_scores で再計算
    best_scores = load_best_scores()
    for wr in warmup_results:
        total_relative = 0.0
        for seed, score in wr["scores_by_seed"].items():
            best = best_scores.get(seed, 0)
            if best > 0 and score > 0:
                if score_max:
                    total_relative += score / best
                else:
                    total_relative += best / score
        wr["total_relative"] = total_relative
    
    return warmup_results


def inject_warmup_to_study(study, warmup_results, param_defs, score_max):
    """ウォームアップ結果を Optuna study に注入する。"""
    for wr in warmup_results:
        # パラメータを Optuna の内部名に変換
        distributions = {}
        params_for_optuna = {}
        for name, spec in param_defs.items():
            kind = spec[0]
            raw_val = wr["params"][name]
            if kind == "int":
                distributions[name] = optuna.distributions.IntDistribution(spec[1], spec[2])
                params_for_optuna[name] = int(raw_val)
            elif kind == "float":
                distributions[name] = optuna.distributions.FloatDistribution(spec[1], spec[2])
                params_for_optuna[name] = float(raw_val)
            elif kind == "categorical":
                distributions[name] = optuna.distributions.CategoricalDistribution(spec[1])
                params_for_optuna[name] = raw_val

        # 目的関数値 = 平均相対スコア
        n_cases = len(wr["scores_by_seed"]) if wr["scores_by_seed"] else 1
        avg_relative = wr["total_relative"] / n_cases

        trial = optuna.trial.create_trial(
            params=params_for_optuna,
            distributions=distributions,
            values=[avg_relative],
            state=optuna.trial.TrialState.COMPLETE,
        )
        study.add_trial(trial)

    print(f"Injected {len(warmup_results)} warmup trials into Optuna study.")


# ============================================================
# メイン関数
# ============================================================
def run_optuna(
    program_path,
    param_defs=None,
    num_cases=100,
    start_seed=0,
    n_trials=50,
    interactive=False,
    score_max=True,
    mode="absolute",
    n_random_warmup=0,
    study_name="optuna-study",
    sampler=None,
):
    """
    Optuna連携ハイパーパラメータ最適化を実行する。

    Args:
        program_path (str): 実行コードファイル (例: 'code01.cpp')
        param_defs (dict): ハイパーパラメータ定義
            例: {"HP_A": ("int", 5, 30), "HP_B": ("float", 1.2, 1.6), "HP_C": ("categorical", ["A","B"])}
        num_cases (int): テストケース数
        start_seed (int): 開始シード
        n_trials (int): Optuna 反復回数
        interactive (bool): インタラクティブ問題か
        score_max (bool): スコア最大化か
        mode (str): "absolute" or "relative"
        n_random_warmup (int): 相対モード用ランダムウォームアップ回数
        study_name (str): Optuna study の名前
        sampler: Optuna sampler (default: optunahub AutoSampler)

    Returns:
        optuna.study.Study: 最適化後の study オブジェクト
    """
    if param_defs is None:
        param_defs = DEFAULT_PARAM_DEFS

    if sampler is None:
        auto_module = optunahub.load_module(package="samplers/auto_sampler")
        sampler = auto_module.AutoSampler()

    print(f"=== Optuna Runner ===")
    print(f"  Program:    {program_path}")
    print(f"  Mode:       {mode}")
    print(f"  Params:     {list(param_defs.keys())}")
    print(f"  Cases:      {num_cases} (seed {start_seed}~{start_seed+num_cases-1})")
    print(f"  Trials:     {n_trials}")
    print(f"  Score max:  {score_max}")
    print(f"  Interactive:{interactive}")
    if mode == "relative":
        print(f"  Warmup:     {n_random_warmup}")
    print()

    # 1. pahcer 初期設定
    setup_pahcer(program_path, num_cases, start_seed, interactive, score_max)

    warmup_results = []

    # 3. Study のロードまたは作成
    study = load_study()
    if study is not None:
        existing_trials = len(study.trials)
        print(f"\nResuming study from {STUDY_PKL_PATH} ({existing_trials} existing trials)")
    else:
        # 2. 相対モード: ランダムウォームアップ studyがまだない時に限る
        if mode == "relative" and n_random_warmup > 0:
            warmup_results = run_random_warmup(
                program_path, param_defs, num_cases, start_seed,
                interactive, score_max, n_random_warmup
            )
    
        if mode == "absolute":
            direction = "maximize" if score_max else "minimize"
        else:
            direction = "maximize"  # 相対スコアは常に最大化

        study = optuna.create_study(
            direction=direction,
            study_name=study_name,
            pruner=optuna.pruners.WilcoxonPruner(),
            sampler=sampler,
        )
        print(f"\nCreated new study (direction={study.direction.name})")

    # 4. ウォームアップ結果を study に注入
    if warmup_results:
        inject_warmup_to_study(study, warmup_results, param_defs, score_max)
        save_study(study)

    # 5. Optuna 最適化ループ
    first_trial_number = len(study.trials)

    if mode == "absolute":
        objective = AbsoluteObjective(param_defs, first_trial_number=first_trial_number)
    else:
        best_scores = load_best_scores()
        if not best_scores:
            print("WARNING: best_scores.json が空です。ウォームアップなしでは相対スコアが計算できません。")
        objective = RelativeObjective(
            param_defs, best_scores, score_max,
            first_trial_number=first_trial_number
        )

    print(f"\n=== Starting Optuna optimization ({n_trials} trials) ===\n")

    # trial ごとに study を保存するコールバック
    def save_callback(study, trial):
        save_study(study)

    study.optimize(objective, n_trials=n_trials, callbacks=[save_callback])

    # 6. 最終結果の表示
    print(f"\n=== Optimization Complete ===")
    print(f"  Best params: {study.best_params}")
    print(f"  Best value:  {study.best_value:.4f}")
    print(f"  Total trials: {len(study.trials)}")

    save_study(study)
    print(f"  Study saved to {STUDY_PKL_PATH}")

    return study


# ============================================================
# CLI
# ============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Optuna連携ハイパーパラメータ最適化")
    parser.add_argument("program", help="実行コードファイル (例: code01.cpp)")
    parser.add_argument("--mode", default="absolute", choices=["absolute", "relative"],
                        help="最適化モード (default: absolute)")
    parser.add_argument("--n-trials", type=int, default=50, help="Optuna反復回数 (default: 50)")
    parser.add_argument("--num-cases", type=int, default=100, help="テストケース数 (default: 100)")
    parser.add_argument("--start-seed", type=int, default=0, help="開始シード (default: 0)")
    parser.add_argument("--interactive", action="store_true", help="インタラクティブ問題")
    parser.add_argument("--min", dest="score_max", action="store_false", help="スコア最小化問題")
    parser.add_argument("--n-random-warmup", type=int, default=0,
                        help="相対モード用ランダムウォームアップ回数 (default: 0)")
    parser.add_argument("--study-name", default="optuna-study", help="Study名 (default: optuna-study)")
    parser.add_argument("--sampler", default="auto", choices=["auto", "tpe", "cmaes"],
                        help="Optuna sampler (default: auto)")

    args = parser.parse_args()

    # sampler の選択
    if args.sampler == "tpe":
        sampler = optuna.samplers.TPESampler()
    elif args.sampler == "cmaes":
        sampler = optuna.samplers.CmaEsSampler()
    else:  # "auto"
        sampler = None  # run_optuna 内で AutoSampler を生成

    run_optuna(
        program_path=args.program,
        param_defs=DEFAULT_PARAM_DEFS,
        num_cases=args.num_cases,
        start_seed=args.start_seed,
        n_trials=args.n_trials,
        interactive=args.interactive,
        score_max=args.score_max,
        mode=args.mode,
        n_random_warmup=args.n_random_warmup,
        study_name=args.study_name,
        sampler=sampler,
    )
