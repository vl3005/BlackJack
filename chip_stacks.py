import concurrent.futures
import random
from collections import deque
from math import sqrt
from tkinter import BooleanVar, Label, Tk, DoubleVar
from tkinter import Canvas, font, Frame

import simpleaudio as sa
from PIL import Image, ImageTk


class Chip1:

    def __init__(self, amount=1):
        self.value = 1
        self.image = chip1imgobj
        self.amount = amount


# noinspection PyPep8Naming
class Chip2_5:

    def __init__(self, amount=1):
        self.value = 2.5
        self.image = chip2_5imgobj
        self.amount = amount


class Chip5:

    def __init__(self, amount=1):
        self.value = 5
        self.image = chip5imgobj
        self.amount = amount


class Chip10:

    def __init__(self, amount=1):
        self.value = 10
        self.image = chip10imgobj
        self.amount = amount


class Chip25:

    def __init__(self, amount=1):
        self.value = 25
        self.image = chip25imgobj
        self.amount = amount


class Chip50:

    def __init__(self, amount=1):
        self.value = 50
        self.image = chip50imgobj
        self.amount = amount


class Chip100:

    def __init__(self, amount=1):
        self.value = 100
        self.image = chip100imgobj
        self.amount = amount


class Chip500:

    def __init__(self, amount=1):
        self.value = 500
        self.image = chip500imgobj
        self.amount = amount


class Chip1000:

    def __init__(self, amount=1):
        self.value = 1000
        self.image = chip1000imgobj
        self.amount = amount


class Chip2000:

    def __init__(self, amount=1):
        self.value = 2000
        self.image = chip2000imgobj
        self.amount = amount


class Chip5000:

    def __init__(self, amount=1):
        self.value = 5000
        self.image = chip5000imgobj
        self.amount = amount


