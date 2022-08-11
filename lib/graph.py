from matplotlib import pyplot as plt


class GRAPH_FIO:
    def __init__(self, title_name:str) -> None:
        self.x_runtime = list()
        self.y_bw = list()
        self.y_iops = list()
        self.bw_figure, self.bw = plt.subplots()
        self.iops_figure, self.iops = plt.subplots()
        # plt.suptitle(title_name)

    def generate_chart(self):
        # plt.subplot(1,2,1)
        if len(self.x_runtime) == len(self.y_bw):
            self.bw.set_title("bw")
            self.bw.set_xlabel("runtime/msec")
            self.bw.set_ylabel("MB/S")
            self.bw.plot(self.x_runtime, self.y_bw, label="bw", color="#00FF00", marker=".", linestyle="-")

    def generate_chart_iops(self):    
        if len(self.x_runtime) == len(self.y_iops):
            # self.iops.subplot(1,2,2)
            self.iops.set_title("iops")
            self.iops.set_xlabel("runtime/msec")
            self.bw.set_ylabel("MB/S")
            self.iops.plot(self.x_runtime, self.y_iops, label="iops", color="#FF0000", marker=".", linestyle="-")


# if __name__ == "__main__":
#     import os
#     import csv
#     graph = GRAPH_FIO("fio_bw")
#     root_path = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
#     with open(os.path.join(root_path, "log", r"fio\fio_log_20220810154922\bw_bw.1.log.172.29.131.97")) as file:
#         reader = csv.reader(file, delimiter=',')
#         for row in reader:
#             graph.x_runtime.append(int(row[0])/1000)
#             graph.y_bw.append(float(row[1])/1024)
#     with open(os.path.join(root_path, "log", r"fio\fio_log_20220810154922\iops_iops.1.log.172.29.131.97")) as file:
#         reader = csv.reader(file, delimiter=',')
#         for row in reader:
#             # graph.x_runtime.append(int(row[0])/1000)
#             graph.y_iops.append(float(row[1])/1024)
    
#     graph.generate_chart()
#     plt.show()
