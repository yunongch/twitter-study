import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.fftpack
import scipy.signal


def scan_csv(path):
    result = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(".csv"):
                result.append(f)
    return result


def makeDir(path):
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)


def drawTimeSeries(x_array, y_array, filename):
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
# temp_date = None
date_start = None
date_end = None
flag_first_line = True
file_input = None
filenames_input = []


# read single csv file
# file_input = open(filenames_input[0])
# reader = csv.reader(file_input)
# 
# for line in reader:
#     temp_username = line[0]
#     temp_date = datetime.datetime.fromtimestamp(int(line[1])).date()
#     # Mark start and end dates
#     if date_start is None or date_end is None:
#         date_start = temp_date
#         date_end = temp_date
#     else:
#         if date_start > temp_date:
#             date_start = temp_date
#         if date_end < temp_date:
#             date_end = temp_date
#     # End of Mark start and end dates
#     if not user_dict.__contains__(temp_username):
#         user_dict[temp_username] = {temp_date: 1}
#     elif not user_dict[temp_username].__contains__(temp_date):
#         user_dict[temp_username][temp_date] = 1
#     else:
#         user_dict[temp_username][temp_date] += 1


# read > 1 files
flag_first_line = True
os.chdir("frequencyTables")
all_dates = []
filenames_input = scan_csv(".")
for filename in filenames_input:
    # if filename.startswith("frequency_"):
    #     index_end = filename.index(".csv")
    #     country_name = filename[10:index_end]
    flag_first_line = True
    file_input = open(filename)
    reader = csv.reader(file_input)
    duplicate_usernames = {}
    for line in reader:
        if flag_first_line:
            if len(all_dates) == 0:
                for date in line:
                    all_dates.append(date)
            flag_first_line = False
            continue
        # temp_username = "%s-%s" % (line[0], country_name)
        temp_username = line[0]
        if user_dict.__contains__(temp_username):
            if duplicate_usernames.__contains__(temp_username):
                duplicate_usernames[temp_username] += 1
                temp_username = "%s-%d" % (temp_username, duplicate_usernames[temp_username])
            else:
                duplicate_usernames[temp_username] = 1
                temp_username = "%s-1" % temp_username
        for index in range(1, len(line)):
            if not user_dict.__contains__(temp_username):
                user_dict[temp_username] = {all_dates[index]: int(line[index])}
            else:
                user_dict[temp_username][all_dates[index]] = int(line[index])
    file_input.close()



# file_test = open('test.txt', 'w', encoding='utf-8')
# for user in user_dict:
#     file_test.write("\n-------------------------------")
#     file_test.write("username:%s\n" % user)
#     for data in user_dict[user]:
#         file_test.write("%s - %s\n" % (data, user_dict[user][data]))
#     file_test.flush()
# file_test.close()

os.chdir("../")
makeDir("Results")
# file_output_all = open("all.txt", "w", encoding="utf-8")
# file_output_trans = open("trans.txt", "w", encoding="utf-8")
# file_output_fft = open("fft.txt", "w", encoding="utf-8")
# file_output_peaks = open("peaks.txt", "w", encoding="utf-8")
# file_output_greatest_peaks = open("greatest_peaks.txt", "w", encoding="utf-8")
# file_output_norms = open("norms.txt", "w", encoding="utf-8")
file_clusters = open('Clusters.csv', 'w', encoding='utf-8')
file_output = open('Peaks.csv', 'w', encoding='utf-8')
writer = csv.writer(file_output)
# write Peaks.csv 's head
peaks_needed = 5
head = ["userid"]
for i in range(0, peaks_needed):
    head.append("peak_position")
    head.append("height")
    head.append("")
writer.writerow(head)
makeDir("norm")
# makeDir("histogram")
filename_histogram = None
keys_most = []
keys_least = []
temp_count_most = None
temp_count_least = None
peaks_allusers = []

