


class Console:
    def __init__(self):
        self.running = True
        self.cmd_output = []


    @property
    def running(self):
        return self.__running
    

    @running.setter
    def running(self, value):
        if isinstance(value, bool):
            self.__running = value
        else:
            raise Exception("Running must be a boolean:", value)
        

    @property
    def cmd_output(self):
        return self.__cmd_output
    

    @cmd_output.setter
    def cmd_output(self, value):
        if isinstance(value, list) and len(value) == 0:
            self.__cmd_output = value
        else:
            raise Exception("Command output must be a list:", value)


    def run(self):
        while self.running:
            self.__read_cmd()


    def __read_cmd(self):
        cmd = input("> ")

        if cmd:
            self.__handle_cmd(cmd)


    def __handle_cmd(self, cmd):
        cmd_args = cmd.split(" ")

        py_cmd = ""
        match cmd_args[0]:
            case "py":
                py_cmd = cmd[3:]

            case "exit":
                self.running = False

            case _:
                print("Unknown command")

        if py_cmd:
            self.cmd_output.append(py_cmd)


