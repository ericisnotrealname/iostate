import paramiko
import json
import time
import subprocess
import psutil
from lib.log import logger


class REMOTE:
    def __init__(self, hostname:str, port:int, username:str, password:str, timeout:int):
        self.host = hostname
        self.port = port
        self.user = username
        self.password = password
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._ssh.connect(hostname=hostname, port=port, username=username, password=password, 
        timeout=timeout)
        self._cmd = "iostat -pmx nvme0n1 -o JSON -d 1 "
    
    def command(self, cmd, background=False):
        if background:
            self._ssh.exec_command(cmd, timeout=1)

        else:
            stdin, stdout, stderr = self._ssh.exec_command(cmd, timeout=1)
            return stdin, stdout, stderr
        return 0,0,0

    def sftp_put(self, filename, filepath):
        """
        SFTP put file to remote path
        :param filename:
        :param filepath:
        :return:
        """
        sftp = self._ssh.open_sftp()
        logger.info(f"pushing {filename} to {filepath}")
        sftp.put(filename, filepath)
        sftp.close()

    def close(self):
        self._ssh.close()

    def get_pid_by_ss(self, port:int):
        _, stdout, _ = self._ssh.exec_command(f"ss -ntlp | grep {port}")
        line = stdout.readline()
        try:
            pid = int(line.split()[5].split(",")[-2].split("=")[-1])
        except:
            pid = -1
        return pid

    def kill(self, pid):
        return self._ssh.exec_command(f"kill -9 {pid}")

    def get_pid_by_netstat(self, port:int):
        _, stdout, _ = self._ssh.exec_command(f"netstat -tunlp | grep {port}")
        line = stdout.readline()
        return int(line.split()[-1].split(r"/./")[0])

    def port_list(self):
        ports = list()
        _, stdout, _ = self._ssh.exec_command("ss -ntlp")
        lines = stdout.readlines()
        for line in lines:
            if line.startswith('LISTEN'):
                ports.append(int(line.split()[3].split(":")[-1]))
        return set(ports)
    #
    # def reboot(self):
    #     logger.info("reboot......")
    #     self._ssh.exec_command("reboot -nf")
    #     self._ssh.close()

    # def wait_for_reboot_complete(self, timeout=600):
    #     logger.info(f"waiting for reboot completed, timeout: {timeout}")
    #     start_time = time.time()
    #     result = False
    #     duration = 0
    #     while duration < timeout:
    #         logger.info(f"connecting to target, timeout: {duration}")
    #         try:
    #             self._ssh.connect(hostname=self.host, port=self.port, username=self.user, password=self.password, timeout=10)
    #         except:
    #             pass
    #         if self._ssh.get_transport().active:
    #             logger.info("reboot succeed")
    #             result = True
    #             break
    #         duration = time.time() - start_time
    #     return result

    def run_iostat(self, runtime):
        _, stdout, _ = self._ssh.exec_command(self._cmd + str(runtime))
        return json.loads(stdout.read().decode())
    # head = ['Device','r/s','w/s','rMB/s','wMB/s','rrqm/s','wrqm/s','%rrqm','%wrqm','r_await','w_await','aqu-sz','rareq-sz','wareq-sz','svctm','%util']

# value['sysstat']['hosts'][0]["statistics"]

class LOCALHOST:
    def __init__(self) -> None:
        self.cmd = "iostat -pmx nvme0n1 -o JSON -d 1 "
    
    def command(self):
        pass

    def run_iostate(self, runtime:int):
        proc = subprocess.Popen(self.cmd + str(runtime),
                                shell=True,
                                stdout=subprocess.PIPE,
                                close_fds=True)
        return json.loads(proc.stdout.read())
        # return json.loads(os.popen(self.cmd).read())