# noinspection PyUnusedLocal,PyShadowingNames,PyShadowingNames,PyArgumentList
class Stack:
    def __init__(self, felt, x: int, y=0, chip=None, amount=0, stack=()):
        self.stack = deque(stack)
        if not self.stack:
            self.amount = chip.amount
            self.stack.append(chip)
            self.value = chip.amount * chip.value
        else:
            self.amount = 0
            self.value = 0
            for chip_ in stack:
                self.value += chip_.amount * chip_.value
                self.amount += chip_.amount
        self.felt = felt
        self.top_chip = self.stack[len(self.stack) - 1]
        self.desc_frame = Frame(self.felt.master, bg="black", highlightcolor='#e6c117',
                                bd=2, highlightthickness=2,
                                relief="ridge")
        if isinstance(self, BetStack) or isinstance(self, WonStack):
            self.desc_string = f"{self.value}"
        else:
            all_stacks.add(self)
            self.x, self.y = return_closest_spot(x, y)
            self.desc_string = f"({self.amount})\n{self.value}"
        self.tag = f'stack_at_{self.x},{self.y}'
        self.desc_label = Label(self.desc_frame,
                                text=self.desc_string,
                                font=font.Font(size=15, weight='bold'),
                                bg='black', fg='#e6c117')
        self.desc_label.pack(side='left')
        self.felt.create_window(self.x, self.y - 83,
                                window=self.desc_frame,
                                state='hidden',
                                tags=(f"desc{self.x}_{self.y}", self.tag))
        self.draw_stack()
        if not isinstance(self, BetStack):
            self.left_edge = self.felt.bbox(f"top_chip{self.x}_{self.y}")[0] - 34
            self.right_edge = self.felt.bbox(f"top_chip{self.x}_{self.y}")[2] + 34
            for i in range(self.left_edge, self.right_edge):
                available_spots.discard(i)
        self.upper_x, self.upper_y = self.felt.bbox(f"top_chip{self.x}_{self.y}")[0], \
             self.felt.bbox(f"top_chip{self.x}_{self.y}")[1]

    def show_desc_str(self, event):
        self.felt.itemconfig(f"desc{self.x}_{self.y}", state='normal')

    def hide_desc_str(self, event):
        self.felt.itemconfig(f"desc{self.x}_{self.y}", state='hidden')

    def draw_stack(self):
        if self.stack:
            shadow_length = self.amount
            if shadow_length > 20:
                shadow_length = 20
            self.felt.create_image(self.x, self.y - 40, image=shadows[shadow_length - 1],
                                   tags=(f"shadow{self.x}_{self.y}", 'image', self.tag), anchor="n")

            self.felt.create_image(self.x, self.y, image=self.top_chip.image,
                                   tags=(f"top_chip{self.x}_{self.y}", 'image', 'stack', self.tag))
            if not isinstance(self, BetStack) and not isinstance(self, WonStack):
                self.felt.tag_lower("armrest")
                self.felt.tag_lower("image")
                self.felt.tag_lower("back_image")
                self.felt.tag_raise("floating")
                self.felt.tag_bind(f"top_chip{self.x}_{self.y}", "<ButtonPress-1>", self.pick_up_chip)
                self.felt.tag_bind(f"top_chip{self.x}_{self.y}", "<ButtonPress-3>", self.pick_up_stack)
            else:
                self.felt.tag_bind(f"top_chip{self.x}_{self.y}", "<ButtonPress-3>", self.pick_up_chip)
                self.felt.tag_bind(f"top_chip{self.x}_{self.y}", "<ButtonPress-1>", self.pick_up_stack)
            self.felt.tag_bind(f"top_chip{self.x}_{self.y}", "<Alt-ButtonPress-1>", self.put_down_one_chip)
            self.felt.tag_bind(f"top_chip{self.x}_{self.y}", "<Alt-ButtonPress-3>", self.put_down_entire_stack)
            self.felt.tag_bind(f"top_chip{self.x}_{self.y}", "<Enter>", self.show_desc_str)
            self.felt.tag_bind(f"top_chip{self.x}_{self.y}", "<Leave>", self.hide_desc_str)

    def put_down_one_chip(self, event):
        global floating_stack_is_picked
        global floater_total, floater_amount
        wrong_stack = True
        if floating_stack:
            for fl_chip in floating_stack:
                if isinstance(fl_chip, self.top_chip.__class__):
                    # chip_collide_sounds[random.randint(0, 3)].play()
                    self.top_chip.amount += 1
                    fl_chip.amount -= 1
                    if fl_chip.amount == 0:
                        floating_stack.remove(fl_chip)
                    step_x, step_y, frames = self.move_on_chip(event)
                    self.update_floater()
                    self.update_stack()
                    self.move_to_hand(event, frames=frames, step_x=step_x, step_y=step_y)
                    wrong_stack = False
                    break
        if wrong_stack:
            sa.WaveObject.from_wave_file("sounds\\no_good.wav").play()

    def put_down_entire_stack(self, event):
        global floating_stack_is_picked, floater_desc_label
        global floater_total, floater_amount, floater_desc_frame
        wrong_stack = True
        count = 0
        if floating_stack:
            for fl_chip in floating_stack:
                if isinstance(fl_chip, self.top_chip.__class__):
                    count = fl_chip.amount
                    self.top_chip.amount += fl_chip.amount
                    floating_stack.remove(fl_chip)
                    step_x, step_y, frames = self.move_on_chip(event)
                    self.update_stack()
                    wrong_stack = False
                    break
        if not wrong_stack:
            step_x, step_y, frames = self.move_on_chip(event, count=count)
            self.update_floater()
            self.update_stack()
            if floating_stack:
                self.move_to_hand(event, frames=frames, step_x=step_x, step_y=step_y)
        else:
            sa.WaveObject.from_wave_file("sounds\\no_good.wav").play()

    def move_to_hand(self, event, frames=10, step_x=0, step_y=0):
        if (step_x, step_y) == (0, 0):
            distance_x = self.upper_x - (event.x + 20)
            distance_y = self.upper_y - (event.y + 10)
            step_x = distance_x / frames
            step_y = distance_y / frames
        self.felt.itemconfig("shadow", state='normal')
        for i in range(0, frames):
            self.felt.move('floating', -step_x, -step_y)
            self.felt.update()
        self.felt.itemconfig("floater_desc", state='normal')
        self.felt.tag_raise('floating')

    def move_on_chip(self, event, count=1, frames=5):
        distance_x = self.felt.bbox(f"top_chip{self.x}_{self.y}")[0] - self.felt.bbox(f"fl_chip")[0]
        distance_y = self.felt.bbox(f"top_chip{self.x}_{self.y}")[1] - self.felt.bbox(f"fl_chip")[1]
        step_x = distance_x / frames
        step_y = distance_y / frames
        for i in range(0, frames):
            self.felt.move('floating', step_x, step_y)
            # time.sleep(0.01)
            self.felt.update()
        self.felt.itemconfig("shadow", state='hidden')
        self.felt.update()
        for i in range(0, count):
            chip_stack_sounds[random.randint(0, 5)].play()
        return step_x, step_y, frames

    def pick_up_stack(self, event):
        global floating_stack_is_picked, floater_desc_label
        global floater_total, floater_amount, floater_desc_frame
        if not floating_stack:
            for stack in allBetStacks:
                print(stack.top_chip.amount)
            floating_stack.appendleft(self.top_chip.__class__(self.top_chip.amount))
            floating_stack_is_picked = True
            self.felt.tag_bind("back_image", "<ButtonPress-3>", self.place_floater_on_felt)
            self.felt.tag_bind("back_image", "<ButtonPress-1>", self.place_stack_on_felt)
            self.felt.create_image(self.x, self.y + 30, image=floating_shadow_img,
                                   tags=("shadow", "floating", "image"),
                                   state='hidden')  # , anchor='n')
            self.felt.create_image(self.x, self.y, image=self.top_chip.image,
                                   tags=("fl_chip", "floating", "image"))  # , anchor='n')
            floater_desc_frame = Frame(self.felt.master, bg="black", highlightcolor='#e6c117',
                                       bd=2, highlightthickness=2,
                                       relief="raised")
            floater_desc_label = Label(floater_desc_frame,
                                       text=f"{floating_stack[0].value}",
                                       font=font.Font(size=15, weight='bold'),
                                       bg='black', fg='#e6c117')
            floater_desc_label.pack()
            self.felt.create_window(self.x, self.y - 70, state='hidden',
                                    window=floater_desc_frame,
                                    # text=f"{floating_stack[0].value}",
                                    # fill='white', justify='center',
                                    # font=font.Font(size=15, weight='bold'),
                                    tags=("floater_desc", "floating"))
            chip_handle_sounds[random.randint(0, 3)].play()
            self.stack.remove(self.top_chip)
            self.update_floater()
            self.update_stack()
            self.move_to_hand(event)
        else:
            step_x, step_y, frames = self.move_on_chip(event)
            chip_found = False
            for chip in floating_stack:
                if isinstance(chip, self.top_chip.__class__):
                    chip.amount += self.top_chip.amount
                    chip_found = True
                    break
            if not chip_found:
                floating_stack.appendleft(self.top_chip.__class__(self.top_chip.amount))
            self.top_chip.amount = 0
            for stack in allBetStacks:
                print("now ", stack.top_chip.amount)
            self.update_floater()
            self.update_stack()
            self.move_to_hand(event, step_x=step_x, step_y=step_y, frames=frames)

    def pick_up_chip(self, event):
        global floating_stack_is_picked, floater_desc_label
        global floater_total, floater_amount, floater_desc_frame
        if not floating_stack:
            floating_stack.appendleft(self.top_chip.__class__(1))
            floating_stack_is_picked = True
            self.felt.tag_bind("back_image", "<ButtonPress-3>", self.place_floater_on_felt)
            self.felt.tag_bind("back_image", "<ButtonPress-1>", self.place_stack_on_felt)
            self.felt.create_image(self.x, self.y + 30, image=floating_shadow_img,
                                   tags=("shadow", "floating", "image"),
                                   state='hidden')  # , anchor='n')
            self.felt.create_image(self.x, self.y, image=self.top_chip.image,
                                   tags=("fl_chip", "floating", "image"))  # , anchor='n')
            floater_desc_frame = Frame(self.felt.master, bg="black", highlightcolor='#e6c117',
                                       bd=2, highlightthickness=2,
                                       relief="raised")
            floater_desc_label = Label(floater_desc_frame,
                                       text=f"{floating_stack[0].value}",
                                       font=font.Font(size=15, weight='bold'),
                                       bg='black', fg='#e6c117')
            floater_desc_label.pack()
            self.felt.create_window(self.x, self.y - 70, state='hidden',
                                    window=floater_desc_frame,
                                    # text=f"{floating_stack[0].value}",
                                    # fill='white', justify='center',
                                    # font=font.Font(size=15, weight='bold'),
                                    tags=("floater_desc", "floating"))
            chip_handle_sounds[random.randint(0, 3)].play()
            self.top_chip.amount -= 1
            self.update_floater()
            self.update_stack()
            self.move_to_hand(event)
        else:
            step_x, step_y, frames = self.move_on_chip(event)
            chip_found = False
            for chip in floating_stack:
                if isinstance(chip, self.top_chip.__class__):
                    chip.amount += 1
                    chip_found = True
                    break
            if not chip_found:
                floating_stack.appendleft(self.top_chip.__class__(1))
            self.update_floater()
            self.top_chip.amount -= 1
            self.update_stack()
            self.move_to_hand(event, step_x=step_x, step_y=step_y, frames=frames)

    def update_stack(self):
        self.amount = 0
        self.value = 0
        for i in range(len(self.stack) - 1, -1, -1):
            chip = self.stack[i]
            if chip.amount > 0:
                self.amount += chip.amount
                self.value += chip.amount * chip.value
            else:
                self.stack.pop()
        if self.amount > 0:
            self.top_chip = self.stack[len(self.stack) - 1]
            self.desc_label['text'] = f"({self.amount})\n{self.value}"
            shadow_length = self.amount
            if shadow_length > 20:
                shadow_length = 20
            self.felt.itemconfig(f"shadow{self.x}_{self.y}", image=shadows[shadow_length - 1])
            self.felt.itemconfig(f"top_chip{self.x}_{self.y}", image=self.top_chip.image)
        else:
            self.felt.delete(self.tag)
            available_spots.update(set(range(self.left_edge, self.right_edge)))
            all_stacks.discard(self)
            del self
            update_available_spots()

    def follow(self, event):
        self.felt.moveto("floating", event.x + 20, event.y + 30)

    def update_floater(self):
        global floater_total, floater_amount
        floater_total = 0
        floater_amount = 0
        if not floating_stack:
            self.delete_floater_stack()
        else:
            top_chip = floating_stack[len(floating_stack) - 1]
            self.felt.bind("<Motion>", self.follow)
            for chip in floating_stack:
                floater_total += chip.value * chip.amount
                floater_amount += chip.amount
            self.felt.itemconfig('fl_chip', image=top_chip.image)
            floater_desc_label['text'] = f"{floater_total}"
            self.felt.tag_raise('floating')

    def delete_floater_stack(self):
        global floating_stack_is_picked
        floating_stack.clear()
        self.felt.delete("floating")
        floating_stack_is_picked = False
        self.felt.tag_unbind("back_image", "<ButtonPress-1>")
        self.felt.tag_unbind("back_image", "<ButtonPress-3>")

    def place_floater_on_felt(self, event):
        if int(event.x) in bet_placement_circle and placed_bet.get() == 0:
            index_of_x = bet_placement_circle.index(int(event.x))
            top_y = bet_placement_circle[index_of_x + 1][0]
            bottom_y = bet_placement_circle[index_of_x + 1][1]
            if int(event.y) in range(bottom_y,
                                     top_y + 1):
                BetStack(self.felt, stack=sort_stack(floating_stack))
                sa.WaveObject.from_wave_file(f"sounds\\chipLay3.wav").play()
                floating_stack.clear()
                self.update_floater()
                update_bankroll()
                return
        if not event.y < upper_curve[event.x] - 200 and available_spots:
            Stack(self.felt, event.x, event.y,
                  chip=floating_stack[0].__class__(1))
            floating_stack[0].amount -= 1
            if floating_stack[0].amount <= 0:
                floating_stack.remove(floating_stack[0])
            sa.WaveObject.from_wave_file(f"sounds\\chipLay3.wav").play()
            self.update_floater()

    def place_stack_on_felt(self, event):
        if int(event.x) in bet_placement_circle and placed_bet.get() == 0:
            index_of_x = bet_placement_circle.index(int(event.x))
            top_y = bet_placement_circle[index_of_x + 1][0]
            bottom_y = bet_placement_circle[index_of_x + 1][1]
            if int(event.y) in range(bottom_y,
                                     top_y + 1):
                BetStack(self.felt, stack=sort_stack(floating_stack))
                sa.WaveObject.from_wave_file(f"sounds\\chipLay3.wav").play()
                floating_stack.clear()
                self.update_floater()
                update_bankroll()
                return
        if not event.y < upper_curve[event.x] - 200 and available_spots:
            if floater_amount == 1:
                self.place_floater_on_felt(event)
            else:
                chips_to_stack = floating_stack[0]
                floating_stack.remove(chips_to_stack)
                Stack(self.felt, event.x, event.y,
                      chip=chips_to_stack)
                sa.WaveObject.from_wave_file(f"sounds\\chipLay3.wav").play()
                self.update_floater()
                self.felt.tag_raise('floating')


