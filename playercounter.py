import re
import gzip
import glob
import os
import time
import codecs


all_logs_path= '/home/braden/Documents/ArcaneSurvival/logs/*.log.gz'
sample_logs_path = './sample-logs/*.log.gz'
files = sorted(glob.glob(all_logs_path))

# this dict is for storing the number of players that joined each hour
popular_time = {'00': 0, '01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0,
                '11': 0, '12': 0, '13': 0, '14': 0, '15': 0, '16': 0, '17': 0, '18': 0, '19': 0, '20': 0, '21': 0,
                '22': 0, '23': 0}

# stores all players that have logged on
players = []

chat_output_lines = []

start_time = time.time()

zombie_kills = 0
skel_kills = 0
chat_line_count = 0

# For storing each line in a file in a list
lines = []


def compress_utf8_file(fullpath, delete_original = True):
    """Compress a UTF-8 encoded file using GZIP compression named *.gz. If `delete_original` is `True` [default: True],
    the original file specified by `delete_original` is removed after compression."""
    with codecs.open(fullpath, 'r', 'utf-8') as fin:
        with gzip.open(fullpath + '.gz', 'wb') as fout:
            for line in fin:
                fout.write(line.encode('utf-8'))
    if delete_original:
        os.remove(fullpath)


def scan_file(lines, file):

    for line in lines:

        file_name = os.path.basename(file)
        date_stamp = file_name[:-7]

        # regex to look for lines where player joins server
        if re.search(r'^\[\d\d:\d\d:\d\d\] \[User Authenticator #\d{1,10}/INFO\]: UUID of player.*$', line):

            time_stamp = line[:10]

            # probably a better way to do this, but it scans through the line to find the location of the player name
            player = line[line.find('UUID') + 15:line.find(' is ')]
            if player not in players:  # if player isn't already in list
                    players.append(player)
                    hour_joined = time_stamp[1:3]
                    popular_time[hour_joined] += 1
                    # print(player.ljust(20), date_joined, time_joined)

        # If it isn't a chat message:
        if '<' not in line:
            if re.search(' Zombie$', line):
                    # print(line)
                    # I'm sure this is bad practice, as global vars are bad, I'll fix it later maybe
                    global zombie_kills
                    zombie_kills += 1
            if re.search(' Skeleton$', line):
                if 'Wither' not in line:
                    # print(line)
                    global skel_kills
                    skel_kills += 1

        # For writing all chat messages to a file

        if re.search(r'^.*/INFO\]:( \[.{1,20}\] | )<..*>.*$', line):
            time_stamp = line[:10]
            player_name = line[line.find('<') + 1: line.find('>')]
            message_content = line[line.find('>') + 2:]
            if player_name != 'Staff' or player_name != 'S':
                print(player_name)
                global chat_line_count
                chat_line_count += 1
                global chat_output_lines
                chat_line = date_stamp +  ' ' + time_stamp + '\t' + player_name + ': ' + message_content + '\n'
                chat_output_lines.append(chat_line)
            else:
                print('It didn\'t work yo\n', line)

def read_files(files):

    for file in files:
        file_size = os.path.getsize(file)
        # For storing each line in a file in a list
        lines = []
        if file_size < 500000:  # TODO change this to be less lazy, purpose is to ignore the huge files full of errors
            with gzip.open(file, 'rt', encoding='utf-8') as log_file:
                lines = list(log_file)

        scan_file(lines,file)

def write_to_file(output_lines):
    output_file = open('chat-history.txt', 'a', encoding='utf-8')
    for chat_line in output_lines:
        output_file.write(chat_line)
    output_file.close()

read_files(files)

write_to_file(chat_output_lines)

compress_utf8_file('./chat-history.txt')

end_time = time.time()
print('Zombie Kill Count: ', zombie_kills)
print('Skeleton Kill Count: ', skel_kills)
print('Total chat line count: ', chat_line_count)
print('Players: ', len(players), '\nTotal time: ', '%.4f'%(end_time-start_time))
