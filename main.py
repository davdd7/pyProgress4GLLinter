from modules import (
    CheckComment, 
    Config, 
    Displayer, 
    Filer, 
    ProgressLinter
)



def main_flow():
    config = Config()
    files_for_check = config.files

    filer = Filer(config.enc)
    displayer = Displayer(config.no_display)
    check_comment = CheckComment()
    my_linter = ProgressLinter(displayer, filer, check_comment, config)

    for file in files_for_check:
        my_linter.parse_file(file)

    

if __name__ == "__main__":

    main_flow()
