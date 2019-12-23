#!/usr/bin/python3
import subprocess
class Mod:


    def __init__(self, mod_name="UNNAMED_MOD!!",
                    commands=["Empty command list!!"]):

        if type(mod_name) is not str:
            raise ValueError('Argument mod_name has to be str!')

        for catcher in commands:
            if type(catcher) is not str:
                raise ValueError('Commands have to be str!')

        self.commands = commands
        self.commands.extend(("exit","help","manual","cls"))
        self.mod_name = mod_name
        self.running = True

    def print_help(self):
        print("{} mode\nFor more information use"
                " Man command.".format(self.mod_name))
        separator()
        print(*self.commands)

    def clear_screen(self):
        subprocess.call("clear", shell=True)

    def manual(self, mod_name):
        with open(modname,"r") as manual:
            print(manual.read())

    def check_if_command(self,command):
        if command in self.commands:
            return True
        return False

    def linux_command(self, command, argument=None):
        if check_if_command(command):
            if argument:
                run_command(command, argument)
            else:
                run_command(command)
        print("This is not a valid command!!")
    
    def exit(self):
        self.running = False


class Usemod(Mod):


    def __init__(self, name, commands):
        super().__init__(name, commands)

    def config(self):
        pass





def separator():
    print(40*"=")



if __name__ == "__main__":
    try:
        First = Usemod("Use", ["ping", "tracert", "ssh"])
        First.print_help()
        print(First.running)
        First.exit()
        print(First.running)
    except Exception as err:
        print(err)

    try:
        Another = Usemod("SoomeFunc", [5])
        Another.print_help()
    except Exception as err:
        print(err)

    try:
        Second = Usemod(5,[5])
        Second.print_help()
    except Exception as err:
        print(err)

    try:
        Third = Usemod("5",[",","da",98])
        Third.print_help()
    except Exception as err:
        print(err)
