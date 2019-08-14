from datetime import timedelta
from os import listdir
from regex import sub as rx_sub
from requests import get
from subprocess import check_output
from sys import stdout
from time import time

CC_RED = 91
CC_GREEN = 92
CC_YELLOW = 93
CC_LIGHTBLUE = 94
CC_PURPLE = 35
CC_CYAN = 36
COLOR_MAP_DICT = {'r': CC_RED, 'g': CC_GREEN, 'y': CC_YELLOW, \
                  'b': CC_LIGHTBLUE, 'p': CC_PURPLE, 'c': CC_CYAN}

# --- utils -------------------------------------------------------------------

def fclrprint(fstring, color_str='y'):
    ''' Print fstring with given color code. '''

    color = CC_YELLOW
    if color_str in COLOR_MAP_DICT:
        color = COLOR_MAP_DICT[color_str]
    colored_fstr = ('\033[%sm' % (color)) + fstring + '\033[0m' 
    print(colored_fstr)

def slugify(s):
    ''' Simplifies ugly strings into something URL-friendly.
    slugify("[Some] _ Article's Title--"): some-articles-title. '''

    s = s.lower()
    for c in [' ', '-', '.', '/']:
        s = s.replace(c, '_')
    s = rx_sub('\W', '', s)
    s = s.replace('_', ' ')
    s = rx_sub('\s+', ' ', s)
    s = s.strip()
    s = s.replace(' ', '-')
    return s

def get_num_of_files_in_dir(dir, fextension):
    ''' Get the number of files in a directory with given file extension. '''

    totalfiles = 0
    for xfname in listdir(dir):
        if xfname.endswith(fextension):
            totalfiles += 1
    return totalfiles

def get_num_of_lines_in_file(fname):
    ''' Get number of lines in file in cheapest way. '''

    num_of_lines_cmd = check_output(['wc', '-l', fname]).strip().decode("utf-8")
    num_of_lines = int(num_of_lines_cmd.split()[0])
    return num_of_lines

def bytes_to_human(size, decimal_places=2):
    ''' Returns a human readable file size from a number of bytes. '''

    for unit in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']:
        if size < 1024: break
        size /= 1024
    return f'{size:.{decimal_places}f}{unit}B'

def seconds_to_human(seconds):
    ''' Returns a human readable string from a number of seconds. '''

    return str(timedelta(seconds=int(seconds))).zfill(8)

def download_file(url, path=None, chunk_size=10**5):
    ''' Downloads a file keeping track of the progress. '''

    if path == None: path = url.split('/')[-1]
    r = get(url, stream=True)
    total_bytes = int(r.headers.get('content-length'))
    bytes_downloaded = 0
    start = time()
    print('Downloading %s (%s)' % (url, bytes_to_human(total_bytes)))
    with open(path, 'wb') as fp:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if not chunk: continue
            fp.write(chunk)
            bytes_downloaded += len(chunk)
            percent = bytes_downloaded / total_bytes
            bar = ('█' * int(percent * 32)).ljust(32)
            time_delta = time() - start
            eta = seconds_to_human((total_bytes - bytes_downloaded) * time_delta / bytes_downloaded)
            avg_speed = bytes_to_human(bytes_downloaded / time_delta).rjust(9)
            stdout.flush()
            stdout.write('\r  %6.02f%% |%s| %s/s eta %s' % (100 * percent, bar, avg_speed, eta))

def column_num2str(n):
    ''' convert spreadsheet column number to column letter. '''
    
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string