


class Console:
    def __init__(self):
        self.running = True
        self.cmd_output = []

        self.__commands = {
            "exit": "self.running = False\nself.console.running = False",
            "help": "print('Commands:', ', '.join(self.console.commands.keys()))",
            "print": "print({arg1})",
            "raw": "{arg1}",
            "tp": "self.actors['{arg1}'].position = Vector({arg2}, {arg3})",
            
            "sh_fps": "self.widgets['fps'].visible = not self.widgets['fps'].visible",
        }


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
        

    @property
    def commands(self):
        return self.__commands
    

    def register_command(self, name, func):
        if isinstance(name, str) and isinstance(func, str):
            self.__commands[name] = func
        else:
            raise Exception("Name and function must be strings:", name, func)


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
        command_key = cmd_args[0]

        if command_key in self.commands:
            template = self.commands[command_key]
            context = {}
            for idx, arg in enumerate(cmd_args[1:], start=1):
                context[f"arg{idx}"] = arg
            py_cmd = eval(f"f'''{template}'''", {}, context) # idk how this shit works, just don't touch it

        else:
            print("Command not found:", command_key)

        if py_cmd:
            self.cmd_output.append(py_cmd)


