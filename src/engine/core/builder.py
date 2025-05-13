#?attr ENGINE

"""
Preprocessor for building and packaging server and client files.
"""

from engine.log import log_engine as log
from engine.log import LogType

from enum import Enum
import os
import shutil
import time



class BuildType(Enum):
    SERVER = 0
    CLIENT = 1
    ENGINE_CLIENT = 2
    ENGINE_SERVER = 3



class Builder:
    """ Simple python preprocessor for building and packaging server and client files. """

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

        self.__run_script = ("""
            @echo off
            python src/main.py
        """)


    @property
    def build_dir(self):
        """ str - Directory to put the build cache files in. """
        return self.__build_dir
    

    @build_dir.setter
    def build_dir(self, value):
        if isinstance(value, str):
            self.__build_dir = value
        else:
            raise TypeError("Build dir must be a string:", value)
        

    @property
    def package_dir(self):
        """ str - Directory to put the package files in. """
        return self.__package_dir
    

    @package_dir.setter
    def package_dir(self, value):
        if isinstance(value, str):
            self.__package_dir = value
        else:
            raise TypeError("Package dir must be a string:", value)
        

    @property
    def server_folders(self):
        """ list - List of folders to build server files from. """
        return self.__server_folders
    

    @server_folders.setter
    def server_folders(self, value):
        if isinstance(value, list):
            self.__server_folders = value
        else:
            raise TypeError("Server folders must be a list:", value)
        

    @property
    def client_folders(self):
        """ list - List of folders to build client files from. """
        return self.__client_folders
    

    @client_folders.setter
    def client_folders(self, value):
        if isinstance(value, list):
            self.__client_folders = value
        else:
            raise TypeError("Client folders must be a list:", value)


    def build(self, build_type):
        """
        Builds and packages the files.
        Args:
            build_type: Type of build to perform.
        """
        log(f"Building {build_type}...", LogType.INFO)
        build_start = time.time()

        if build_type == BuildType.SERVER or build_type == BuildType.ENGINE_SERVER:
            folders = self.server_folders
            build_folder_preffix = "/server"
        elif build_type == BuildType.CLIENT or build_type == BuildType.ENGINE_CLIENT:
            folders = self.client_folders
            build_folder_preffix = "/client"

        for folder in folders:
            for file in self.__get_all_files(folder):
                if file.endswith(".py"):
                    self.__parse_file(file, build_type)

        for file in self.__get_all_files(self.build_dir + build_folder_preffix + "/src_cache"):
            copy_dest = self.package_dir + build_folder_preffix + "/src/" + "/".join(file.split("\\")[1:])
            os.makedirs(os.path.dirname(copy_dest), exist_ok=True)
            shutil.copy(file, copy_dest)

        for folder in folders:
            for file in self.__get_all_files(folder):
                if not file.endswith(".py") and not file.endswith(".pyc"):
                    dest_dir = self.package_dir + build_folder_preffix + "/" + file
                    os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
                    shutil.copy(file, dest_dir)

        with open(self.package_dir + build_folder_preffix + "/run.bat", "w") as f:
            f.write(self.__run_script)

        log(f"{build_type} built in {time.time() - build_start:.3f} seconds.", LogType.INFO)


    def clear_build(self):
        """ Clears files from package and build directories. """
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        if os.path.exists(self.package_dir):
            shutil.rmtree(self.package_dir)


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

        defines = []
        if build_type == BuildType.SERVER:
            defines = ["SERVER"]
            file_name_preffix = "/server" 
        elif build_type == BuildType.CLIENT:
            defines = ["CLIENT"]
            file_name_preffix = "/client"
        elif build_type == BuildType.ENGINE_SERVER:
            defines = ["ENGINE", "SERVER"]
            file_name_preffix = "/server"
        elif build_type == BuildType.ENGINE_CLIENT:
            defines = ["ENGINE", "CLIENT"]
            file_name_preffix = "/client"

        if lines[0].startswith("#?attr"):
            attr = lines[0][7:].strip()
            if attr not in defines:
                return
            
        file_name = self.build_dir + file_name_preffix + "/src_cache/" + "/".join(file.split("\\")[1:])

        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        f = open(file_name, "w")

        should_skip = 0
        prev_def = []
        
        for line in lines:
            if line.strip().startswith("#?"):
                line = line.strip()
                if len(line) < 7:
                    log(f"Invalid preprocessor directive in file {f}: {line}", LogType.ERROR)
                    continue

                match line[2:].split()[0]:
                    case "ifdef":
                        prev_def.append(line[8:])
                        if prev_def[-1] not in defines:
                            should_skip += 1

                    case "ifndef":
                        prev_def.append(line[9:])
                        if prev_def[-1] in defines:
                            should_skip += 1

                    case "endif":
                        tmp = prev_def.pop()
                        if tmp not in defines:
                            should_skip -= 1

                    case "attr":
                        pass

                    case _:
                        log(f"Invalid preprocessor directive in file {f}: {line}", LogType.ERROR)

            else:
                if not should_skip:
                    stripped_line = line.strip()
                    if not stripped_line:
                        continue
                    f.write(line)

        f.close()




