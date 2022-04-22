import csv
import os

import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
import scipy.signal
import datetime


def makeDir(path):
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)


def fft(x_array, y_array, filename):
    # Number of sample points
    N = len(x_array)
    # sample spacing
    T = 1.0 / 1000

    # x = np.linspace(0.0, N * T, N)
    # y = 4 * np.sin(60.0 * 2.0 * np.pi * x) + 8 * np.sin(90.0 * 2.0 * np.pi * x)
    yf = scipy.fftpack.fft(y_array)
    xf = np.linspace(0.0, 1.0 // (2.0 * T), N // 2)
    fig, ax = plt.subplots()
    ax.plot(xf, 2.0 / N * np.abs(yf[:N // 2]))
    plt.savefig(filename)
    plt.close()
    return yf

def movingAvg(array):
    day_range = 7
    if len(array) <= day_range:
        print("[ERROR]while doing movingAvg: array is not long enough.")
        return
    result_array = array[:]
    temp_sum = 0
    for index in range(day_range, len(array)):
        for index1 in range((index - day_range), index):
            temp_sum += array[index1]
        result_array[index] = array[index] - (temp_sum / day_range)
        temp_sum = 0
    return result_array


print("[--Start--]")
user_dict = {}
temp_date = None
temp_username = None
date_start = None
date_end = None
file_input = open('UserDates.csv')
reader = csv.reader(file_input)
for line in reader:
    temp_username = line[0]
    temp_date = datetime.datetime.fromtimestamp(int(line[1])).date()
    # Mark start and end dates
    if date_start is None or date_end is None:
        date_start = temp_date
        date_end = temp_date
    else:
        if date_start > temp_date:
            date_start = temp_date
        if date_end < temp_date:
            date_end = temp_date
    # End of Mark start and end dates
    if not user_dict.__contains__(temp_username):
        user_dict[temp_username] = {temp_date: 1}
    elif not user_dict[temp_username].__contains__(temp_date):
        user_dict[temp_username][temp_date] = 1
    else:
        user_dict[temp_username][temp_date] += 1

file_output_all = open("all.txt", "w", encoding="utf-8")
file_output_trans = open("trans.txt", "w", encoding="utf-8")
makeDir("fft")
filename_fft = None
keys_most = []
keys_least = []
temp_count_most = None
temp_count_least = None
for user in user_dict:
    file_output_all.write("Username:" + user + "\n\n")
    # add 0 tweets data
    date_index = date_start
    while date_index <= date_end:
        if not user_dict[user].__contains__(date_index):
            user_dict[user][date_index] = 0
        date_index += datetime.timedelta(1)
    # End of add 0 tweets data
    # print all data & most and least data
    counts = []
    dates = []
    for record in sorted(user_dict[user]):
        file_output_all.write(str(record) + "  Count:" + str(user_dict[user][record]) + "\n")
        counts.append(user_dict[user][record])
        dates.append(record)
        if temp_count_most is None:
            keys_most.append(record)
            temp_count_most = user_dict[user][record]
        if temp_count_least is None:
            if user_dict[user][record] != 0:
                keys_least.append(record)
                temp_count_least = user_dict[user][record]
        else:
            if temp_count_most < user_dict[user][record]:
                keys_most.clear()
                keys_most.append(record)
                temp_count_most = user_dict[user][record]
            elif temp_count_most == user_dict[user][record]:
                if not keys_most.__contains__(record):
                    keys_most.append(record)
            if 0 < user_dict[user][record] < temp_count_least:
                keys_least.clear()
                keys_least.append(record)
                temp_count_least = user_dict[user][record]
            elif temp_count_least == user_dict[user][record]:
                if not keys_least.__contains__(record):
                    keys_least.append(record)
    file_output_all.write("\nMost: " + str(temp_count_most) + " tweets in days: ")
    for key in keys_most:
        file_output_all.write(str(key) + " ")
    file_output_all.write("\nLeast: " + str(temp_count_least) + " tweets in days: ")
    for key in keys_least:
        file_output_all.write(str(key) + " ")
    file_output_all.write("\n--------------------------\n")
    file_output_all.flush()
    keys_most = []
    keys_least = []
    temp_count_most = None
    temp_count_least = None

    trans_counts = movingAvg(counts)
    for ele in trans_counts:
        file_output_trans.write(str(ele))
        file_output_trans.write("\n")
    file_output_trans.flush()

    # peaks = scipy.signal.find_peaks(trans_counts, distance=20)
    # do fft and draw
    filename_fft = "%s.png" % user
    fft(dates, trans_counts, filename_fft)


file_output_all.close()
file_output_trans.close()
print("[--End--]")
