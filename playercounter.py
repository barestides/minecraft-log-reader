import re
import gzip
import glob
import os
import time

logsPath = '/home/braden/Documents/ArcaneSurvival/logs/*.log.gz'
files = sorted(glob.glob(logsPath))

# this dict is for storing the number of players that joined each hour
popular_time = {'00': 0, '01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0,
                '11': 0, '12': 0, '13': 0, '14': 0, '15': 0, '16': 0, '17': 0, '18': 0, '19': 0, '20': 0, '21': 0,
                '22': 0, '23': 0}

# stores all players that have logged on
players = []

start_time = time.time()

# For storing each line in a file in a list
lines = []

count = 0

for file in files:

    file_size = os.path.getsize(file)
    if file_size < 500000:  # TODO change this to be less lazy, purpose is to ignore the huge files full of errors
        with gzip.open(file, 'rt', encoding='utf-8') as log_file:
            lines = list(log_file)
            count += len(lines)

    for line in lines:

        # regex to look for lines where player joins server
        if re.search(r'^\[\d\d:\d\d:\d\d\] \[User Authenticator #\d{1,10}/INFO\]: UUID of player.*$', line):
            # probably a better way to do this, but it scans through the line to find the location of the player name
            player = line[line.find('UUID of player') + 15:line.find(' is ')]
            if player not in players:  # if player isn't already in list
                    players.append(player)
                    file_name = os.path.basename(file)
                    date_joined = file_name[:-7]
                    time_joined = line[:10]
                    hour_joined = time_joined[1:3]
                    popular_time[hour_joined] += 1
                    print(player.ljust(20), date_joined, time_joined)
        # if re.search(r'^\[\d\d:\d\d:\d\d\] \[Server thread/INFO\]: <.*>.*$', line):
        #     player_name = line[line.find('INFO]: <') + 8 : line.find('>')]
        #     print(player_name)

end_time = time.time()
print('Lines: ', count)

