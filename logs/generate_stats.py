import sys

try:
    file = sys.argv[1]
    file = open(file, "r")
    raw = file.read().split("\n")
    file.close()
    raw.pop()
    turns = 0
    time = 0
    flag = 1
    experiments = len(raw)
    for sample in raw:
        if sample[0] != "C":
            flag = 0
            experiments -= 1
        else:
            turns += int(sample.split("Cleared Board in ")
                         [1].split(" turns")[0])
            time += float(sample.split("Realtime taken: ")[1].split(" s")[0])

    print "Average turn to clear the board: ", turns*1.0/experiments
    print "Total time taken: ", time
    print "Number of Experiments: ", experiments
    if flag == 0:
        print "Some of the experiments failed, these statistics may not be valid, please run the experiments again."

except Exception as e:
    print e
    print "usage: python generate_stats.py <logfile>"
