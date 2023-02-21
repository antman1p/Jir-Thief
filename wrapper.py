'''
Wrapper to run jir_thief.py using multiple threads
Splits huge dictionary into one word files
outputs to path with matched keyword on the folder name for ease of analysis 
'''
import os
import shutil
from datetime import datetime
import subprocess
from multiprocessing import Pool
from argparse import ArgumentParser


def run_stuff(keywords_lst):
    ''' Define Worker pool with keyword list '''
    worker_pool = Pool(4)
    worker_pool.map(run_scrapper, keywords_lst)


def run_scrapper(keyword_to_test):
    ''' Run jir_thief with the variables defined in argparser
        and the keyword file generated '''

    print(f'Testing {keyword_to_test}.')
    dict_file = f'dictionaries/{keyword_to_test}.txt'
    loot_path = args.loot_dir + '/' + keyword_to_test
    cmd = f'python3 jir_thief.py -j {args.cURL} -u {args.username} \
         -p {args.access_token} -d {dict_file} -o {loot_path}'
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL)
    process.wait()
    print(f'Tested {keyword_to_test}.')


if __name__ == '__main__':

    parser = ArgumentParser()
    optional = parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')

    required.add_argument('-d', '--dict', dest='dict_path',
                          help='path to dictionary', required=True)
    required.add_argument('-j', '--url',
                          dest='cURL',
                          help='target URL', required=True)
    required.add_argument('-u', '--user',
                          dest='username',
                          help='Account username', required=True)
    required.add_argument('-p', '--accesstoken',
                          dest='access_token',
                          help='Account access token', required=True)
    optional.add_argument(
        '-o',
        '--output-dir',
        dest='loot_dir',
        default='loot',
        help='loot output directory')
    parser._action_groups.append(optional)
    args = parser.parse_args()

    loot_dir = args.loot_dir
    dictionary_file = args.dict_path

    with open(dictionary_file, 'r', encoding='utf-8') as whole_dict_file:
        for line in whole_dict_file:

            search_term = line.strip()
            # path for the loot of specific keyword
            keyword_loot_dir = loot_dir + '/' + search_term

            # create temp keyword dictionaries
            keyword_dict_file = 'dictionaries/' + search_term + '.txt'
            with open(keyword_dict_file, 'w', encoding='utf-8') as temp_keyword_file:
                temp_keyword_file.write(line)

            # check if destination keyword loot dir exist
            if os.path.isdir(keyword_loot_dir):
                # check if destination keyword loot dir is empty
                if not os.listdir(keyword_loot_dir):
                    print(f'Directory {keyword_loot_dir} is empty')

                # if destination keyword loot dir is not empty, move it to
                # backup and empty it
                else:
                    print(f'Directory {keyword_loot_dir} is not empty')
                    print(f'Backing up {keyword_loot_dir} and deleting it')
                    running_date = datetime.utcnow().strftime('%Y-%m-%d-%H-%M')  # catch date

                    # backup path is keyword_loot_dir + _date
                    keyword_loot_dir_backup = keyword_loot_dir + '_' + running_date
                    # move loot to keyword_loot_dir_date/loot
                    shutil.move(keyword_loot_dir, keyword_loot_dir_backup)

                    print(f'{keyword_loot_dir_backup} created')
                    print(f'{keyword_loot_dir} deleted')
                    # recreate loot
                    os.mkdir(keyword_loot_dir)
                    print(f'{keyword_loot_dir} recreated')

            else:
                print(f'{keyword_loot_dir} doesn\'t exist. Creating it.')
                os.mkdir(keyword_loot_dir)
                print(f'{keyword_loot_dir} created.')

    with open(dictionary_file, 'r', encoding='utf-8') as whole_dict_file:
        keywords_list = whole_dict_file.read().splitlines()

    run_stuff(keywords_list)
