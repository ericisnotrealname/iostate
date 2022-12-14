from lib import iostate, graph, log
import platform
import os
import time
import csv
import stat
import subprocess
import configparser


logger = log.logger

root_path = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))


FIO_PATH = os.path.join(root_path, "tools", "fio")
STATE_755 = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH


class FIO:
    def __init__(self) -> None:
        self.conf = configparser.ConfigParser()
        self.conf.read(os.path.join(root_path, "tools", "fio", "fio_file_name.ini"))
        system = platform.system()
        if not os.path.exists(FIO_PATH):
            raise RuntimeError("FIO is non-existent: '{}'".format(FIO_PATH))
        if system == "Linux":
            self.fio = os.path.join(FIO_PATH, self.conf["fio_name"]["LINUX_FILE"])
            if not os.access(self.fio, os.X_OK):
                os.chmod(self.fio, STATE_755)
        elif system == "Windows":
            self.fio = os.path.join(FIO_PATH, self.conf["fio_name"]["WINDOWS_FILE"])
        else:
            raise RuntimeError("Unknown OS: '{}'".format(system))
        self.__parm__ = dict()
        self.remote = None
        self.server_port = 8765
        self.jobfile_path = os.path.join(root_path, "tools", "fio", "jobfiles")
        self.log = logger
        self.graph = graph.GRAPH_FIO("fio")

    def generate_bw_graph(self, current_log_path:str, file_name:str):
        # graph = graph.GRAPH_FIO("fio_bw")
        log_file = os.path.join(current_log_path,file_name)
        with open(log_file) as log_csv:
            reader = csv.reader(log_csv, delimiter=',')
            for row in reader:
                self.graph.x_runtime.append(int(row[0])/1000)
                self.graph.y_bw.append(float(row[1])/1024)
        self.graph.generate_chart()
        self.graph.bw_figure.savefig(os.path.join(current_log_path, file_name+".png"))

    def add_section(self, section):
        if section not in self.__parm__.keys():
            self.__parm__[section] = {}

    def sections(self):
        return self.__parm__.keys()

    def keys(self, section):
        return self.__parm__[section].keys()

    def values(self, section):
        return self.__parm__[section].values()

    def items(self, section):
        return self.__parm__[section]

    def get_parm(self):
        return self.__parm__

    def set_parm(self, section, key, value=None):
        if section not in self.__parm__.keys():
            self.__parm__[section] = {}
        self.__parm__[section][key] = value

    def set_parms(self, section, parms):
        if section not in self.__parm__.keys():
            self.__parm__[section] = {}
        for key in parms.keys():
            self.__parm__[section][key] = parms[key]

    def clear_parm(self, section=None):
        if section is not None:
            self.__parm__[section].clear()
        else:
            self.__parm__.clear()

    def create_jobfile_from_parm(self, filename, save=False):
        if save:
            path = os.path.join(root_path, "tools", "fio", "jobfiles")
        else:
            path = os.path.join(root_path, "temp")
        conf = configparser.ConfigParser()
        sections = self.__parm__.keys()
        for i in sections:
            if self.__parm__[i] is not None:
                conf[i] = self.__parm__[i]
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        jobfile = os.path.join(path, filename+timestamp+".ini")
        file_job = open(jobfile, "w", encoding="utf-8")
        conf.write(file_job, space_around_delimiters=False)
        file_job.close()
        return jobfile
        

    def job_file_path(self, jobfile):
        if os.path.exists(jobfile):
            return jobfile
        elif os.path.exists(job_file := os.path.join(self.jobfile_path, jobfile)):
            return job_file
        raise "No such jobfile"

    def remote_server(self, hostname, ssh_port=22, server_port=8765, username="root", 
    password="nvme", timeout=3, system="Linux"):
        
        remote_path = os.path.join("/tmp/", self.conf["fio_name"]["LINUX_FILE"]) if system=="Linux" \
            else os.path.join("C:\\temp", self.conf["fio_name"]["WINDOWS_FILE"])
        
        self.remote = iostate.REMOTE(hostname=hostname, port=ssh_port, username=username, 
        password=password, timeout=timeout)
        self.log.info("connceted")
        ports = self.remote.port_list()
        if server_port in ports:
            self.log.warning(f"server_port:{server_port} has been used")
            self.log.warning("SKIP TO START REMOTE SERVER")
            return -1, -1, -1
        stdin, stdout, stderr = self.remote.command(f"{remote_path} -v")
        if stdout.channel.recv_exit_status() != 0:
            self.log.warn("sending file...")
            self.remote.sftp_put(os.path.join(FIO_PATH, self.conf["fio_name"]["LINUX_FILE"]), remote_path)
            self.remote.command("chmod 755 /tmp/fio-3.30")
        self.log.info("starting server...")
        stdin, stdout, stderr = self.remote.command(f"/tmp/fio-3.30 --server=0.0.0.0,{server_port}", background=True)
        return stdin, stdout, stderr

    def close_remote(self):
        try:
            pid = self.remote.get_pid_by_ss(self.server_port)
        except:
            pid = self.remote.get_pid_by_netstat(self.server_port)
        self.log.info(f"remote pid is: {pid}")
        self.log.info(f"kill remote server: {pid}")
        self.remote.kill(pid)
        self.remote.close()

    def fio_output(self, pipe):
        for line in iter(pipe.readline, b''):
            if line == "":
                break
            try:
                if line.split(":")[0].lower() == "jobs":
                    line_split = line.split("[")
                    logger.info("bw: %s; IOPS: %s; eta:%s", 
                    line_split[3].split(']')[0], line_split[4].split(']')[0], line_split[5].split(']')[0].split("eta")[1])
                else:
                    logger.info(line.split("\n")[0])
            except:
                logger.info(line.split("\n")[0])
            # logger.info("IOPS: %s", line.split("[")[4].split(']')[0])

    def client(self, hostname, jobfile, server_port=8765, **kwargs):
        self.server_port = server_port
        self.remote_server(hostname=hostname,server_port=self.server_port,**kwargs)
        self.log.info(f"start remote server {hostname}:{server_port}")
        log_path = os.path.join(root_path, "log", "fio")
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        current_log_path = os.path.join(log_path, f"fio_log_{timestamp}")
        os.makedirs(current_log_path)
        os.chdir(current_log_path)
        jobfile = self.job_file_path(jobfile)
        cmd = f"{self.fio} --client={hostname},{server_port} {jobfile}"
        self.log.info(f"**local command line**: {cmd}")
        # proc = subprocess.check_call(cmd,shell=True)
        process = subprocess.Popen(cmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with process.stdout:
            self.fio_output(process.stdout)
        exitcode = process.wait()
        if exitcode == 0:
            self.log.info("succeed")
        else:
            self.log.error("failed")
        # self.log.info(f"status: {proc}")
        os.chdir(root_path)

        file_tail = ".1.log." + hostname
        return current_log_path, file_tail

    