from tkinter import Tk, Label, Button
from tkinter import *
from tkinter import messagebox
from tkinter.scrolledtext import *
from PIL import Image, ImageTk
import functools
import random
import math
import time

class Game:
    def __init__(self, window, rows, columns):
        self.window = window
        self.window.title('Minesweeper')
        self.window.geometry("1000x666".format(self.window.winfo_screenwidth(), self.window.winfo_screenheight()))
        self.window.resizable(False, False)
        self.window.bind('<Escape>', self.toggle_fullscreen)
        self.canvas = Canvas(window)
        self.canvas.place(relx = 0.4, rely = 0.5, anchor = CENTER)
        
        self.rows = rows
        self.columns = columns
        self.mines = []
        self.non_mines = []
        self.tiles = []
        self.mine_locations = set()
        self.create_buttons()

        self.game_paused = True

        self.clock = Label(window, text = '00:00', font='Arial 36')
        self.clock.place(relx = 0.75, rely = 0.1, anchor = NW)
        self.flags_left = Label(window, text = 'X: ' + str(self.rows*self.columns//5), font = 'Arial 36')
        self.flags_left.place(relx = 0.75, rely = 0.2, anchor = NW)
        Button(window, text = 'RESET', font='Arial 18 bold', command = self.reset, width = 8).place(relx = 0.75, rely = 0.9, anchor = SW)

    def toggle_fullscreen(self, event):
        self.window.attributes('-fullscreen', not self.window.attributes('-fullscreen'))

    def create_buttons(self):
        self.tile_values = [[0 for x in range(self.columns)] for y in range(self.rows)]
        self.tiles = [[0 for x in range(self.columns)] for y in range(self.rows)]
        for x in range(self.rows):
            for y in range(self.columns):
                self.tiles[x][y] = Button(self.canvas, text='', font='Arial ' + str(int(200//math.sqrt(self.rows*self.columns))), state = 'active', command=functools.partial(self.start, x, y), height = 1 + int(math.sqrt(self.rows*self.columns)//30), width = 3)
                self.tiles[x][y].grid(row = x, column = y, columnspan = 1, sticky = 'ew')
                self.tiles[x][y].bind("<Button-3>", self.flag)

    def start(self, row, column):
        self.game_paused = False
        while len(self.mine_locations) < (self.rows*self.columns//5):
            x = random.randint(0, self.rows - 1)
            y = random.randint(0, self.columns - 1)
            if abs(row - x) > 1 or abs(column - y) > 1:
                self.mine_locations.add((x, y))

        for x in range(self.rows):
            for y in range(self.columns):
                if (x, y) in self.mine_locations:
                    self.tiles[x][y].configure(command=self.explode, text='')
                    self.mines.append([x, y])
                    for i in range(-1,2):
                        for j in range(-1,2):
                            if not ((x + i) < 0 or (y + j) < 0 or (x + i) >= self.rows or (y + j) >= self.columns):
                                self.tile_values[x + i][y + j] += 1
                else:
                    self.tiles[x][y].configure(command=functools.partial(self.mark, x, y), text='')
                    self.non_mines.append(self.tiles[x][y])
        
        self.mark(row, column)
        self.start_time = time.time()
        self.timer()

    def timer(self):
        current_time = time.time()
        delta_time = (current_time - self.start_time)
        minutes = int(delta_time//60)
        seconds = int(delta_time%60)
        if delta_time < 3600 and not self.game_paused:
            self.clock.config(text='{0:02d}:{1:02d}'.format(minutes, seconds))
            self.window.after(100, self.timer)

    def mark(self, row, column):
        if not self.tiles[row][column].cget('state') == DISABLED:
            self.tiles[row][column].config(text = str(self.tile_values[row][column]), bg = 'gray85', state = DISABLED)
            if not self.tile_values[row][column]:
                self.tiles[row][column].config(text ='', bg = 'gray85')
                for i in range(-1,2):
                        for j in range(-1,2):
                            if not ((row + i) < 0 or (column + j) < 0 or (row + i) >= self.rows or (column + j) >= self.columns):
                                self.mark(row + i, column + j)

        flags = 0
        for x in self.tiles:
            for y in x:
                if y.cget('text') == 'X':
                    flags += 1
                    self.flags_left.config(text = 'X: ' + str(self.rows*self.columns//5 - flags), fg = ('black', 'red')[(self.rows*self.columns//5 - flags) < 0])
                                
        for x in self.non_mines:
            if not x.cget('state') == DISABLED:
                return

        #self.title['text'] = '  YOU  WIN!!  '
        self.game_paused = True
        self.flags_left.config(text = '')
        for each in self.mines:
            self.tiles[each[0]][each[1]].config(text='', bg='green', state=DISABLED)
        for x in self.tiles:
            for y in x:
                y.config(state=DISABLED)

    def mark_all(self, row, column):
        for x in self.non_mines:
            if not x.cget('state') == DISABLED:
                x.config(text='', bg='gray85')

        #self.title['text'] = '  YOU  WIN!!  '
        self.game_paused = True
        for each in self.mines:
            self.tiles[each[0]][each[1]].config(text='', bg='green', state=DISABLED)
        for x in self.tiles:
            for y in x:
                y.config(state=DISABLED)

    def explode(self):
        #self.title['text'] = '  GAME  OVER  '
        self.game_paused = True
        self.flags_left.config(text = '')
        for each in self.mines:
            self.tiles[each[0]][each[1]].config(text='', bg='red', state=DISABLED)
        for x in self.tiles:
            for y in x:
                y.config(state=DISABLED)

    def flag(self, event):
        if not len(self.mines):
            return
        
        if not event.widget.cget('state') == DISABLED:
            if event.widget.cget('text') == 'X':
                event.widget.config(text='')
            else:
                event.widget.config(text='X')

        flags = 0
        for x in self.tiles:
            for y in x:
                if y.cget('text') == 'X':
                    flags += 1
                    self.flags_left.config(text = 'X: ' + str(self.rows*self.columns//5 - flags), fg = ('black', 'red')[(self.rows*self.columns//5 - flags) < 0])

    def reset(self):
        self.mines = []
        self.non_mines = []
        self.tiles = []
        self.mine_locations = set()
        self.create_buttons()

        self.game_paused = True

        self.clock.config(text = '00:00')
        self.flags_left.config(text = 'X: ' + str(self.rows*self.columns//5))