# noinspection PyArgumentList
class BetStack(Stack):

    def __init__(self, felt, chip=0, stack=()):
        self.x = 1280
        self.y = 620
        super().__init__(felt, self.x, self.y, stack=stack)
        placed_bet.set(value=floater_total)
        self.felt.move(f"desc{self.x}_{self.y}", 80, 80)
        self.felt.itemconfig(f"desc{self.x}_{self.y}", state='normal')
        self.felt.tag_lower(f"desc{self.x}_{self.y}")
        allBetStacks.add(self)

    def show_desc_str(self, event):
        pass

    def hide_desc_str(self, event):
        pass

    def update_stack(self):
        total_bet = 0
        self.amount = 0
        self.value = 0
        for i in range(len(self.stack) - 1, -1, -1):
            chip = self.stack[i]
            if chip.amount > 0:
                self.amount += chip.amount
                self.value += chip.amount * chip.value
            else:
                self.stack.pop()
        if self.amount > 0:
            self.top_chip = self.stack[len(self.stack) - 1]
            self.desc_label['text'] = f"{self.value}"
            shadow_length = self.amount
            if shadow_length > 20:
                shadow_length = 20
            self.felt.itemconfig(f"shadow{self.x}_{self.y}", image=shadows[shadow_length - 1])
            self.felt.itemconfig(f"top_chip{self.x}_{self.y}", image=self.top_chip.image)
            placed_bet.set(value=self.value)
        else:
            self.felt.delete(self.tag)
            allBetStacks.remove(self)
            del self
            placed_bet.set(value=0)
        update_bankroll()

    def take_away(self):
        self.felt.delete(self.tag)
        allBetStacks.remove(self)

    def assign_binds(self):
        self.felt.tag_bind(f"top_chip{self.x}_{self.y}", "<ButtonPress-3>", self.pick_up_chip)
        self.felt.tag_bind(f"top_chip{self.x}_{self.y}", "<ButtonPress-1>", self.pick_up_stack)
        self.felt.tag_bind(f"top_chip{self.x}_{self.y}", "<Alt-ButtonPress-1>", self.put_down_one_chip)
        self.felt.tag_bind(f"top_chip{self.x}_{self.y}", "<Alt-ButtonPress-3>", self.put_down_entire_stack)

    def remove_binds(self):
        self.felt.tag_unbind(f"top_chip{self.x}_{self.y}", "<ButtonPress-3>")
        self.felt.tag_unbind(f"top_chip{self.x}_{self.y}", "<ButtonPress-1>")
        self.felt.tag_unbind(f"top_chip{self.x}_{self.y}", "<Alt-ButtonPress-1>")
        self.felt.tag_unbind(f"top_chip{self.x}_{self.y}", "<Alt-ButtonPress-3>")


