import paramiko
from common.config_dispose import ConfigDispose


class ParamikoHandle(object):
    def __init__(self, host, port=22, username="root", password=None):
        self.pkey = ConfigDispose.get_default("id_rsa_path")
        self.key = paramiko.RSAKey.from_private_key_file(self.pkey)
        self.host = host
        self.port = port
        self.username = username
        self.pwd = password
        # 获取Transport实例
        self.__transport = paramiko.Transport(self.host, self.port)
        # 连接SSH服务端，使用password
        self.__transport.connect(
            username=self.username, password=self.pwd
        ) if self.pwd else self.__transport.connect(
            username=self.username, pkey=self.key
        )
        # 获取SFTP实例
        self.sftp = paramiko.SFTPClient.from_transport(self.__transport)

    # 关闭通道
    def close(self):
        self.sftp.close()
        self.__transport.close()

    # 上传文件到远程主机
    def file_upload(self, local_path, remote_path):
        self.sftp.put(local_path, remote_path)
        self.close()

    # 从远程主机下载文件到本地
    def file_download(self, local_path, remote_path):
        self.sftp.get(remote_path, local_path)
        self.close()

    # 在远程主机上创建目录
    def dir_create(self, target_path, mode=777):
        self.sftp.mkdir(target_path, mode)
        self.close()

    # 删除远程主机上的目录
    def dir_delete(self, target_path):
        self.sftp.rmdir(target_path)
        self.close()

    # 查看目录下文件以及子目录
    def dir_list(self, target_path):
        self.close()
        return self.sftp.listdir(target_path)

    # 删除文件
    def file_delete(self, target_path):
        self.sftp.remove(target_path)
        self.close()

    # 查看目录下文件以及子目录的详细信息（包含内容和参考os.stat返回一个FSTPAttributes对象，对象的具体属性请用__dict__查看）
    def dir_lists(self, target_path):
        try:
            list = self.sftp.listdir_attr(target_path)
        except BaseException as e:
            pass
        self.close()
        return list

    # 获取文件详情
    def file_stat(self, remote_path):
        try:
            stat_info = self.sftp.stat(remote_path)
            self.close()
            return True, stat_info
        except:
            self.close()
            return False, "文件不存在"

    # SSHClient输入命令远程操作主机
    def cmd(self, command):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        ssh._transport = self.__transport
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read()
        # logger.info(result)
        self.close()
        return result.decode("utf-8")
