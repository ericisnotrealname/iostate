from lib.fio import FIO

io = FIO()
jobs = {"GLOBAL":{
    "bs": "4k",
    "direct":"1",
    "thread":"32",
    "rw":"randwrite",
    "filename":"/dev/nvme0n1",
    "iodepth":"16",
    "runtime":"20",
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
io.client("172.29.131.97", jobfile)

