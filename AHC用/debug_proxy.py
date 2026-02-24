"""
debug_proxy.py - インタラクティブI/Oデバッグプロキシ

testerとユーザープログラムの間に入り、双方向のstdin/stdout通信を
ファイルにログ出力しながら中継する。

使い方:
    python debug_proxy.py --log debug/0000.log --cmd "python code01.py"
    python debug_proxy.py --log debug/0000.log --cmd "./code01.exe"
"""

import subprocess
import sys
import threading
import argparse
import os


def relay_tester_to_user(tester_stdin, user_stdin, log_file, lock, in_only=False):
    """
    tester側(自プロセスのstdin)からの入力を読み取り、
    ユーザープログラムのstdinに転送しつつログに記録する。
    """
    try:
        for line in tester_stdin:
            with lock:
                if in_only:
                    log_file.write(line)
                else:
                    log_file.write(f"[IN ] {line}")
                if not line.endswith("\n"):
                    log_file.write("\n")
                log_file.flush()
            user_stdin.write(line)
            user_stdin.flush()
    except (BrokenPipeError, OSError):
        pass
    finally:
        try:
            user_stdin.close()
        except:
            pass


def relay_user_to_tester(user_stdout, tester_stdout, log_file, lock, in_only=False):
    """
    ユーザープログラムのstdoutを読み取り、
    tester側(自プロセスのstdout)に転送しつつログに記録する。
    """
    try:
        for line in user_stdout:
            if not in_only:
                with lock:
                    log_file.write(f"[OUT] {line}")
                    if not line.endswith("\n"):
                        log_file.write("\n")
                    log_file.flush()
            tester_stdout.write(line)
            tester_stdout.flush()
    except (BrokenPipeError, OSError):
        pass


def main():
    parser = argparse.ArgumentParser(description="Interactive I/O debug proxy")
    parser.add_argument("--log", required=True, help="Path to the log file")
    parser.add_argument("--cmd", required=True, help="Command to run the user program")
    parser.add_argument("--in-only", action="store_true", help="Log only IN lines without [IN ] prefix")
    args = parser.parse_args()

    # ログディレクトリを作成
    log_dir = os.path.dirname(args.log)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # ユーザープログラムを起動
    import shlex
    cmd_parts = shlex.split(args.cmd)

    proc = subprocess.Popen(
        cmd_parts,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,  # stderrはそのまま透過
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,  # line-buffered
    )

    lock = threading.Lock()

    with open(args.log, "w", encoding="utf-8") as log_file:
        if not args.in_only:
            log_file.write(f"# Debug log: {args.cmd}\n")
            log_file.flush()

        # tester→ユーザー のリレースレッド
        t_in = threading.Thread(
            target=relay_tester_to_user,
            args=(sys.stdin, proc.stdin, log_file, lock, args.in_only),
            daemon=True,
        )

        # ユーザー→tester のリレースレッド
        t_out = threading.Thread(
            target=relay_user_to_tester,
            args=(proc.stdout, sys.stdout, log_file, lock, args.in_only),
            daemon=True,
        )

        t_in.start()
        t_out.start()

        # ユーザープログラムの終了を待つ
        proc.wait()

        # 少し待ってスレッドの処理完了を待つ
        t_out.join(timeout=2)
        t_in.join(timeout=1)

    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
