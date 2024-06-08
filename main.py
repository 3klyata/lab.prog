import curses
from text_analysis import *
from text_editor import TextEditor
import os

class File:
    def __init__(self , path = '') -> None:
        self.file_path = path

    def choose_file(self,path):
        if not os.path.isfile(path):
            return False
        self.file_path = path

    def read(self):
        if not os.path.isfile(self.file_path):
            return None
        file = open(self.file_path, 'r', encoding='utf-8')
        text = file.read()
        file.close()
        return text

    def get_path(self):
        return self.file_path


class MenuItem:
    
    def __init__(self, name, function_name, *args) -> None:
        self.name = name
        self.function = function_name
        self.args = args
    
    def use(self):

        # Перевірка, чи args містить дані 
        if self.args == ():
            self.function()
        else:
            self.function(*self.args)


class Menu:
    
    def __init__(self, stdscr, file: File = None):
        self.stdscr = stdscr
        self.menu_items = []
        self.current_row = 0
        self.file = file if file != None else None

    def add_menu_item(self, menu_item: MenuItem):
        self.menu_items.append(menu_item)

    def draw_menu(self):
        self.stdscr.erase()
        y = 0
        for ind_y, row in enumerate(self.menu_items):
            x = 0
            y = ind_y

            # Підсвічування вибраного пункту меню
            if ind_y == self.current_row:
                self.stdscr.attron(curses.color_pair(1))
                self.stdscr.addstr(y, x, row.name)
                self.stdscr.attroff(curses.color_pair(1))
            else:
                self.stdscr.addstr(y, x, row.name)

        if self.file:
            FILE_NAME_OFFSET = 2
            if self.file.get_path():
                self.stdscr.addstr(y + FILE_NAME_OFFSET, 0, f"Обраний файл: {self.file.get_path()}")
            else:
                self.stdscr.addstr(y + FILE_NAME_OFFSET, 0, 'Файл не обран або введеного файлу не існує')
        self.stdscr.refresh()

    def handle_input(self):
        key = self.stdscr.getch()
        if key == curses.KEY_UP and self.current_row > 0:
            self.current_row -= 1
        elif key == curses.KEY_DOWN and self.current_row < len(self.menu_items)-1:
            self.current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]: # коди клавіші ENTER
            
            # Використання функції, яка прив'язана до пункту меню.
            self.menu_items[self.current_row].use() 
        if key == 27: #код клавіші ESC
            return False
        

    def start(self):

        # Відключення миготіння курсору
        curses.curs_set(0) 

        # Колірна пара для виділення тексту
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.current_row = 0
        self.draw_menu()
        while True:
            if self.handle_input() == False:
                break
            self.draw_menu()

def count_wordforms(stdscr, input_text):
    
    # Перевірка, чи input_text функція, яка може повернути текст
    if callable(input_text):
        text = input_text()
    else:
        text = input_text

    if not text or len(text) == 0:
        return False

    stdscr.erase()
    stdscr.addstr("ОБРОБКА ДАНИХ")
    stdscr.refresh()

    ta = TextAnalizer()
    wordforms = ta.text_analysis(text, CountAbsoluteWordforms())
    max_y = stdscr.getmaxyx()[0] - 3
    cursor_y = 0

    while True:
        stdscr.erase()
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr("Натисніть клавішу ESC щоб вийти до меню \n\n")
        stdscr.attroff(curses.color_pair(1))

        # Виведення словоформ до кінця видимого екрану
        for ind, word in enumerate(wordforms):
            if ind < cursor_y:
                continue
            if ind >= max_y + cursor_y:
                break
            stdscr.addstr(f"{word} : {wordforms[word]}\n")

        # Обробка клавіш перегортання
        key = stdscr.getch()
        if key == curses.KEY_DOWN and cursor_y+max_y < len(wordforms):
            cursor_y += 1
        elif key == curses.KEY_UP and cursor_y > 0:
            cursor_y -= 1

        if key == 27: # код клавіші ESC
            break
        
        stdscr.refresh()        
               

def сount_exclamatory_sentence(stdscr, input_text):

     # Перевірка, чи input_text функція, яка може повернути текст
    if callable(input_text):
        text = input_text()
    else:
        text = input_text

    if not text or len(text) == 0:
        return False

    ta = TextAnalizer()
    exclamatory_count = ta.text_analysis(text, CountExclamatorySentence())
    
    while True:
        stdscr.erase()        
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr("Натисніть клавішу ESC щоб вийти до меню \n\n")
        stdscr.attroff(curses.color_pair(1))
    
        stdscr.addstr(f"Кількість окличних речень у тексті: {exclamatory_count}\n")

        key = stdscr.getch()
        if key == 27: #Escape key code
            break
        stdscr.refresh()   

      
def flexion_highlighting(stdscr):
    ta = TextAnalizer()
    last_word = ''

    while True:  
        stdscr.erase()       
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr("Введіть \q щоб вийти до меню\n\n")
        stdscr.attroff(curses.color_pair(1))

        stdscr.addstr(f"Останнє слово: {last_word} \n\n")
        stdscr.addstr(f"Введіть слово, щоб знайти флексію (закінчення) \n")
        curses.echo() 
        word = stdscr.getstr(5,0, 30).decode()
        
        # Перевірка, чи ввів користувач слово
        if word == '' or not word or set(word) == set(' '):
            continue
        if word == '\q' or word == '\й': 
            break
        last_word = ta.text_analysis(word, FlexionHighlighting())

        stdscr.refresh()   


def load_file(stdscr, file: File):
    stdscr.erase()
    stdscr.addstr(f"Введіть шлях до файлу. Якщо файл каталозі {TEXTS_FOLDER}, просто введіть назву файлу\n")
    curses.echo() 
    stdscr.addstr(2,0, "Шлях: ")
    path = stdscr.getstr(2,6, 256).decode() 
    if not '\\' in path and not '/' in path:
        path = f"{TEXTS_FOLDER}/" + path 
    file.choose_file(path)
    return path


def main(stdscr):
    file = File()
    text_editor = TextEditor(stdscr)
    main_menu = Menu(stdscr, file)
    analysis_menu = Menu(stdscr)

    main_menu.add_menu_item(MenuItem('Завантажити файл', load_file, stdscr, file))
    main_menu.add_menu_item(MenuItem('Редагувати файл', text_editor.start, file.get_path))
    main_menu.add_menu_item(MenuItem('Аналіз тексту', analysis_menu.start))
    main_menu.add_menu_item(MenuItem('Закінчити роботу', exit))
   
    analysis_menu.add_menu_item(MenuItem('Підрахунок абсолютної частоти вживання словоформ', count_wordforms, stdscr, file.read))
    analysis_menu.add_menu_item(MenuItem('Підрахунок окличних речень', сount_exclamatory_sentence, stdscr, file.read))
    analysis_menu.add_menu_item(MenuItem('Пошук флексії (закінчення) слова', flexion_highlighting, stdscr))
    analysis_menu.add_menu_item(MenuItem('Назад', main_menu.start))
    main_menu.start()



curses.wrapper(main)
