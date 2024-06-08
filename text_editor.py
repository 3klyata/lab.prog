import curses


class TextEditor:

    def __init__(self, stdscr):
        self.stdscr = stdscr

    def start(self, file_path):

        # Перевірка, чи input_text функція, яка може повернути текст
        if callable(file_path):
            path = file_path()
        else:
            path = file_path

        if path == '' or not path:
            return False
        
        # Налуштування вікна терміналу для зчитування введення
        self.stdscr.nodelay(1)
        curses.noecho()
        curses.raw()
        self.stdscr.keypad(1)
        
        content = []
        src = path
        win_max_y, win_max_x = self.stdscr.getmaxyx()
        offset_y = 2
        win_max_y -= offset_y
        x, y, max_y, max_x = [0] * 4
        try:
            with open(src, encoding='utf-8') as f:
                file_content = f.read().split('\n')
                file_content = file_content[:-1] if len(
                    file_content) > 1 else file_content
                for line in file_content:
                    content.append([ord(symbol) for symbol in line])
        except:
            content.append([])

        while True:

            # Виведення тексту
            self.stdscr.move(0, 0)
            if max_y < y:
                y = max_y
            if max_y >= y + win_max_y:
                y = max_y - win_max_y + 1
            if max_x < x:
                x = max_x
            if max_x >= x + win_max_x:
                x = max_x - win_max_x + 1
            for line_y in range(win_max_y):
                row = line_y + y
                for symbol_x in range(win_max_x):
                    column = symbol_x + x
                    try:
                        self.stdscr.addch(line_y, symbol_x, content[row][column])
                    except:
                        pass
                self.stdscr.clrtoeol()
                try:
                    self.stdscr.addch('\n')
                except:
                    pass

            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            self.stdscr.attron(curses.color_pair(1))
            self.stdscr.addstr(win_max_y + offset_y - 1, 0, "Ctrl + q щоб вийти     Ctrl + s щоб зберегти")
            self.stdscr.attroff(curses.color_pair(1))

            # Переміщення курсору
            curses.curs_set(0)
            self.stdscr.move(max_y - y, max_x - x)
            curses.curs_set(1)

            self.stdscr.refresh()

            # Обробка введення
            key = -1
            while (key == -1):
                key = self.stdscr.getch()
                
            # Перевірка, чи символ не є спеціальним по коду
            if (key > 31 and key < 192) or key >= 1024:
                content[max_y].insert(max_x, key)
                max_x += 1
            
            # Перевріка, чи символ є символом нової лінії
            elif chr(key) in '\n\r':
                line_symbols = content[max_y][max_x:]
                content[max_y] = content[max_y][:max_x]
                max_y += 1
                max_x = 0
                content.insert(max_y, [] + line_symbols)
                
            # Перевірка, чи натиснута клавіша BACKSPACE
            elif key in [8, 263]:
                if max_x:
                    max_x -= 1
                    del content[max_y][max_x]
                elif max_y:
                    line_symbols = content[max_y][max_x:]
                    del content[max_y]
                    max_y -= 1
                    max_x = len(content[max_y])
                    content[max_y] += line_symbols
            elif key == curses.KEY_LEFT:
                if max_x != 0: max_x -= 1
                elif max_y > 0:
                    max_y -= 1
                    max_x = len(content[max_y])
            elif key == curses.KEY_RIGHT:
                if max_x < len(content[max_y]): max_x += 1
                elif max_y < len(content) - 1:
                    max_y += 1
                    max_x = 0
            elif key == curses.KEY_UP and max_y != 0:
                max_y -= 1
            elif key == curses.KEY_DOWN and max_y < len(content) - 1:
                max_y += 1
            line = content[max_y] if max_y < len(content) else None
            rwlen = len(line) if line is not None else 0
            if max_x > rwlen: max_x = rwlen
            
            # 0x1f - модифікатор клавіши Ctrl
            if key == (ord('q') & 0x1f):
                return True
            elif key == (ord('s') & 0x1f):
                file_content = ''
                for line_symbols in content:
                    file_content += ''.join([chr(c)
                                             for c in line_symbols]) + '\n'
                with open(src, 'w', encoding='utf-8') as f:
                    f.write(file_content)
