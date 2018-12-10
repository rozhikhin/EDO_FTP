import ftplib
import sys
import socket

class FtpDown(object):
    def __init__(self):
        self.i = 1
        self.params_dict = {}

    def show_help(self):
        print('\nПример использования:\n filin_ftp.exe host=aaa.ru port=21 user=vasya password=pass remote_dir=Orders local_dir=C:\Stoletov\Orders\\ encoding=windows-1251')
        print('\nПараметры port и remote_dir можно не указывать. По умолчанию:\n port = 21\n'
              ' remote_dir - корневой каnалог пользователя FTP\n'
              'encoding = latin-1')
        sys.exit()

    def get_params(self):
        for param in sys.argv:
            if param == __file__:
                continue
            if '.exe' in param:
                continue
            param = param.strip('-')
            key, value = param.split('=')
            self.params_dict[key] = value
        if not 'remote_dir' in self.params_dict:
            self.params_dict['remote_dir'] = ''
        if not 'port' in self.params_dict:
            self.params_dict['port'] = 21
        if not 'encoding' in self.params_dict:
            self.params_dict['encoding'] = 'latin-1'
        return self.params_dict

    def get_files(self):

        if self.i == 10:
            print('Все 10 попыток были безуспешны')
            return

        try:
            self.params_dict = self.get_params()
            host = self.params_dict['host']
            user = self.params_dict['user']
            password = self.params_dict['password']
            ftp_dir = self.params_dict['remote_dir']
            local_dir = self.params_dict['local_dir']
            port = int(self.params_dict['port'])
            encoding = self.params_dict['encoding']

            if local_dir[-1] != '\\':
                local_dir +=  '\\'
        except (KeyError, ValueError) as err:
            print(str(err))
            self.show_help()

        try:
            ftp = ftplib.FTP()
            ftp.encoding = encoding
            ftp.connect(host, port)
            ftp.login(user, password)
            ftp.cwd(ftp_dir)
            files = ftp.nlst()

            for filename in files:
                try:
                    print(filename)
                    with open(local_dir + filename, "wb") as file:
                        ftp.retrbinary("RETR " + filename, file.write)
                except ftplib.error_perm as err:
                        print(str(err))
                        if str(err) == "550 Access is denied.":
                            continue

        except ftplib.error_perm as resp:
            if str(resp) == "550 No files found.":
                print("Directory is empty.")
            print(str(resp))
        except socket.gaierror as err:
            print(str(err))
            print("Хост не существует")
        except TimeoutError as err:
            print(str(err))
            print("Предпринимаю очередную попытку!")
            self.i += 1
            print('Попытка номер ' + str(self.i))
            self.get_files()

        else:
            print('Все файлы скачаны')
            for filename in files:
                try:
                    ftp.delete(filename)
                except ftplib.error_perm as err:
                    print(str(err))
                    if str(err) == "550 Access is denied.":
                        continue
            ftp.quit()

inst = FtpDown()
if "help" in sys.argv:
    inst.show_help()
inst.get_files()