# noinspection PyArgumentList
class WonStack(Stack):  # TODO: override all needed functions

    def __init__(self, felt, x=1205, y=620, chip=0, stack=()):
        self.x = x
        self.y = y
        super().__init__(felt, self.x, self.y, stack=stack)
        self.felt.move(f"desc{self.x}_{self.y}", 0, 150)
        all_stacks.add(self)
        update_bankroll()

    def update_stack(self):  # TODO: override
        self.amount = 0
        self.amount = 0
        self.value = 0
        for i in range(len(self.stack) - 1, -1, -1):
            chip = self.stack[i]
            if chip.amount > 0:
                self.amount += chip.amount
                self.value += chip.amount * chip.value
            else:
                self.stack.pop()
        if self.amount > 0:
            self.top_chip = self.stack[len(self.stack) - 1]
            self.desc_label['text'] = f"{self.value}"
            shadow_length = self.amount
            if shadow_length > 20:
                shadow_length = 20
            self.felt.itemconfig(f"shadow{self.x}_{self.y}", image=shadows[shadow_length - 1])
            self.felt.itemconfig(f"top_chip{self.x}_{self.y}", image=self.top_chip.image)
        else:
            self.felt.delete(self.tag)
            all_stacks.remove(self)
            del self


executor = concurrent.futures.ThreadPoolExecutor()
shadows = []
floating_stack = deque()
chip_stack_sounds = []
bankroll = DoubleVar
placed_bet = DoubleVar
all_stacks = set()
allBetStacks = set()
chip_collide_sounds = []
available_spots = set()

