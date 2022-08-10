from matplotlib import pyplot as plt


class GRAPH_FIO:
    def __init__(self, title_name:str) -> None:
        self.x_runtime = list()
        self.y_bw = list()
        self.y_iops = list()
        plt.title(title_name)

    def generate_chart(self):
        plt.xlabel("runtime/msec")
        if len(self.x_runtime) == len(self.y_bw):
            plt.plot(self.x_runtime, self.y_bw, label="bw", color="#00FF00", marker=".", linestyle="-")
        if len(self.x_runtime) == len(self.y_iops):
            plt.plot(self.x_runtime, self.y_iops, label="iops", color="#00FF00", marker=".", linestyle="--")


