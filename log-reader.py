import re
import gzip
import glob
import os
import time
import codecs
import operator

all_logs_path = '/home/braden/Documents/ArcaneSurvival/logs/*.log.gz'
sample_logs_path = './sample-logs/*.log.gz'

# this dict is for storing the number of players that joined each hour
popular_time = {'00': 0, '01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0,
                '11': 0, '12': 0, '13': 0, '14': 0, '15': 0, '16': 0, '17': 0, '18': 0, '19': 0, '20': 0, '21': 0,
                '22': 0, '23': 0}

# stores all players that have logged on
players = {}

chat_output_lines = []
start_time = time.time()

command_count = {}

chat_line_count = 0


def compress_utf8_file(fullpath, delete_original=True):
    """Compress a UTF-8 encoded file using GZIP compression named *.gz. If `delete_original` is `True` [default: True],
    the original file specified by `delete_original` is removed after compression."""
    with codecs.open(fullpath, 'r', 'utf-8') as fin:
        with gzip.open(fullpath + '.gz', 'wb') as fout:
            for line in fin:
                fout.write(line.encode('utf-8'))
    if delete_original:
        os.remove(fullpath)


def command_checker(line):
    """ This function checks a line that has a command in it and calculates how many times each command was run on the
    server. """
    command_checker.command_count = {}
    slashindex = line.rfind('/')
    if re.search('/.* .*$', line[slashindex:]):
        command = line[slashindex+1:slashindex + line[slashindex:].find(' ')].rstrip()
    else:
        command = line[slashindex+1:].rstrip()

    # Since all lines with the word "issued" are sent to this functions, the != 'INFO]:' is there to ignore the lines
    # that just say "teleport issued" as a server message.
    if command is not '' and command != 'INFO]:':
        command_count[command] = command_count.get(command, 0) + 1


def death_checker(line):
    """ This function checks a given line for certain player deaths and calculates the number of each death type that
    occurred."""
    if re.search('Zombie$', line):
        # I'm sure this is bad practice, as global vars are bad, I'll fix it later maybe
        death_checker.zombie_kills += 1
    elif re.search('Skeleton$', line):
        if 'Wither' not in line:
            death_checker.skel_kills += 1
    elif re.search('place$', line) or re.search('hard$', line):
        death_checker.fall_kills += 1
    elif re.search('in lava$', line):
        death_checker.lava_kills += 1

death_checker.zombie_kills = 0
death_checker.skel_kills = 0
death_checker.fall_kills = 0
death_checker.lava_kills = 0


def scan_file(lines, file):
    """This is the general line scanning function. It checks for the different types of lines and deals with the
    line accordingly."""

    for line in lines:

        file_name = os.path.basename(file)
        date_stamp = file_name[:-7]

        # Check for chat message
        if re.search(r'^.*/INFO\]:( \[.{1,20}\] | )<..*>.*$', line):
            time_stamp = line[:10]
            player_name = line[line.find('<') + 1: line.find('>')]
            message_content = line[line.find('>') + 2:]
            if player_name != 'Staff' and player_name != 'S':
                global chat_line_count
                chat_line_count += 1
                global chat_output_lines
                chat_line = date_stamp + ' ' + time_stamp + '\t' + player_name + ': ' + message_content + '\n'
                global players
                if player_name not in players.keys():
                    players[player_name] = {'chat_count': 0, 'deaths': 0}
                players[player_name]['chat_count'] += 1
                chat_output_lines.append(chat_line)

        # regex to look for lines where player joins server
        elif re.search(r'^.*Authenticator #\d{1,10}/INFO\]: UUID of player.*$', line):

            time_stamp = line[:10]
            global players
            # probably a better way to do this, but it scans through the line to find the location of the player name
            player = line[line.find('UUID') + 15:line.find(' is ')]
            if player not in players.keys():  # if player isn't already in list
                    hour_joined = time_stamp[1:3]
                    popular_time[hour_joined] += 1

                    players[player] = {'chat_count': 0, 'deaths': 0}

        # check if it's a command
        elif re.search('issued', line):
            command_checker(line)

        # If it isn't a chat message, check for player deaths:
        elif '<' not in line:
            first_word = line[33:].split(' ', 1)[0]

            # There is currently an error here, this is for testing all the lines that begin with a player's name
            if first_word in players.keys():
                print(line)
                second_word = line[33:].split(' ', 2)[1]
                print(first_word, '    ', second_word)
                death_checker(line)


def read_files(path):
    """This function reads in the logfiles from the specified path"""
    files = sorted(glob.glob(path))
    for file in files:
        file_size = os.path.getsize(file)
        # For storing each line in a file in a list
        lines = []
        if file_size < 500000:  # TODO change this to be less lazy, purpose is to ignore the huge files full of errors
            with gzip.open(file, 'rt', encoding='utf-8') as log_file:
                lines = list(log_file)

        scan_file(lines, file)


def write_to_file(output_lines, filename):
    """This function writes a list of lines to a file"""
    output_file = open(filename, 'a', encoding='utf-8')
    for line in output_lines:
        output_file.write(line)
    output_file.close()


def sort_dict(dictionary):
    """This function converts a dictionary to a list of tuples sorted by the dictionary's values from greatest to
    least."""
    return sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)


def print_top_10(list_of_tuples, spacing):
    """This function prints the first 10 values in a list of tuples"""
    count = 1
    for item in list_of_tuples[:10]:
        print(str(count).ljust(3), item[0].ljust(spacing), item[1])
        count += 1

read_files(sample_logs_path)


# Uncomment these to write chat messages to a .txt.gz file
# write_to_file(chat_output_lines, 'chat-history.txt')
# compress_utf8_file('./chat-history.txt')

sorted_join_times = sort_dict(popular_time)
#sorted_players_by_chat_messages = sort_dict(players[:]['chat_count'])
sorted_commands = sort_dict(command_count)

# This is used for seeing how long the script took to run
end_time = time.time()

# Displaying all the gathered information:

print('\nMost popular join hours:\n')
for join_time in sorted_join_times:
    print(join_time[0], '  ', join_time[1])

print('\nMost chat messages:\n')
#print_top_10(sorted_players_by_chat_messages, 20)

print('\nMost common commands:\n')
print_top_10(sorted_commands, 20)

print('\nZombie Kill Count: ', death_checker.zombie_kills)
print('Skeleton Kill Count: ', death_checker.skel_kills)
print('Fall Kill Count: ', death_checker.fall_kills)
print('Lava Kill Count: ', death_checker.lava_kills)
print('Total chat line count: ', chat_line_count)
print('Players: ', len(players), '\nTotal time: ', '%.4f' % (end_time-start_time))
