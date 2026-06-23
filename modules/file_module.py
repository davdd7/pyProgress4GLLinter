import shutil


class Filer:
    def __init__(self, file_encode):
        self.file_encode = file_encode
        self.__NEW_LINES = []
        
    def read_file_line(self, filename):
        try:
            if self.file_encode != "windows-1251" and self.file_encode != "cp866":
                self.file_encode = self._detect_encoding(filename)
            with open(filename, "r", encoding=self.file_encode) as reading_file:
                for line in reading_file:
                    yield line
        except Exception as e:
            print("Error in reading line!")
            return

    def add_new_line(self, new_line):
        self.__NEW_LINES.append(new_line)

    def write_changes(self, filename):
        self._create_backup_file(filename)
        with open(filename, "w", encoding=self.file_encode) as wr_file:
            wr_file.writelines(self.__NEW_LINES)

    def _detect_encoding(self, filename):
        try:
            with open(filename, "r", encoding="windows-1251") as dec_fi:
                dec_fi.read()
            return "windows-1251"
        except UnicodeDecodeError:
            return "cp866"
    
    @staticmethod
    def _create_backup_file(filename):
        shutil.copy2(filename, filename + ".bak")