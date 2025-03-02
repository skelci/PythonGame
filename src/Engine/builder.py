#?attr ENGINE

from enum import IntEnum

import os
import shutil



class BuildType(IntEnum):
    SERVER = 0
    CLIENT = 1
    COMBINED = 2


class Builder:
    def __init__(self, build_dir, package_dir, server_folders, client_folders):
        self.build_dir = build_dir
        self.package_dir = package_dir
        self.server_folders = server_folders
        self.client_folders = client_folders


    @property
    def build_dir(self):
        return self.__build_dir
    

    @build_dir.setter
    def build_dir(self, value):
        if isinstance(value, str):
            self.__build_dir = value
        else:
            raise TypeError("Build dir must be a string:", value)
        

    @property
    def package_dir(self):
        return self.__package_dir
    

    @package_dir.setter
    def package_dir(self, value):
        if isinstance(value, str):
            self.__package_dir = value
        else:
            raise TypeError("Package dir must be a string:", value)
        

    @property
    def server_folders(self):
        return self.__server_folders
    

    @server_folders.setter
    def server_folders(self, value):
        if isinstance(value, list):
            self.__server_folders = value
        else:
            raise TypeError("Server folders must be a list:", value)
        

    @property
    def client_folders(self):
        return self.__client_folders
    

    @client_folders.setter
    def client_folders(self, value):
        if isinstance(value, list):
            self.__client_folders = value
        else:
            raise TypeError("Client folders must be a list:", value)


    def build_server(self):
        for folder in self.server_folders:
            for file in self.__get_all_files(folder):
                if file.endswith(".py"):
                    self.__parse_file(file, BuildType.SERVER)

        for file in self.__get_all_files(self.build_dir + "/server/src_cache"):
            copy_dest = self.package_dir + "/server/src/" + "/".join(file.split("\\")[1:])
            os.makedirs(os.path.dirname(copy_dest), exist_ok=True)
            shutil.copy(file, copy_dest)

        for folder in self.server_folders:
            for file in self.__get_all_files(folder):
                if not file.endswith(".py") and not file.endswith(".pyc"):
                    dest_dir = self.package_dir + "/server/" + file
                    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
                    shutil.copy(file, dest_dir)

        with open(self.package_dir + "/server/run.bat", "w") as f:
            f.write("python ./src/main.py")


    def build_client(self):
        for folder in self.client_folders:
            for file in self.__get_all_files(folder):
                if file.endswith(".py"):
                    self.__parse_file(file, BuildType.CLIENT)

        for file in self.__get_all_files(self.build_dir + "/client/src_cache"):
            copy_dest = self.package_dir + "/client/src/" + "/".join(file.split("\\")[1:])
            os.makedirs(os.path.dirname(copy_dest), exist_ok=True)
            shutil.copy(file, copy_dest)

        for folder in self.client_folders:
            for file in self.__get_all_files(folder):
                if not file.endswith(".py") and not file.endswith(".pyc"):
                    dest_dir = self.package_dir + "/client/" + file
                    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
                    shutil.copy(file, dest_dir)

        with open(self.package_dir + "/client/run.bat", "w") as f:
            f.write("python ./src/main.py")


    def clear_build(self, build_type = BuildType.COMBINED):
        dir_suffix = ("/server", "/client", "")[build_type]
        if os.path.exists(self.build_dir + dir_suffix):
            shutil.rmtree(self.build_dir + dir_suffix)
        if os.path.exists(self.package_dir + dir_suffix):
            shutil.rmtree(self.package_dir + dir_suffix)


    def __get_all_files(self, folder):
        files = []
        for root, _, filenames in os.walk(folder):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files
    

    def __parse_file(self, file, build_type):
        with open(file, "r") as f:
            lines = f.readlines()

        if len(lines) == 0:
            return

        if lines[0].startswith("#?attr"):
            if lines[0][7:] == "ENGINE":
                return
            if build_type == BuildType.CLIENT and lines[0][7:] == "SERVER":
                return
            if build_type == BuildType.SERVER and lines[0][7:] == "CLIENT":
                return

        file_name = self.build_dir + ("/server/" if build_type == BuildType.SERVER else "/client/") + "src_cache/" + "/".join(file.split("\\")[1:])

        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        f = open(file_name, "w")

        should_skip = False
        
        for line in lines:
            if line.strip().startswith("#?"):
                line = line.strip()
                if len(line) < 7:
                    print("Invalid line:", file, ":", line)
                    continue

                if build_type == BuildType.SERVER:
                    match line[2:7]:
                        case "ifdef":
                            if line[8:] == "CLIENT" or line[8:] == "ENGINE":
                                should_skip = True

                        case "endif":
                            should_skip = False
                        
                if build_type == BuildType.CLIENT:
                    match line[2:7]:
                        case "ifdef":
                            if line[8:] == "SERVER" or line[8:] == "ENGINE":
                                should_skip = True

                        case "endif":
                            should_skip = False

            else:
                if not should_skip:
                    f.write(line)

        f.close()




