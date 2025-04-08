#?attr ENGINE

"""
Preprocessor for building and packaging server and client files.
"""

from enum import IntEnum

import os
import shutil
import time



class BuildType(IntEnum):
    SERVER = 0
    CLIENT = 1
    COMBINED = 2


class Builder:
    """
    Simple python preprocessor for building and packaging server and client files.
    """


    def __init__(self, build_dir, package_dir, server_folders, client_folders):
        """
        Args:
            build_dir (str): Directory to put the build cache files in.
            package_dir (str): Directory to put the package files in.
            server_folders (list): List of folders to build server files from.
            client_folders (list): List of folders to build client files from.
        """
        self.build_dir = build_dir
        self.package_dir = package_dir
        self.server_folders = server_folders
        self.client_folders = client_folders

        self.__run_script = (
            "@echo off\n"
            "python src/main.py\n"
            "pause\n"
        )        


    @property
    def build_dir(self):
        """
        str - Directory to put the build cache files in.
        """
        return self.__build_dir
    

    @build_dir.setter
    def build_dir(self, value):
        if isinstance(value, str):
            self.__build_dir = value
        else:
            raise TypeError("Build dir must be a string:", value)
        

    @property
    def package_dir(self):
        """
        str - Directory to put the package files in.
        """
        return self.__package_dir
    

    @package_dir.setter
    def package_dir(self, value):
        if isinstance(value, str):
            self.__package_dir = value
        else:
            raise TypeError("Package dir must be a string:", value)
        

    @property
    def server_folders(self):
        """
        list - List of folders to build server files from.
        """
        return self.__server_folders
    

    @server_folders.setter
    def server_folders(self, value):
        if isinstance(value, list):
            self.__server_folders = value
        else:
            raise TypeError("Server folders must be a list:", value)
        

    @property
    def client_folders(self):
        """
        list - List of folders to build client files from.
        """
        return self.__client_folders
    

    @client_folders.setter
    def client_folders(self, value):
        if isinstance(value, list):
            self.__client_folders = value
        else:
            raise TypeError("Client folders must be a list:", value)


    def build_server(self):
        """
        Builds and packages the server files.
        """
        print("Building server...")
        build_start = time.time()

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
            f.write(self.__run_script)

        print(f"Server built in {time.time() - build_start:.3f} seconds.")


    def build_client(self):
        """
        Builds and packages the client files.
        """
        print("Building client...")
        build_start = time.time()

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
            f.write(self.__run_script)

        print(f"Client built in {time.time() - build_start:.3f} seconds")


    def clear_build(self, build_type = BuildType.COMBINED):
        """
        Clears files from package and build directories.
        Args:
            build_type (BuildType): Type of build to clear.
        """
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
            attr = lines[0][7:].strip()
            if attr not in ("ENGINE", "SERVER", "CLIENT"):
                print("Invalid attribute:", file, ":", attr)
                return

            if attr == "ENGINE":
                return
            elif build_type == BuildType.CLIENT and attr == "SERVER":
                return
            elif build_type == BuildType.SERVER and attr == "CLIENT":
                return
            

        file_name = self.build_dir + ("/server/" if build_type == BuildType.SERVER else "/client/") + "src_cache/" + "/".join(file.split("\\")[1:])

        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        f = open(file_name, "w")

        should_skip = 0
        prev_def = []
        
        for line in lines:
            if line.strip().startswith("#?"):
                line = line.strip()
                if len(line) < 7:
                    print("Invalid line:", file, ":", line)
                    continue

                if build_type == BuildType.SERVER:
                    match line[2:7]:
                        case "ifdef":
                            prev_def.append(line[8:])
                            if prev_def[-1] == "CLIENT" or prev_def[-1] == "ENGINE":
                                should_skip += 1

                        case "endif":
                            if prev_def[-1] == "SERVER":
                                continue
                            should_skip -= 1
                            prev_def.pop()
                        
                if build_type == BuildType.CLIENT:
                    match line[2:7]:
                        case "ifdef":
                            prev_def.append(line[8:])
                            if prev_def[-1] == "SERVER" or prev_def[-1] == "ENGINE":
                                should_skip += 1

                        case "endif":
                            if prev_def[-1] == "CLIENT":
                                continue
                            should_skip -= 1
                            prev_def.pop()

            else:
                if not should_skip:
                    stripped_line = line.strip()
                    if not stripped_line or stripped_line.startswith("#"):
                        continue
                    f.write(line)

        f.close()




