


class Console:
    def __init__(self):
        self.running = True


    @property
    def running(self):
        return self.__running
    

    @running.setter
    def running(self, value):
        if isinstance(value, bool):
            self.__running = value
        else:
            raise Exception("Running must be a boolean:", value)


    def run(self):
        while self.running:
            self.__read_cmd()


    def log(self, msg):
        print()
        print(msg)
        print("> ", end="")


    def __read_cmd(self):
        cmd = input("> ")

        if cmd:
            self.__handle_cmd(cmd)


    def __handle_cmd(self, cmd):
        cmd_args = cmd.split(" ")

        match cmd_args[0]:
            case "py":
                try:
                    exec(cmd[3:])
                except Exception as e:
                    print(e)

            case "exit":
                self.running = False

            case _:
                print("Unknown command")



