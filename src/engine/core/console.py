#?attr SERVER

"""
Console module for the engine.
"""

from engine.log import log_server as log
from engine.log import LogType



class Console:
    """ Simple terminal console for the server. """

    def __init__(self):
        self.__running = True
        self.__cmd_output = []

        self.__commands = {
            "help": "print('Commands:', ', '.join(self.console.commands.keys()))",
            "print": "print({args})",
            "raw": "{args}",
            "sim_speed": "self.levels['{arg1}'].simulation_speed = float({arg2})",
            "stop": "self.stop()\nself.console.stop()",
            "tp": "self.levels['{arg1}'].actors['{arg2}'].position = Vector({arg3}, {arg4})",

            #?ifdef ENGINE
            "build_clear": "self.builder.clear_build()",
            "build_client": "self.builder.clear_build(BuildType.CLIENT)\nself.builder.build_client()",
            "build_server": "self.builder.clear_build(BuildType.SERVER)\nself.builder.build_server()",
            #?endif
            
            "stat_tps": "print('tps:', self.get_stat('tps'))",
            "stat_console_cmds": "print('console_cmds:', self.get_stat('console_cmds'), 'ms')",
            "stat_level_updates": "print('level_updates:', self.get_stat('level_updates'), 'ms')",
            "stat_widget_tick": "print('widget_tick:', self.get_stat('widget_tick'), 'ms')",
            "stat_network": "print('network:', self.get_stat('network'), 'ms')",
            "stat_all": "for stat in ('tps', 'console_cmds', 'level_updates', 'network'):\n\tprint(stat + ': ' + self.get_stat(stat))",
        }

        log("Console initialized", LogType.INFO)


    @property
    def running(self):
        """ bool: Whether the console is running or not. """
        return self.__running
        

    @property
    def cmd_output(self):
        """ list[str]: The command execution buffer. """
        return self.__cmd_output
        

    @property
    def commands(self):
        """ dict[str, str]: The commands registered to the console. """
        return self.__commands
    

    def stop(self):
        """
        Called only by the engine.
        Stops the command loop.
        """
        self.__running = False
    

    def register_command(self, cmd, func):
        """
        Registers a command to the console.
        Args:
            cmd (str): The command name.
            func (str): The string, which will be parsed and executed by eval(). Example: "self.levels['{arg1}'].actors['{arg2}'].position = Vector({arg3}, {arg4})"
        Raises:
            TypeError: If the command name or function is not a string.
        """
        if isinstance(cmd, str) and isinstance(func, str):
            self.__commands[cmd] = func
        else:
            raise TypeError("Name and function must be strings:", cmd, func)


    def run(self):
        """
        Called only by the engine.
        Starts the command loop.
        This method is blocking and will not return until the console is stopped.

        """
        while self.running:
            self.__read_cmd()


    def __read_cmd(self):
        cmd = input()

        if cmd:
            self.handle_cmd(cmd)


    def handle_cmd(self, cmd: str):
        """
        Parses the command and adds it to the command execution queue.
        Args:
            cmd (str): The command to be executed.
        """
        cmd_args = cmd.split(" ")

        py_cmd = ""
        command_key = cmd_args[0]

        if command_key in self.commands:
            template = self.commands[command_key]
            context = {}
            if "{args}" in template:
                args = " ".join(cmd_args[1:])
                context["args"] = args
            else:
                for idx, arg in enumerate(cmd_args[1:], start=1):
                    context[f"arg{idx}"] = arg
            try:
                py_cmd = eval(f"f'''{template}'''", {}, context)
            except TypeError:
                print("Insufised param count")

        else:
            print("Command not found:", command_key)

        if py_cmd:
            self.cmd_output.append(py_cmd)


