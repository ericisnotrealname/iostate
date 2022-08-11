import os
from lib.fio import FIO
from matplotlib import pyplot as plt



io = FIO()
jobs = {"GLOBAL":{
    "bs": "4k",
    "direct":"1",
    "thread":"32",
    "rw":"randwrite",
    "filename":"/dev/nvme0n1",
    "iodepth":"16",
    "runtime":"60",
    "numjobs":"1",
    "write_bw_log":"bw",
    "write_lat_log":"lat",
    "write_hist_log":"hist",
    "write_iops_log":"iops",
    "log_avg_msec":"1000"
}}


for i in jobs["GLOBAL"].keys():
    io.set_parm("GLOBAL", i, jobs["GLOBAL"][i])
jobfile = io.create_jobfile_from_parm("test", True)
current_log_path, file_tail = io.client("172.29.131.97", jobfile)

# current_log_path = r"C:\Users\linye\Documents\iostate\log\fio\fio_log_20220810154922"
# filename = "bw_bw.1.log.172.29.131.97"
filename = "bw_bw" + file_tail
io.generate_bw_graph(current_log_path, file_name=filename)
io.graph.bw_figure.savefig(os.path.join(current_log_path, filename+".png"))
