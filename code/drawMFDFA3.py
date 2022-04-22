import MFDFA
import csv
import os
import matplotlib.pylab as plt
import numpy as np


# 2     Show slopes.
# 3     Add differencing. Output to csv.


def makeDir(path):
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)


def function_diff(username, array, period):
    if period == -1:
        # Skip users with period -1
        return None

    if period >= len(array):
        print("[Error] when doing", str(username), "differencing: period", str(period), "longer than the length of data", str(len(array)))
        return None

    array_output = []
    for i in range(0, len(array) - period):
        x = array[i + period] - array[i]
        array_output.append(x)

    print(username, ": ", array_output, "\n\n")
    return array_output



print("[---Start---]")


file_TwitterData = open("TwitterData.csv", "r", encoding="utf-8")
file_Periods = open("Periods.csv", "r", encoding="utf-8")
file_Results = open("Results.csv", "w", encoding="utf-8")


# Read TwitterData from csv
raw_data = {}
reader = csv.reader(file_TwitterData)
for line in reader:
    raw_data[line[0]] = []
    for i in range(1, len(line)):
        data = line[i].replace(".", "")
        raw_data[line[0]].append(int(data))
file_TwitterData.close()


# Read Periods from csv
periods = {}
reader = csv.reader(file_Periods)
for line in reader:
    periods[line[0]] = []
    for i in range(1, len(line)):
        data = line[i].replace(".", "")
        periods[line[0]] = int(data)
file_Periods.close()


# MFDFA parameters
lag = np.unique(np.logspace(0.5, 3, 100).astype(int))
# the power q
q = 2
# the order of the polynomial fitting
order = 1



# Choose which user to be processed
need_all = True
need_userlist = ["TEN_GOP"]


# Do MFDFA

if need_all:
    need_userlist.clear()
    need_userlist.extend(raw_data)

resultset = {}
resultset_diff = {}

print("\n\n\nDiff result:\n\n\n")
for user in need_userlist:

    # Do MFDFA
    lag, dfa = MFDFA.MFDFA(np.array(raw_data[user]), lag=lag, q=q, order=order)
    resultset[user] = (lag, dfa)

    # Do differencing
    diffed_list = function_diff(str(user), raw_data[user], int(periods[user]))
    if diffed_list is None:
        # period -1 encountered
        resultset_diff[user] = None
        continue
    lag, dfa = MFDFA.MFDFA(np.array(diffed_list), lag=lag, q=q, order=order)
    resultset_diff[user] = (lag, dfa)

# print("\n\nResult:\n")

# Draw & output
# makeDir("MFDFA")

# write csv head
output_writer = csv.writer(file_Results)
output_writer.writerow(["user", "slope", "diff_slope"])

for user in need_userlist:

    # Do raw data
    # plt.loglog(resultset[user][0], resultset[user][1], "o", label="fOU: MFDFA q=2")
    # print(user, ":", var, "\n")
    # plt.savefig("%s.png" %user)
    var1 = np.polyfit(np.log(resultset[user][0][:15]), np.log(resultset[user][1][:15]), 1)[0][0]

    # Do diffed data
    # plt.loglog(resultset_diff[user][0], resultset_diff[user][1], "o", label="fOU: MFDFA q=2")
    # print(user, ":", var, "\n")
    # plt.savefig("%s.png" %user)
    if resultset_diff[user] is not None:
        var2 = np.polyfit(np.log(resultset_diff[user][0][:15]), np.log(resultset_diff[user][1][:15]), 1)[0][0]
    else:
        var2 = "None"

    output_writer.writerow([str(user), str(var1), str(var2)])
    # plt.close()

file_Results.close()
print("[---End---]")
