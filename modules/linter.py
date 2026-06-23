import re
from modules import Displayer, Filer, Config, CheckComment

class ProgressLinter:
    KEYWORDS = [
        'define', 'variable', 'display', 'find', 'for', 'each',
        'if', 'then', 'else', 'do', 'end', 'procedure', 'run',
        'input', 'output', 'message', 'not', 'skip', 'and', 'true', 
        'false', 'yes', 'no', 'begins', 'where', 'no-lock', 'no-error',
        'function', 'returns', 'first', 'last', 'break', 'by', 'as', 'date',
        'integer', 'datetime', 'time', 'now', 'begins', 'character', 'no-undo',
        'repeat', 'case', 'while'
    ]

    BLOCK_WORDS = [
        r"for\s*each", r"for\s*first", r"for\s*last", r"case", r"function", r"procedure", r"forward", r"do", r"repeat"
    ]

    BLOCK_IF_WORDS = [
        r"for\s*each", r"for\s*first", r"for\s*last", r"case", r"find", r"if"
    ]

    def __init__(self, displayer:Displayer, filer:Filer, check_comment: CheckComment, config: Config):
        self.__RESULT = []
        self.displayer = displayer
        self.filer = filer
        self.check_comment = check_comment
        self.config = config

        self.stack = []
        self.if_state_flag = False
        self.then_flag = False

        self.function_flag = False

        self.end_flag = False

        self.do_checker = False

        self.for_checker = False

        self.need_comment = True
        self.comment_state = 0
        self.is_comment = False

        self.is_include = False


    def parse_file(self,filename):
        line_num = 0
        check_full = True
        count = 0

        if self.config.lines != "":
            check_full = False
            try:
                count = int(self.config.lines)
            except Exception as e:
                print(f"Значение {self.config.lines} должно быть числом!")
                check_full = True

        for line in self.filer.read_file_line(filename):
            line_num += 1
            if not check_full and line_num > count:
                self.filer.add_new_line(line)
            else:
                try:
                    self._check_line(line.rstrip(), line_num)
                except Exception as e:
                    print(f"ERROR LINE {line_num} line: {line} er_mes: {e}")
                    self.filer.add_new_line(line)
            

        self.displayer.display_warns(self.check_comment.warns_dict)
        if not self.config.no_display:
            self.displayer.display_result(self.__RESULT)
        if self.config.fix:
            self.filer.write_changes(filename)

    def _check_line(self, line_string, line_num):

        if self._check_include(line_string):
            self.filer.add_new_line(line_string + "\n")
            return
        
        

        
        self.do_checker = False
        self.need_comment = True

        if line_string.strip() == "":
            self.filer.add_new_line(line_string + "\n")
            return
        
        new_line = ""

        self.comment_state = self.check_comment.check_is_comment(line_string, line_num)
        self.is_comment = self.check_comment.is_comment

        if self.is_comment and (self.comment_state != 1 and self.comment_state != 4 and self.comment_state != 3):
            self.filer.add_new_line(line_string + "\n")
            return

        if self.comment_state == 1:
            new_line = self.check_comment.comment_ms[line_num]["line"]
            # проверка на двоеточие для FOR
            self._is_end_for(new_line)

            if self._is_string(new_line):
                self.filer.add_new_line(line_string + "\n")
                return
            #self.is_comment = True
        elif self.comment_state == 2:
            new_line = self.check_comment.comment_ms[line_num]["line"]

            # проверка на двоеточие для FOR
            self._is_end_for(new_line)

            if self._is_string(new_line):
                self.filer.add_new_line(line_string + "\n")
                return
            #self.is_comment = False
        elif self.comment_state == 3:
            # проверка на двоеточие для FOR
            self._is_end_for(new_line)

            if re.search(r"\bend\b", self.check_comment.comment_ms[line_num]["line"], re.I):
                self.stack.pop()
            self.filer.add_new_line(line_string + "\n")
            return
        elif self.comment_state == 4:
            #self.is_comment = False
            self.filer.add_new_line(line_string + "\n")
            return
        elif self.comment_state == 5:
            self.filer.add_new_line(line_string + "\n")
            return
        else:
            # проверка на двоеточие для FOR
            self._is_end_for(new_line)

            new_line = line_string
            if self._is_string(new_line):
                self.filer.add_new_line(new_line + "\n")
                return
                 

        # сюда можно будет добавить разные методы проверки
        new_line = self._check_uppercase(new_line)

        new_line = self._check_end_statement_comment(new_line, line_num)
        
        if self.comment_state == 1 or (self.comment_state == 2 and self.need_comment):
            new_line = new_line + self.check_comment.comment_ms[line_num]["comment"]

        new_line = new_line + "\n"

        self.filer.add_new_line(new_line)

        if new_line.strip() != line_string.strip():
            self._write_result(line_num, line_string, new_line)
    
    def _check_uppercase(self, new_line):
        '''
        Проверка регистра ключевых слов
        '''
        for kw in self.KEYWORDS:
            pattern = r"\b" + re.escape(kw) + r"(?![\w-])"
            new_line = re.sub(pattern, kw.upper(), 
                            new_line, flags=re.IGNORECASE)
        
        return new_line
    
    def _is_string(self, new_line):
        if not self.is_comment:

            if re.search(r"\"", new_line):
                return True
            if re.search(r"'", new_line):
                return True
            return False
        return False
    

    def _check_include(self, new_line):
        if re.search(r"\{(.+?)\}", new_line):
            return True
        if re.search(r"\{", new_line) and not self.is_comment:
            self.is_include = True
            return True
        if re.search(r"\}", new_line) and not self.is_comment:
            self.is_include = False
            return True
        if self.is_include:
            return True
        return False

    def _check_end_statement_comment(self, new_line:str, line_num):
        '''
        проверка комментариев после end
        '''

        self._check_if_statement(new_line, line_num)

        self._check_blocks(new_line, line_num)

        new_line = self._check_end_of_block(new_line, line_num)


        return new_line

    def _check_end_of_block(self, new_line:str, line_num):
        if re.search(r"\bend\b", new_line, re.I):
            if not re.search(r"{(.*?)\bend\b(.*?)}", new_line, re.IGNORECASE):
                self.end_flag = True

        dot_match = re.search(r"\.", new_line)
        if dot_match and self.end_flag:

            self.end_flag = False
            end_info_from_stack = self.stack.pop()

            if re.search(r"\bfor\b", end_info_from_stack, re.IGNORECASE):
                self.for_checker = False

            dot_position = dot_match.start()
            
            if self.comment_state == 0:
                
                return new_line[:dot_position + 1] + end_info_from_stack + new_line[dot_position + 1:]
            if self.comment_state == 1:
                
                return new_line[:dot_position + 1] +\
                    end_info_from_stack +\
                    new_line[dot_position + 1:]
            if self.comment_state == 2:

                

                comment_line = self.check_comment.comment_ms[line_num]["comment"]

                comment_start_search_result = re.search(r"/\*\s*END", comment_line)
                if comment_start_search_result:

                    #com_start_pos = comment_start_search_result.start()
                    # получаю последний индекс поиска END                    
                    comment_end_search_result = re.search(r"\*/", comment_line)

                    if comment_end_search_result:
                        #com_end_pos = comment_end_search_result.end()
                        if comment_line.strip() == end_info_from_stack.strip():
                            
                            return new_line
                        else:
                            self.need_comment = False
                            return new_line + end_info_from_stack
                else:
                    return new_line + end_info_from_stack

        return new_line

    def _is_end_for(self, new_line):
        if self.for_checker:
            if re.search(r":", new_line):
                self.for_checker = False
                return True
            else:
                return False
        else:
            return True

    def _check_blocks(self, new_line:str, line_num):
        for bw in self.BLOCK_WORDS:
            if re.search(r"\b{}\b".format(bw), new_line, re.IGNORECASE):
                if bw == r"procedure" and not re.search(r"\bend\b", new_line, re.I):
                    self.stack.append(f" /* END {new_line[:-1]} */")
                if bw == r"function" and not re.search(r"\bend\b", new_line, re.I):
                    self.function_flag = True
                    func_name_match = re.search(r"\bFUNCTION\b\s+(.+?)\s+\bRETURNS\b", new_line, re.IGNORECASE)
                    if not func_name_match:
                        self.function_flag = False
                        return
                    self.stack.append(f" /* END FUNCTION {func_name_match.group(1)} */ ")
                if bw == r"forward" and self.function_flag:
                    self.stack.pop()
                if bw == r"case" and not re.search(r"\bend\b", new_line, re.I):
                    self.stack.append(f" /* END CASE {line_num} */ ") 
                if bw == r"for\s*each" and not self.for_checker:
                    self.for_checker = True
                    self.stack.append(f" /* END FOR {line_num}*/ ")
                if bw == r"for\s*first" and not self.for_checker:
                    self.for_checker = True
                    self.stack.append(f" /* END FOR {line_num}*/ ")
                if bw == r"for\s*last" and not self.for_checker:
                    self.for_checker = True
                    self.stack.append(f" /* END FOR {line_num}*/ ")
                if bw == r"repeat" and not re.search(r"\bend\b", new_line, re.I):
                    self.stack.append(f" /* END REPEAT {line_num}*/ ")
                if bw == r"do" and not self.do_checker and not re.search(r"\bend\b", new_line, re.I):
                    self.stack.append(f" /* END DO {line_num}*/ ")

    def _check_if_statement(self, new_line: str, line_num: int):
        if re.search(r"\bIF\b(.*?)\bTHEN\b(.*?)\bELSE\b", new_line, re.IGNORECASE):
            return

        if re.search(r"\bif\b", new_line, re.IGNORECASE):
            if not re.search(r"\bIF\b(.*?)\bTHEN\b(.*?)\bELSE\b", new_line, re.IGNORECASE):
                self.stack.append(f" /* END IF {line_num} */ ")
                self.if_state_flag = True

        if self.if_state_flag:
            if re.search(r"\bthen\b", new_line, re.IGNORECASE):
                self.then_flag = True

        if self.if_state_flag and self.then_flag:
            for el in self.BLOCK_IF_WORDS:
                if re.search(r"\b{}\b".format(el), new_line, re.IGNORECASE):
                    self.stack.pop()
                    self.if_state_flag = False
                    self.then_flag = False
                    return
            if re.search(r"\bdo\s*:", new_line, re.IGNORECASE):

                self.if_state_flag = False
                self.then_flag = False
                self.do_checker = True

                
            elif new_line.endswith("."):

                self.stack.pop()
                self.if_state_flag = False
                self.then_flag = False

    def _write_result(self, line_num, line_string, new_line):
            '''
            Запись результата проверок, если были изменения
            '''
            res_dict = {}
            res_dict["line_num"] = line_num
            res_dict["old_line"] = line_string
            res_dict["new_line"] = new_line

            self.__RESULT.append(res_dict)