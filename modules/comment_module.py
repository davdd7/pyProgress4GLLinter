import re

class CheckComment:
    def __init__(self):
        
        self.start_com_ind = 0
        self.end_com_ind = 0

        self.is_comment = False

        self.comment_ms = {}
        self.warns_dict = {}

        self.comment_stack = []

    # Если мы находим комментарий
    # устанавливаем у него флаг и номер строки - 
    # делаем как ключ для словаря, чтобы в случае ошибок - выдавать варнинги
    # а так же объединять после результата


    # если комментарий флаг true - игнорируем все строки до первого */


    def check_is_comment(self, line, line_num):
        self.comment_state = 0

        line_for_checking = ""
        line_with_comment_data = ""

        op_stack = []
        cl_stack = []
        # 0 - нет коммента
        # 1 - есть открывающий только
        # 2 - есть оба
        # 3 - варнинг
        # 4 - закрыт комментарий
        # 5 - просто комментарий - попускаем
        op_stack = list(re.finditer(r"/\*", line))
        cl_stack = list(re.finditer(r"\*/", line))

        if len(op_stack) == 0 and len(cl_stack) == 0:
            if self.is_comment:
                return 5
            return 0
        
        st_res = len(op_stack) - len(cl_stack)

        if st_res == 0:
            if self.is_comment:
                return 5

        elif st_res > 0:
            for i in range(st_res):
                self.comment_stack.append(1)

            if self.is_comment:
                return 5
        elif st_res < 0:
            for i in range(abs(st_res)):
                self.comment_stack.pop()
            if len(self.comment_stack) == 0:
                self.is_comment = False
                return 4
            else:
                return 5


        st_com = re.search(r"/\*", line)

        # находим начало комментария
        if st_com:
            
            start_com_ind = st_com.start()

            line_for_checking = line[:start_com_ind]
            line_with_comment_data = line[start_com_ind:]

            if not self.is_comment:
                self.is_comment = True

                if line_for_checking.strip() == "":
                    if len(self.comment_stack) == 0:
                        self.is_comment = False

                    return 5

                end_com_search = re.search(r"\*/", line_with_comment_data)
                # сразу здесь проверяем на второй

                if end_com_search:
                    # ищем конец комментария. Если есть - прверяем что дальше пусто. 
                    # Если не пусто - записываем для варнинга
                    end_com_ind = end_com_search.end()
                    line_after_comment = line_with_comment_data[end_com_ind:]

                    if len(line_after_comment.strip()) == 0:
                        # если пусто после комментария - тогда 
                        # создаем часть для разбора и часть для добавления просто
                        line_info_dict = {
                            "line" : line_for_checking,
                            "comment" : line_with_comment_data
                        }
                        self.comment_ms[line_num] = line_info_dict
                        self.is_comment = False
                        return 2
                    else:
                        if len(self.comment_stack) == 0:
                            self.is_comment = False
                        self.warns_dict[line_num] = line
                        line_info_dict = {
                            "line" : line_for_checking,
                            "comment" : line_with_comment_data
                        }
                        self.comment_ms[line_num] = line_info_dict
                        # что-то есть после комментария -> в варнинг
                        return 3
                
                else:
                    line_info_dict = {
                        "line" : line_for_checking,
                        "comment" : line_with_comment_data
                    }
                    self.comment_ms[line_num] = line_info_dict
                    return 1
        
            else:
                
                return 5
        else:
            if self.is_comment:
                return 5
            return 0