chip_handle_sounds = []
for i in range(1, 7):
    chip_stack_sounds.append(sa.WaveObject.from_wave_file(f"sounds\\chipsStack{i}.wav"))
for i in range(1, 5):
    chip_collide_sounds.append(sa.WaveObject.from_wave_file(f"sounds\\chipsCollide{i}.wav"))
for i in range(1, 6):
    chip_handle_sounds.append(sa.WaveObject.from_wave_file(f"sounds\\chipsHandle{i}.wav"))
floater_desc_label = ""
floater_desc_frame = ""
color_up_var = BooleanVar(value=False)
mainWindow = Tk
floating_stack_is_picked = False
floater_total, floater_amount = 0, 0
felt = Canvas
floating_shadow_img = 'img'
upper_curve = []
lower_curve = []
bet_placement_circle = []
chip1img = Image.open(r'graphics\stock_cards\chip1.png')
chip1imgobj = ImageTk.PhotoImage(image=chip1img)
chip2_5img = Image.open(r'graphics\stock_cards\chip2.5.png')
chip2_5imgobj = ImageTk.PhotoImage(image=chip2_5img)
chip5img = Image.open(r'graphics\stock_cards\chip5.png')
chip5imgobj = ImageTk.PhotoImage(image=chip5img)
chip10img = Image.open(r'graphics\stock_cards\chip10.png')
chip10imgobj = ImageTk.PhotoImage(image=chip10img)
chip25img = Image.open(r'graphics\stock_cards\chip25.png')
chip25imgobj = ImageTk.PhotoImage(image=chip25img)
chip50img = Image.open(r'graphics\stock_cards\chip50.png')
chip50imgobj = ImageTk.PhotoImage(image=chip50img)
chip100img = Image.open(r'graphics\stock_cards\chip100.png')
chip100imgobj = ImageTk.PhotoImage(image=chip100img)
chip500img = Image.open(r'graphics\stock_cards\chip500.png')
chip500imgobj = ImageTk.PhotoImage(image=chip500img)
chip1000img = Image.open(r'graphics\stock_cards\chip1000.png')
chip1000imgobj = ImageTk.PhotoImage(image=chip1000img)
chip2000img = Image.open(r'graphics\stock_cards\chip2000.png')
chip2000imgobj = ImageTk.PhotoImage(image=chip2000img)
chip5000img = Image.open(r'graphics\stock_cards\chip5000.png')
chip5000imgobj = ImageTk.PhotoImage(image=chip5000img)

