import subprocess
import pipes

def execute_case(seed,TL=None,file="code1.py"):
    input_file_path = f'in/{seed:04}.txt'
    output_file_path = f'out/{seed:04}.txt'
    with open(input_file_path) as fin:
        with open(output_file_path, 'w') as fout:
            proc = subprocess.run(['python',file], stdin=fin, stdout=fout, stderr=subprocess.PIPE,timeout=TL)
            print(proc.stderr.decode('utf8').split('\n'))
            if "Err" in proc.stderr.decode('utf8'):
                raise
            pipefile = f'pipeline/pipefile_{seed:04}'
            with pipes.Template().open(pipefile, 'w') as p:
                subprocess.run(['cargo', "run", "--release","--bin", "vis", input_file_path, output_file_path], stdout=p, timeout=TL)
            output = open(pipefile).read()
            assert output
    return seed, output

def execute_case_interactive(seed,TL=None,file="code1.py"):
    input_file_path = f'in/{seed:04}.txt'
    output_file_path = f'out/{seed:04}.txt'
    proc = subprocess.run(f'cargo run --release --bin tester python {file} < {input_file_path} > {output_file_path}',stderr=subprocess.PIPE,shell=True,timeout=TL)
    print(proc.stderr.decode('utf8').split('\n'))
    if "Err" in proc.stderr.decode('utf8'):
        raise
    pipefile = f'pipeline/pipefile_{seed:04}'
    with pipes.Template().open(pipefile, 'w') as p:
        subprocess.run(['cargo', "run", "--release","--bin", "vis", input_file_path, output_file_path], stderr=p, timeout=TL)
    output = open(pipefile).read()
    assert output
    return seed, output