for user in user_dict:
    # file_output_all.write("Username:" + user + "\n\n")
    # add 0 tweets data
    # date_index = date_start
    # while date_index <= date_end:
    #     if not user_dict[user].__contains__(date_index):
    #         user_dict[user][date_index] = 0
    #     date_index += datetime.timedelta(1)
    # End of add 0 tweets data
    # print all data & most and least data
    counts = []
    dates = []
    for record in user_dict[user]:
        # file_output_all.write(str(record) + "  Count:" + str(user_dict[user][record]) + "\n")
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
    # file_output_all.write("\nMost: " + str(temp_count_most) + " tweets in days: ")
    # for key in keys_most:
    #     file_output_all.write(str(key) + " ")
    # file_output_all.write("\nLeast: " + str(temp_count_least) + " tweets in days: ")
    # for key in keys_least:
    #     file_output_all.write(str(key) + " ")
    # file_output_all.write("\n--------------------------\n")
    # file_output_all.flush()
    keys_most = []
    keys_least = []
    temp_count_most = None
    temp_count_least = None

    trans_counts = movingAvg(counts)
    # file_output_trans.write("\n--------------------------\n")
    # file_output_trans.write("username:" + user + "\n")
    # for ele in trans_counts:
    #     file_output_trans.write(str(ele))
    #     file_output_trans.write("\n")
    #     file_output_trans.flush()
    # do fft
    yf = scipy.fftpack.fft(trans_counts)
    # file_output_fft.write("\n--------------------------\n")
    # file_output_fft.write("username:" + user + "\n")
    # file_output_norms.write("\n--------------------------\n")
    # file_output_norms.write("username:" + user + "\n")
    norms = []
    temp_norm = None
    for ele in yf:
        # file_output_fft.write(str(ele))
        # file_output_fft.write("\n")
        # file_output_fft.flush()
        # transfer yf to norm
        temp_norm = np.sqrt(np.square(np.real(ele)) + np.square(np.imag(ele)))
        norms.append(temp_norm)
        # file_output_norms.write(str(temp_norm))
        # file_output_norms.write("\n")
        # file_output_norms.flush()

    # draw norm time series
    # filename_norm = "%s.png" % user
    # drawTimeSeries(dates, norms, filename_norm)
    # find peaks
    tuple_peaks, properties = scipy.signal.find_peaks(norms, distance=1, height=1)
    heights = properties['peak_heights']
    # file_output_peaks.write("\n--------------------------\n")
    # file_output_peaks.write("username:" + user + "\n")
    index_peaks_toBeDeleted = []
    for i in range(0, len(tuple_peaks)):
        # remove peaks greater than
        if tuple_peaks[i] > 2130:
            index_peaks_toBeDeleted.append(i)
            continue
        # file_output_peaks.write(str(tuple_peaks[i]) + ":" + str(heights[i]))
        # file_output_peaks.write("\n")
        # file_output_peaks.flush()

    index_peaks_toBeDeleted.reverse()
    for index in index_peaks_toBeDeleted:
        tuple_peaks = np.delete(tuple_peaks, index)
        heights = np.delete(heights, index)
    
    # skip this loop when user has < 5 peaks
    if len(tuple_peaks) < 5:
        continue

    # find greatest 5 peaks
    temp = 0
    for i in range(0, peaks_needed):
        for j in range((i+1), len(heights)):
            if heights[j] > heights[i]:
                temp = heights[i]
                heights[i] = heights[j]
                heights[j] = temp
                temp = tuple_peaks[i]
                tuple_peaks[i] = tuple_peaks[j]
                tuple_peaks[j] = temp

    # N / peak
    peaks2 = []
    count_days = len(all_dates)
    for i in range(0, peaks_needed):
        peaks2.append(count_days / tuple_peaks[i])

    # write to csv
    content = [str(user)]
    for i in range(0, peaks_needed):
        content.append(tuple_peaks[i])
        content.append(heights[i])
        content.append("")
    writer.writerow(content)

    # calculate the threshold
    threshold = heights[0] / 2
    # count how many norms that match the threshold
    # match_count = 0
    positive = norms[0] - threshold > 0
    change_count = 0
    for norm in norms:
        if (norm - threshold) > 0:
            if not positive:
                positive = True
                change_count += 1
        else:
            if positive:
                positive = False
                change_count += 1
        # if norm == threshold:
        #     print("norm:", norm, "match", threshold)
        #     match_count += 1

    peaks_allusers.append({"user": user, "peak": tuple_peaks[0], "height": heights[0], "threshold": threshold, "change_count": change_count, "N/peak": tuple_peaks[0]})

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

writer_clusters = csv.writer(file_clusters)
writer_clusters.writerow(["user", "peak", "height", "0.5line", "change_count"])
for index in range(0, len(clusters)):
    # print("\n---------------------------------\n")
    # print("cluster", index, ":")
    # print(clusters[index])
    str_index = "Cluster%d" %index
    writer_clusters.writerow([str_index])
    for user in clusters[index]:
        # calculate passing times for each user
        writer_clusters.writerow([user["user"], user["peak"], user["height"], user["threshold"], user["change_count"]])

file_input.close()
file_output.close()
# file_output_all.close()
# file_output_trans.close()
# file_output_fft.close()
# file_output_peaks.close()
# file_output_greatest_peaks.close()
file_clusters.close()
# file_output_norms.close()
print("[--End--]")