chip_values = (Chip5000(),
               Chip2000(),
               Chip1000(),
               Chip500(),
               Chip100(),
               Chip50(),
               Chip25(),
               Chip10(),
               Chip5(),
               Chip1())

chip_hierarchy = (Chip5000,
                  Chip2000,
                  Chip1000,
                  Chip500,
                  Chip100,
                  Chip50,
                  Chip25,
                  Chip10,
                  Chip5,
                  Chip2_5,
                  Chip1)


# noinspection PyArgumentList
def take_away_bets():
    for stack in allBetStacks:
        BetStack.take_away(stack)
        chip_collide_sounds[random.randint(0, 3)].play()
        if not allBetStacks:
            break
    placed_bet.set(value=0)


# noinspection PyArgumentList
def return_closest_spot(x, y):
    if not int(x) in available_spots:
        distance = felt.winfo_width() * 2
        for spot in sorted(available_spots):
            if abs(distance) > abs(spot - x):
                distance = spot - x
            else:
                break
        x += distance
    if upper_curve[int(x)] > y:
        y = upper_curve[int(x)]
    elif y > lower_curve[int(x)]:
        y = lower_curve[int(x)]
    return x, y


# noinspection PyArgumentList
def update_bankroll():
    value = 0
    for stack in all_stacks:
        value += stack.value
    value += floater_total
    bankroll.set(value=value)


