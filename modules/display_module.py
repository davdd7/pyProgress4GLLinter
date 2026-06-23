class Displayer:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

    def __init__(self, no_display=False):
        self.no_display = no_display

    def display_result(self, result: list):
        if self.no_display:
            return
        else:
            if len(result) > 0:
                for line_info in result:
                    self._display_dict_result(line_info)
            else:
                self._display_good()

    def display_warns(self, warns_dict:dict):
        if len(warns_dict) == 0:
            return
        print(f"{self.YELLOW} Check this lines for mustakes.")
        print(f"Delete please all comments inside, or set them right\n")
        for key, val in warns_dict.items():
            print(f"line_num {key} line_value: {val}")

        print(f"{self.RESET}\n")



    def _display_good(self):
        print(f"{self.GREEN}Don`t need changes!{self.RESET}")

    def _display_dict_result(self, some_dict: dict):
        print("\n")
        print(f"line: {some_dict["line_num"]}")
        print(f"{self.RED}{some_dict["old_line"]}{self.RESET}")
        print(f"{self.GREEN}{some_dict["new_line"]}{self.RESET}")