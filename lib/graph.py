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
            self.bw.set_ylim(min(self.y_bw) - 20, max(self.y_bw)+ 20)
            self.bw.plot(self.x_runtime, self.y_bw, label="bw", color="#00FF00", marker=".", linestyle="-")

    def generate_chart_iops(self):    
        if len(self.x_runtime) == len(self.y_iops):
            # self.iops.subplot(1,2,2)
            self.iops.set_title("iops")
            self.iops.set_xlabel("runtime/msec")
            self.bw.set_ylabel("MB/S")
            self.iops.plot(self.x_runtime, self.y_iops, label="iops", color="#FF0000", marker=".", linestyle="-")

