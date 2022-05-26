import pipes
from subprocess import Popen, PIPE, call


class SubprocessCMD:
    @staticmethod
    def subexec_cmd(cmd):
        pcmd = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = pcmd.communicate()
        ret_code = pcmd.poll()
        if ret_code != 0:
            return False, ""
        return True, stdout.decode("utf-8")

    @staticmethod
    def exists_remote(host, path):
        """Test if a file exists at path on a host accessible with SSH."""
        status = call(["ssh", host, "test -f {}".format(pipes.quote(path))])
        if status == 0:
            return True
        if status == 1:
            return False
        raise Exception("SSH failed")
