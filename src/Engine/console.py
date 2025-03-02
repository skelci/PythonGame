#?attr SERVER



class Console:
    def __init__(self):
        self.__running = True
        self.__cmd_output = []

        self.__commands = {
            "help": "print('Commands:', ', '.join(self.console.commands.keys()))",
            "print": "print({arg1})",
            "raw": "{arg1}",
            "sim_speed": "self.simulation_speed = float({arg1})",
            "stop": "self.stop()\nself.console.stop()",
            "tp": "self.actors['{arg1}'].position = Vector({arg2}, {arg3})",

            "build_clear": "self.builder.clear_build()",
            "build_client": "self.builder.clear_build(BuildType.CLIENT)\nself.builder.build_client()",
            "build_server": "self.builder.clear_build(BuildType.SERVER)\nself.builder.build_server()",
            
            "stat_tps": "print('tps:', self.get_stat('tps'))",
            "stat_console_cmds": "print('console_cmds:', self.get_stat('console_cmds'), 'ms')",
            "stat_physics": "print('physics:', self.get_stat('physics'), 'ms')",
            "stat_widget_tick": "print('widget_tick:', self.get_stat('widget_tick'), 'ms')",
            "stat_all": "for stat in ('tps', 'console_cmds', 'physics', 'widget_tick'):\n\tprint(self.get_stat(stat))",
        }


    @property
    def running(self):
        return self.__running
        

    @property
    def cmd_output(self):
        return self.__cmd_output
        

    @property
    def commands(self):
        return self.__commands
    

    def stop(self):
        self.__running = False
    

    def register_command(self, name, func):
        if isinstance(name, str) and isinstance(func, str):
            self.__commands[name] = func
        else:
            raise TypeError("Name and function must be strings:", name, func)


    def run(self):
        while self.running:
            self.__read_cmd()


    def __read_cmd(self):
        cmd = input("> ")

        if cmd:
            self.handle_cmd(cmd)


    def handle_cmd(self, cmd):
        cmd_args = cmd.split(" ")

        py_cmd = ""
        command_key = cmd_args[0]

        if command_key in self.commands:
            template = self.commands[command_key]
            context = {}
            for idx, arg in enumerate(cmd_args[1:], start=1):
                context[f"arg{idx}"] = arg
            try:
                py_cmd = eval(f"f'''{template}'''", {}, context) # idk how this shit works, just don't touch it
            except TypeError as e:
                print("Insufised param count")

        else:
            print("Command not found:", command_key)

        if py_cmd:
            self.cmd_output.append(py_cmd)


