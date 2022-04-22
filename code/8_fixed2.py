import csv
import sys
import os
import math
import matplotlib.pylab as plt
import numpy as np
import os.path as pt
import scipy.fftpack
from statsmodels.tsa.arima.model import ARIMA


# 5     AIC change to min
# 6     Output the min pdqb.
#       Remove other details outputs
# 7     Retain b that's closed to integer.
#       Output changed to csv format.
#       When has more than 1 b, pick the one from the group that has max mi.
#       Draw Time-series of users which has (b*3) near 7.
#       Draw all Time-series
# 8     Specify b output format.

class NormGroup:
    def __init__(self, norm, maximum):
        self.norm = norm
        self.maximum = maximum

    def printInfo(self):
        print("[Norm:", self.norm, "; Max:", self.maximum)


def divideIntoGroups(array, size):
    groups = []
    index = 0
    while (index + size) <= len(array):
        groups.append(array[index: (index + size)])
        index = index + size
    return groups


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


def drawTimeSeries(x_array, y_array, filename):
    # Number of sample points
    N = len(x_array)
    # sample spacing
    T = 1.0 / 1000

    xf = np.linspace(0.0, 1.0 // (2.0 * T), N // 2)
    fig, ax = plt.subplots()
    ax.plot(xf, 2.0 / N * np.abs(y_array[:N // 2]))
    plt.savefig(filename)
    plt.close()
    return


print("[Program started]")

input_file_list = scan_csv(".")
if len(input_file_list) == 0:
    print("[Program Ended]No csv files found.")
    sys.exit(1)

raw_data = {}
file_input = open(input_file_list[0])
reader = csv.reader(file_input)
for line in reader:
    raw_data[line[0]] = []
    for i in range(1, len(line)):
        data = line[i].replace(".", "")
        raw_data[line[0]].append(int(data))

makeDir("Result")
# file_raw = open("raw.txt", "w", encoding="utf-8")
# file_mvag = open("mvag.txt", "w", encoding="utf-8")
# file_fft = open("fft.txt", "w", encoding="utf-8")
# file_cut = open("cut.txt", "w", encoding="utf-8")
# file_norm = open("norm.txt", "w", encoding="utf-8")
# file_mi = open("mi.txt", "w", encoding="utf-8")
# file_avg = open("avg.txt", "w", encoding="utf-8")
file_output = open("output.csv", "w", encoding="utf-8")
output_writer = csv.writer(file_output)

# write csv head
output_writer.writerow(["user", "p", "d", "q", "b", "AIC"])

b_gap = 0.1
size_group = 5
for user in raw_data:

    mvag = movingAvg(raw_data[user])
    ffted = scipy.fftpack.fft(mvag)
    cut = ffted[:math.floor(len(ffted) / 2)]
    norm = []
    for ele in cut:
        # Do norm
        norm.append(np.sqrt(np.square(np.real(ele)) + np.square(np.imag(ele))))

    """
    file_raw.write("\n\n\n")
    file_raw.write(user + "-----------------------------\n")
    for data in raw_data[user]:
        file_raw.write(str(data))
        file_raw.write("\n")
    file_mvag.write("\n\n\n")
    file_mvag.write(user + "-----------------------------\n")
    for data in mvag:
        file_mvag.write(str(data))
        file_mvag.write("\n")
    file_fft.write("\n\n\n")
    file_fft.write(user + "-----------------------------\n")
    for data in ffted:
        file_fft.write(str(data))
        file_fft.write("\n")
    file_cut.write("\n\n\n")
    file_cut.write(user + "-----------------------------\n")
    for data in cut:
        file_cut.write(str(data))
        file_cut.write("\n")
    """

    # Step 1
    groups_norm = divideIntoGroups(norm, size_group)
    groups = []
    summ = 0
    # file_mi.write("\n\n\n")
    # file_mi.write(user + "-----------------------------\n")
    # file_norm.write("\n\n\n")
    # file_norm.write(user + "-----------------------------\n")

    mi_group = []
    for group in groups_norm:
        maximum = max(group)
        mi_group.append(maximum)
        # file_mi.write(str(maximum))
        # file_mi.write("\n")

        # for data in group:
        #     file_norm.write(str(data))
        #     file_norm.write("\n")
        # file_norm.write("\n")

        summ = summ + maximum
        temp = NormGroup(group, maximum)
        groups.append(temp)
    avg = summ / len(groups_norm)
    std = np.std(mi_group)
    print(user, "'s STD:", std)
    # file_avg.write("\n\n\n")
    # file_avg.write(user + "-----------------------" + str(avg) + "\n")

    # Step 2
    j_group = []
    b_group = []
    b_not_near = None
    temp_max_mi_not_near = None
    temp_max_mi = None
    # index_group_target_b = "None"
    for i in range(0, len(groups)):
        if (groups[i].maximum - avg) > 2 * std:
            j = 5 * i + 3
            b = len(raw_data[user]) / j
            # if b is closed enough to integer, save the (j,b) pair.
            if (b + b_gap >= math.ceil(b) >= b) or (b - b_gap <= math.floor(b) <= b):
                j_group.append(j)
                # b from max mi group will always be the first ele of b_group
                if temp_max_mi is None or temp_max_mi < groups[i].maximum:
                    temp_max_mi = groups[i].maximum
                    b_group.insert(0, b)
                    # index_group_target_b = i
                else:
                    b_group.append(b)
            else:
                if temp_max_mi_not_near is None or temp_max_mi_not_near < groups[i].maximum:
                    temp_max_mi_not_near = groups[i].maximum
                    b_not_near = b
            # print("j:", j, "b:", b)

    # Time series of users who have b*3 near 7
    # target = 7
    # for b in b_group:
    #     multiplyBy2 = b * 2
    #     multiplyBy3 = b * 3
    #     if (multiplyBy2 + b_gap >= target >= multiplyBy2) or (multiplyBy3 + b_gap >= target >= multiplyBy3):
    #         print("[b qualified]b =", b)
    #         drawTimeSeries(norm, norm, "%s.png" % user)

    drawTimeSeries(norm, norm, "%s.png" % user)

    # Step 3
    target_b = None
    x_array = None
    p_group = None
    d_group = None
    q_group = None

    if len(b_group) == 0:
        # 0 b output
        p_group = [1, 2, 3]
        d_group = [0, 1]
        q_group = [1, 2, 3]
    else:
        p_group = [1, 2, 3]
        d_group = [0]
        q_group = [1, 2, 3]
        target_b = int(round(b_group[0]))
        if len(b_group) == 1:
            # only has 1 b
            # print("only has 1 b")
            x_array = []
            for i in range(target_b, len(norm)):
                x_array.append(norm[i] - norm[i - target_b])
            norm = x_array
        # else:
        # multiple b
        # print("multiple b")
        # target_b = b_group[len(b_group) - 1]
    # Step 4
    models = []
    aic_min = None
    target_p = None
    target_d = None
    target_q = None
    for p in p_group:
        for d in d_group:
            for q in q_group:
                model = ARIMA(norm, order=(p, d, q))
                models.append(model)
                result = model.fit()
                if aic_min is None or aic_min > result.aic:
                    aic_min = result.aic
                    target_p = p
                    target_d = d
                    target_q = q
                print("AIC:", result.aic)

    print(user, "'s ARIMA model count:", len(models))

    if target_b is None:
        str_b = str(b_not_near)
    else:
        str_b = str(target_b)

    # Step 5
    output_writer.writerow([user, str(target_p), str(target_d), str(target_q), str_b, str(aic_min)])

# file_raw.close()
# file_mvag.close()
# file_fft.close()
# file_cut.close()
# file_norm.close()
# file_mi.close()
# file_avg.close()
file_output.close()

print("[Program ended]")