def sort_stack(stack):
    sorted_stack = deque()
    for value in chip_hierarchy:
        for chip in stack:
            if isinstance(chip, value):
                sorted_stack.append(chip)
    return sorted_stack


def find_chip_change(value):
    stack = deque()
    if value % int(value) == 0.5:
        stack.appendleft(Chip2_5(1))
        value -= 2.5
        value = int(value)
    elif value % int(value) > 0:
        stack.appendleft(Chip2_5(1))
        value -= 1.5
        value = int(value)
    for chip in chip_values:
        count = 0
        while value >= chip.value:
            count += 1
            value -= chip.value
        if count:
            stack.appendleft(chip.__class__(count))
        if 1 > value:
            break
    return sort_stack(stack)


def pay_player(player_bj, value=0):
    new_stack = deque()
    if not color_up_var.get() and not value:
        for stack in allBetStacks:
            for chip in stack.stack:
                new_stack.appendleft(chip.__class__(chip.amount))
            WonStack(felt, stack=sort_stack(new_stack))
            value += stack.value
        if player_bj:
            stack = find_chip_change(value / 2)
            WonStack(felt, x=1242, stack=sort_stack(stack))
    else:
        for stack in allBetStacks:
            if not value:
                value += stack.value
        stack = find_chip_change(value)
        WonStack(felt, stack=stack)
        if player_bj:
            stack = find_chip_change(value / 2)
            WonStack(felt, x=1242, stack=stack)
    chip_handle_sounds[random.randint(0, 4)].play()


# noinspection PyArgumentList
def update_available_spots():
    for stack in all_stacks:
        for i in range(stack.left_edge, stack.right_edge):
            available_spots.discard(i)
    if available_spots:
        i = min(available_spots)
        while i <= 39:
            available_spots.discard(i)
            i += 1
    if available_spots:
        i = max(available_spots)
        while i >= felt.winfo_width() - 39:
            available_spots.discard(i)
            i -= 1


def load_everything(impfelt: Canvas, main_window: Tk, placed_bet_var: DoubleVar, bankroll_var: DoubleVar):
    global felt, floating_shadow_img, mainWindow
    global available_spots, placed_bet, bankroll
    felt = impfelt
    mainWindow = main_window
    placed_bet = placed_bet_var
    bankroll = bankroll_var
    bet_placement_radius = 72
    for x in range(-bet_placement_radius, bet_placement_radius):
        bet_placement_circle.append(x + mainWindow.winfo_width() // 2)
        bet_placement_circle.append((int(sqrt(bet_placement_radius ** 2 - x ** 2) + mainWindow.winfo_width() // 4),
                                     int(-sqrt(bet_placement_radius ** 2 - x ** 2) + mainWindow.winfo_width() // 4)))
    highest = int(felt.winfo_height() * 790/1080)
    lowest = int(felt.winfo_height() * 558/1080)
    delta = highest - lowest
    middle = felt.winfo_width() // 2
    for i in range(0, 2564):
        upper_curve.insert(i, round((highest - (delta / middle ** 2 * (i - middle) ** 2)), 2))
    for i in range(0, 2564):
        lower_curve.insert(i, upper_curve[i] + 24)
    available_spots = set(range(40, felt.winfo_width() - 39))
    for i in range(1, 21):
        shadow_path = Image.open(f"graphics\\shadow{i}.png")
        shadow_img = ImageTk.PhotoImage(image=shadow_path)
        shadows.append(shadow_img)

    floating_shadow_path = Image.open("graphics\\floatingshadow.png")
    floating_shadow_img = ImageTk.PhotoImage(image=floating_shadow_path)

    # buyin(starting_total) TODO: Write this
    Stack(felt, felt.winfo_width() // 2,
          chip=Chip100(5))
    Stack(felt, felt.winfo_width() // 2,
          chip=Chip25(20))
    Stack(felt, felt.winfo_width() // 2,
          chip=Chip1000(20))
    update_bankroll()
