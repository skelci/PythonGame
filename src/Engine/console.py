


class Console:
    def __init__(self):
        self.running = True
        self.__cmd_output = []

        stat_widgets = ("fps", "events", "console_cmds", "physics", "render_regs", "bg_render", "render", "actor_render", "widget_render")
        self.__commands = {
            "exit": "self.running = False\nself.console.running = False",
            "help": "print('Commands:', ', '.join(self.console.commands.keys()))",
            "print": "print({arg1})",
            "raw": "{arg1}",
            "tp": "self.actors['{arg1}'].position = Vector({arg2}, {arg3})",
            
            "stat_fps": "self.widgets['fps'].visible = not self.widgets['fps'].visible",
            "stat_events": "self.widgets['events'].visible = not self.widgets['events'].visible",
            "stat_console_cmds": "self.widgets['console_cmds'].visible = not self.widgets['console_cmds'].visible",
            "stat_physics": "self.widgets['physics'].visible = not self.widgets['physics'].visible",
            "stat_render_regs": "self.widgets['render_regs'].visible = not self.widgets['render_regs'].visible",
            "stat_bg_render": "self.widgets['bg_render'].visible = not self.widgets['bg_render'].visible",
            "stat_render": "self.widgets['render'].visible = not self.widgets['render'].visible",
            "stat_actor_render": "self.widgets['actor_render'].visible = not self.widgets['actor_render'].visible",
            "stat_widget_render": "self.widgets['widget_render'].visible = not self.widgets['widget_render'].visible",
            "stat_all": f"for widget in self.widgets:\n\tif widget in {stat_widgets}:\n\t\tself.widgets[widget].visible = True",
            "stat_none": f"for widget in self.widgets:\n\tif widget in {stat_widgets}:\n\t\tself.widgets[widget].visible = False",
        }


    @property
    def running(self):
        return self.__running
    

    @running.setter
    def running(self, value):
        if isinstance(value, bool):
            self.__running = value
        else:
            raise TypeError("Running must be a boolean:", value)
        

    @property
    def cmd_output(self):
        return self.__cmd_output
        

    @property
    def commands(self):
        return self.__commands
    

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


