import argparse

class Config:
    '''
    Предварительные настройки
    '''
    def __init__(self):
        self.files = []
        self.enc = ""
        self.fix = False
        self.no_display = False
        self.lines = ""
        
        self._get_parser_args()

    def _get_parser_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("files", nargs="+", help="Файлы для обработки")
        parser.add_argument("--enc", help="Set encoding cp866 or windows-1251")
        parser.add_argument("--fix", action="store_true")
        parser.add_argument("--no_display", action="store_true")
        parser.add_argument("--lines", help="Set count for check, or all")
        args = parser.parse_args()
        
        self.files = args.files
        self.enc = args.enc
        self.fix = args.fix
        self.no_display = args.no_display
        self.lines = args.lines