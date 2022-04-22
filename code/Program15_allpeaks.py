import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
import scipy.signal
import datetime

# Peaks.csv now outputs all peaks for every user



def makeDir(path):
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)


def drawFFT(x_array, y_array, filename):
    # Number of sample points
    N = len(x_array)
    # sample spacing
    T = 1.0 / 1000

    # x = np.linspace(0.0, N * T, N)
    # y = 4 * np.sin(60.0 * 2.0 * np.pi * x) + 8 * np.sin(90.0 * 2.0 * np.pi * x)
    # yf = scipy.fftpack.fft(y_array)
    xf = np.linspace(0.0, 1.0 // (2.0 * T), N // 2)
    fig, ax = plt.subplots()
    ax.plot(xf, 2.0 / N * np.abs(y_array[:N // 2]))
    plt.savefig(filename)
    plt.close()
    return


def drawHistogram(data, filename):
    plt.hist(data, bins=20, facecolor="blue", edgecolor="black", alpha=0.7)
    # plt.xlabel("区间")
    # plt.ylabel("频数/频率")
    # plt.title("频数/频率分布直方图")
    plt.savefig(filename)
    plt.close()
    return


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
file_output = open('Peaks.csv', 'w', encoding='utf-8')
reader = csv.reader(file_input)
writer = csv.writer(file_output)
# write head
# peaks_needed = 5
head = ["Username"]
# for i in range(0, peaks_needed):
#     head.append("height")
#     head.append("peak_val")
writer.writerow(head)

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
file_output_fft = open("fft.txt", "w", encoding="utf-8")
file_output_peaks = open("peaks.txt", "w", encoding="utf-8")
file_output_greatest_peaks = open("greatest_peaks.txt", "w", encoding="utf-8")
# makeDir("fft")
# makeDir("histogram")
filename_histogram = None
keys_most = []
keys_least = []
temp_count_most = None
temp_count_least = None
peaks_allusers = []

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
    file_output_trans.write("\n--------------------------\n")
    file_output_trans.write("username:" + user + "\n")
    for ele in trans_counts:
        file_output_trans.write(str(ele))
        file_output_trans.write("\n")
        file_output_trans.flush()
    # do fft
    yf = scipy.fftpack.fft(trans_counts)
    file_output_fft.write("\n--------------------------\n")
    file_output_fft.write("username:" + user + "\n")
    for ele in yf:
        file_output_fft.write(str(ele))
        file_output_fft.write("\n")
        file_output_fft.flush()

    # find peaks
    tuple_peaks, properties = scipy.signal.find_peaks(yf, distance=1, height=1)
    heights = properties['peak_heights']
    file_output_peaks.write("\n--------------------------\n")
    file_output_peaks.write("username:" + user + "\n")
    index_peaks_toBeDeleted = []
    for i in range(0, len(tuple_peaks)):
        # remove peaks greater than
        if tuple_peaks[i] > 550:
            index_peaks_toBeDeleted.append(i)
            continue
        file_output_peaks.write(str(tuple_peaks[i]) + ":" + str(heights[i]))
        file_output_peaks.write("\n")
        file_output_peaks.flush()

    index_peaks_toBeDeleted.reverse()
    for index in index_peaks_toBeDeleted:
        tuple_peaks = np.delete(tuple_peaks, index)
        heights = np.delete(heights, index)
        
    # find greatest 5 peaks
    temp = 0
    # peaks_needed
    for i in range(0, len(heights)):
        for j in range((i+1), len(heights)):
            if heights[j] > heights[i]:
                temp = heights[i]
                heights[i] = heights[j]
                heights[j] = temp
                temp = tuple_peaks[i]
                tuple_peaks[i] = tuple_peaks[j]
                tuple_peaks[j] = temp

    # write to csv
    content = [str(user)]
    # peaks_needed
    for i in range(0, len(heights)):
        content.append(tuple_peaks[i])
        content.append(heights[i])
        content.append("")
    writer.writerow(content)

    # calculate the threshold
    peaks_allusers.append({"user": user, "peak": tuple_peaks[0], "height": heights[0], "threshold": tuple_peaks[0] / 2})

    # histogram
    # hist, bin_edges = np.histogram(tuple_peaks, 500)
    # peaks_alluser.append(tuple_peaks)

# draw
# filename_histogram = "histogram.png"
# drawHistogram(peaks_alluser, filename_histogram)

# remove peaks greater than 
# for ele in peaks_allusers:
#     if ele["peak"] > 550:
#         print(ele["user"], "is deleted")
#         peaks_allusers.remove(ele)

# build clusters
clusters = [[peaks_allusers[0]]]
index_cluster = 0
temp_avg = 0.0
for index in range(1, len(peaks_allusers)):
    # file_output_greatest_peaks.write(str(user))
    # file_output_greatest_peaks.write(str(peaks_allusers[user]))
    # file_output_greatest_peaks.write("\n")
    flag = False
    for cluster in clusters:
        temp_sum = 0
        for peak in cluster:
            temp_sum += peak["peak"]
        temp_avg = temp_sum / len(cluster)
        # print("avg:", str(temp_avg))
        if abs(peaks_allusers[index]["peak"] - temp_avg) < 3:
            # print(str(peaks_allusers[index]["peak"]))
            cluster.append(peaks_allusers[index])
            flag = True
            break
    if not flag:
        clusters.append([peaks_allusers[index]])
    # if 0 <= abs(peaks_allusers[index]["peak"] - peaks_allusers[index-1]["peak"]) < 3:
    #     print("[", peaks_allusers[index]["user"], "&", peaks_allusers[index-1]["user"], "]", "distance less than 3")
    #     clusters[index_cluster].append(peaks_allusers[index])
    # else:
    #     print("[", peaks_allusers[index]["user"], "&", peaks_allusers[index-1]["user"], "]", "distance >= 3")
    #     index_cluster += 1
    #     clusters.append([peaks_allusers[index]])


# write clusters to csv

file_clusters = open('Clusters.csv', 'w', encoding='utf-8')
writer_clusters = csv.writer(file_clusters)
writer_clusters.writerow(["user", "peak", "height", "count"])
for index in range(0, len(clusters)):
    # print("\n---------------------------------\n")
    # print("cluster", index, ":")
    # print(clusters[index])
    str_index = "Cluster%d" %index
    writer_clusters.writerow([str_index])
    for user in clusters[index]:
        # calculate passing times for each user
        writer_clusters.writerow([user["user"], user["peak"], user["height"]])


file_input.close()
file_output.close()
file_output_all.close()
file_output_trans.close()
file_output_fft.close()
file_output_peaks.close()
file_output_greatest_peaks.close()
file_clusters.close()
print("[--End--]")
