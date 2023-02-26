from hashlib import sha256
import json
import os
import sys


def split_large_file(file, max_block_size):
    md = sha256()
    block_count = 0
    with open(file, 'rb') as fin:
        while (block := fin.read(max_block_size)) != b'':
            md.update(block)
            block_count += 1
            with open(f'{file}.part{block_count}', 'wb') as fout:
                fout.write(block)
    with open(f'{file}.info.json', 'w') as f:
        json.dump({
            'filename': os.path.basename(file),
            'sha256_hash': md.hexdigest(),
            'splitted_files': [f'{os.path.basename(file)}.part{i}' for i in range(1, block_count+1)]
        }, f)


def merge_splitted_files(info_file):
    md = sha256()
    with open(info_file, 'r') as f:
        info = json.load(f)
    with open(os.path.join(os.path.dirname(info_file), info['filename']), 'wb') as fout:
        for block_filename in info['splitted_files']:
            with open(os.path.join(os.path.dirname(info_file), block_filename), 'rb') as fin:
                block = fin.read()
                md.update(block)
                fout.write(block)
    if md.hexdigest() != info['sha256_hash']:
        print('Merge Error! Hash Mismatch!')
        os.remove(os.path.join(os.path.dirname(info_file), info['filename']))


if __name__ == '__main__':
    mode = sys.argv[1]
    file = sys.argv[2]
    if mode == '--split':
        split_large_file(file, int(sys.argv[3]))
        sys.exit()
    if mode == '--merge':
        merge_splitted_files(file)
        sys.exit()
    print('Mode Error! Split or Merge!')
