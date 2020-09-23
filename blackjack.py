try:
    import tkinter
except ImportError:
    import Tkinter as tkinter
import random
import tkinter.font as font

import winsound as PlaySound

if tkinter.TkVersion >= 8.6:  # tkinter version above 8.6 supports png files
    extension = 'png'
else:
    extension = 'ppm'

# fp_thread = threading.Thread()
hit_str = "You should hit."
dd_str = "You should double down. (Not possible yet)"
stand_str = "You should stand."
stand_obvious_str = "Are you kidding me? STAND!"
LOSE_COLOR = '#453841'  # The score digits color in case the player loses
WIN_COLOR = '#FFD800'  # The score digits color in case the player win
FELT_COLOR = '#339933'  # The color of the table felt
RESULT_BG_COLOR = "navy"  # Background color of the result label
ACTION_TIME = 24  # The time the dealer waits before the player forfeits his say
TIME_BETWEEN_ROUNDS = 10  # The time before the round is reset if the player doesn't reset it
BTN_BG = '#ffecb3'  # Standard background color for the buttons
timer_visible = False  # Set to true if the timer is displayed
PLAYERS_TURN = False  # Set to true whenever it's the player say
timer_label = None  # Holder for the timer
ROUND_IN_SESSION = False  # Set to true if cards are being dealt
RESULT_LOSE_COLOR = "#990000"  # Background color of result label if the player loses
RESULT_WIN_COLOR = 'gold'  # Background color of result label if the player wins
NAT_DELAY_TIME = 1250  # Natural delay time between result label updates
dealerstand_score = 17  # The score in which the dealer can't hit anymore
hand_is_soft = False  # True if a hand contains a soft ace (Value of 11)
dealer_hits_on_soft = True  # True if dealer can/must hit on Soft 17
kill_delays = False
deck_ready = True  # False if the deck was dealt, not shuffled
player_bj = False  # True if the player got Blackjack
cleanup = False  # True if the player left the table, breaks all timer loops
card_back_image = ''  # Handler for the cards deck back graphic
hole_card = ''  # Handler for dealer's hole card
suit_label = ''
hc_suit_label = ''
rounds_player_won = ''
rounds_dealer_won = ''
rounds_draw = ''
current_round_num = ''
player_bj_label = ''
dealer_bj_label = ''
hide_ch_button = ''
p_w_tally = 0
d_w_tally = 0
draw_tally = 0
total_rounds_tally = 0
player_bj_tally = 0
dealer_bj_tally = 0
first_card_obj = ''  # Handler for dealer's hole card label
hc_for_cheatsheet = ''  # The label that show's the dealer's hole card in the cheat sheet
is_cheatsheet_on = False  # True if the cheat sheet is currently displayed
card_frame_height = 0  # Handler for both card rows
no_of_decks = 4  # How many decks of 52 cards do you want in the main deck
no_of_backs = 0  # Number of backs pictures provided in each set
chosen_deck = 5  # The deck chosen in options by the player, assigned below
wanted_window_width = 0  # Wanted window width dependant on the chosen deck
available_decks = {  # Dictionary containing all decks assigned by:
    # (Name for filepath, no_of_backs, card_frame_height,
    # wanted_window_width)
    1: ("aqua", 13, 141, 90 * 7 + 90),
    2: ("casino", 2, 186, 130 * 7 + 90),
    3: ("newwave", 6, 126, 79 * 6 + 110),
    4: ("origin", 4, 113, 74 * 7 + 110),
    5: ("bicycle", 3, 166, 115 * 7 + 90),
    6: ("broadwalk", 1, 166, 115 * 7 + 90),
    7: ("charlie", 2, 166, 115 * 7 + 90)
}
counted = {  # Dictionary containing the cheatsheet stats
    'A': '0',
    '2': '0',
    '3': '0',
    '4': '0',
    '5': '0',
    '6': '0',
    '7': '0',
    '8': '0',
    '9': '0',
    '10': '0',
    'J': '0',
    'Q': '0',
    'K': '0'
}

basic_strategy = {1: {
    False: {  # If the hand is not soft
        hit_str: [
            (4, 5, 6, 7, 8, [2, 3, 4, 7, 8, 9, 10, 11]),
            (9, [7, 8, 9, 10, 11]),
            (10, [10, 11]),
            (12, [2, 3, 7, 8, 9, 10, 11]),
            (13, 14, 15, [7, 8, 9, 10, 11]),
            (16, [7, 8, 9, 10, 11]),
        ],
        dd_str: [
            (4, 5, 6, 7, 8, [5, 6]),
            (9, [2, 3, 4, 5, 6]),
            (10, [2, 3, 4, 5, 6, 7, 8, 9]),
            (11, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        ],
        stand_str: [
            (12, [4, 5, 6]),
            (13, 14, 15, [2, 3, 4, 5, 6]),
            (16, [2, 3, 4, 5, 6]),
            (17, 18, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        ],
        stand_obvious_str: [
            (19, 20, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11])]
    },
    True: {hit_str: [  # If the hand is no longer soft
        (12, [2, 3, 7, 8, 9, 10, 11]),
        (13, 14, 15, 16, [2, 3, 7, 8, 9, 10, 11]),
        (17, [7, 8, 9, 10, 11]),
        (18, [9, 10, 11])
    ],
        dd_str: [
            (13, 14, 15, 16, [4, 5, 6]),
            (17, [2, 3, 4, 5, 6]),
            (18, [3, 4, 5, 6]),
            (19, [6])
        ],
        stand_str: [
            (12, [4, 5, 6]),
            (18, [2, 7, 8])
        ],
        stand_obvious_str: [
            (19, 20, [2, 3, 4, 5, 7, 8, 9, 10, 11])
        ]
    }
},
    2: {
        False: {  # If the hand is not soft
            hit_str: [
                (4, 5, 6, 7, 8, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
                (9, [7, 8, 9, 10, 11]),
                (10, [10, 11]),
                (12, [2, 3, 7, 8, 9, 10, 11]),
                (13, 14, 15, [7, 8, 9, 10, 11]),
                (16, [7, 8, 9, 10, 11]),
            ],
            dd_str: [
                (9, [2, 3, 4, 5, 6]),
                (10, [2, 3, 4, 5, 6, 7, 8, 9]),
                (11, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
            ],
            stand_str: [
                (12, [4, 5, 6]),
                (13, 14, 15, [2, 3, 4, 5, 6]),
                (16, [2, 3, 4, 5, 6]),
                (17, 18, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
            ],
            stand_obvious_str: [
                (19, 20, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11])]
        },
        True: {hit_str: [  # If the hand is no longer soft
            (12, [2, 3, 7, 8, 9, 10, 11]),
            (13, [2, 3, 4, 7, 8, 9, 10, 11]),
            (14, [2, 3, 7, 8, 9, 10, 11]),
            (15, 16, [2, 3, 7, 8, 9, 10, 11]),
            (17, [7, 8, 9, 10, 11]),
            (18, [9, 10, 11])
        ],
            dd_str: [
                (13, [5, 6]),
                (14, [4, 5, 6]),
                (15, 16, [4, 5, 6]),
                (17, [2, 3, 4, 5, 6]),
                (18, [3, 4, 5, 6]),
                (19, [6])
            ],
            stand_str: [
                (12, [4, 5, 6]),
                (18, [2, 7, 8])
            ],
            stand_obvious_str: [
                (19, 20, [2, 3, 4, 5, 7, 8, 9, 10, 11])
            ]
        }
    },
    4: {
        False: {  # If the hand is not soft
            hit_str: [
                (4, 5, 6, 7, 8, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
                (9, [2, 7, 8, 9, 10, 11]),
                (10, [10, 11]),
                (12, [2, 3, 7, 8, 9, 10, 11]),
                (13, 14, 15, 16, [7, 8, 9, 10, 11])
            ],
            dd_str: [
                (9, [3, 4, 5, 6]),
                (10, [2, 3, 4, 5, 6, 7, 8, 9]),
                (11, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
            ],
            stand_str: [
                (12, [4, 5, 6]),
                (13, 14, 15, 16, [2, 3, 4, 5, 6]),
                (17, 18, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
            ],
            stand_obvious_str: [
                (19, 20, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11])]
        },
        True: {hit_str: [  # If the hand is no longer soft
            (12, [2, 3, 7, 8, 9, 10, 11]),
            (13, [2, 3, 4, 7, 8, 9, 10, 11]),
            (14, [2, 3, 7, 8, 9, 10, 11]),
            (15, 16, [2, 3, 7, 8, 9, 10, 11]),
            (17, [2, 7, 8, 9, 10, 11]),
            (18, [9, 10, 11])
        ],
            dd_str: [
                (13, [5, 6]),
                (14, [4, 5, 6]),
                (15, 16, [4, 5, 6]),
                (17, [3, 4, 5, 6]),
                (18, [3, 4, 5, 6]),
                (19, [6])
            ],
            stand_str: [
                (12, [4, 5, 6]),
                (18, [2, 7, 8])
            ],
            stand_obvious_str: [
                (19, 20, [2, 3, 4, 5, 7, 8, 9, 10, 11])
            ]
        }
    }
}


def disable_buttons():
    stand_button['state'] = bas_strat_button['state'] = 'disabled'
    new_game['state'] = hit_button['state'] = 'disabled'


# = leave_button['state'] = ch_button['state'] \


def load_chosen_set(card_images):
    global no_of_backs
    global card_frame_height
    global wanted_window_width
    no_of_backs = available_decks[chosen_deck][1]
    card_frame_height = available_decks[chosen_deck][2]
    wanted_window_width = available_decks[chosen_deck][3]
    suits = {'H': '♥', 'C': '♣', 'D': '♦', 'S': '♠'}
    card_names = {
        1: 'A',
        2: '2',
        3: '3',
        4: '4',
        5: '5',
        6: '6',
        7: '7',
        8: '8',
        9: '9',
        10: '10',
        11: 'J',
        12: 'Q',
        13: 'K'}

    for suit in suits:
        for card in range(1, 10):
            name = 'decks\\{}\\{}0{}.{}'.format(available_decks[chosen_deck][0], suit, str(card), extension)
            image = tkinter.PhotoImage(file=name)
            card_images.append({0: card, 1: image, 2: suits[suit], 3: card_names[card].upper(), 4: False})

        for card in range(10, 14):
            name = 'decks\\{}\\{}{}.{}'.format(available_decks[chosen_deck][0], suit, str(card), extension)
            image = tkinter.PhotoImage(file=name)
            card_images.append({0: 10, 1: image, 2: suits[suit], 3: card_names[card].upper(), 4: False})


def load_back_of_card():
    global card_back_image
    card_back_image = tkinter.PhotoImage(
        file="decks\\{}\\back{}.{}".format(
            available_decks[chosen_deck][0],
            random.randint(1, no_of_backs),
            extension))


def check_basic_strategy():
    global basic_strategy
    for item in basic_strategy[no_decks_for_BS][hand_is_soft]:
        for n_pscore in basic_strategy[no_decks_for_BS][hand_is_soft][item]:
            if player_score_label.get() in n_pscore:
                if dealer_score_label.get() in n_pscore[len(n_pscore) - 1]:
                    if timer_visible:
                        result_text.set(item)
                        if item == hit_str:
                            PlaySound.PlaySound("sounds\\hint_hit.wav",
                                                PlaySound.SND_FILENAME
                                                + PlaySound.SND_ASYNC)
                            flash_bg_fg_widgets(6, 'white', '#bf40bf', hit_button)
                        elif item == dd_str:
                            PlaySound.PlaySound("sounds\\hint_dd",
                                                PlaySound.SND_FILENAME
                                                + PlaySound.SND_ASYNC)
                            flash_bg_fg_widgets(6, 'white', '#bf40bf', hit_button)
                        else:
                            PlaySound.PlaySound("sounds\\hint_stand.wav",
                                                PlaySound.SND_FILENAME
                                                + PlaySound.SND_ASYNC)
                            flash_bg_fg_widgets(6, 'white', '#bf40bf', stand_button)
                    return item


def enable_buttons():
    if ROUND_IN_SESSION:
        stand_button['state'] = hit_button['state'] = 'normal'
        leave_button['state'] = ch_button['state'] = 'normal'
        new_game['state'] = 'disabled'
        bas_strat_button['state'] = 'normal'
    else:
        stand_button['state'] = hit_button['state'] = 'disabled'
        leave_button['state'] = ch_button['state'] = 'normal'
        new_game['state'] = bas_strat_button['state'] = 'normal'


def invert_color(item, color):  # Invert color
    if type(color) == str:
        rgb = item.winfo_rgb(color)
    else:
        rgb = color
    rgb = (65535 - rgb[0], 65535 - rgb[1], 65535 - rgb[2])
    tk_rgb = "#%04x%04x%04x" % rgb
    return tk_rgb


def working_dots():  # TODO: Requires Threading
    """
    Creates the cool process bar like dots on the big button.
    Lasts 2.75 seconds while sounds are playing.
    :return:
    """
    hit_button['text'] = hit_button['text'] + '\n'
    for i in range(1, 12):
        hit_button['text'] = hit_button['text'] + '.'
        create_delay(250)


def show_stats_sheet():
    global is_cheatsheet_on
    ch_button['text'] = "Hide\nStats Sheet"
    ch_button['command'] = hide_stats_sheet
    is_cheatsheet_on = True
    mainWindow.update()
    secondWindow.update()
    secondWindow.deiconify()


def hide_stats_sheet():
    global is_cheatsheet_on
    secondWindow.withdraw()
    is_cheatsheet_on = False
    ch_button['text'] = "Show\nStats Sheet"
    ch_button['command'] = show_stats_sheet
    mainWindow.update()


def reset_hitnstand_button():
    hit_button['text'] = 'HIT'
    stand_button['text'] = 'STAND'


def move_to_discard_pile():
    for i in range(len(deck) - 1, -1, -1):
        if deck[i][4]:
            deck[i][4] = False
            discard_pile.append(deck[i])
            deck.pop(i)


def clear_table():
    global dealer_card_frame
    global player_card_frame
    global player_bj
    global dealer_hand
    global player_hand
    dealer_hand = []
    player_hand = []
    player_bj = False
    move_to_discard_pile()
    reset_hitnstand_button()
    player_score_label.set(0)
    dealer_score_label.set(0)
    result['bg'] = RESULT_BG_COLOR
    result['fg'] = 'white'
    dealer_score_no['fg'] = 'white'
    player_score_no['fg'] = 'white'
    dealer_score_no["font"] = font.Font(size=18)
    player_score_no["font"] = font.Font(size=18)
    result_text.set("🂡🂫 Welcome to the BLACKJACK table! 🂫🂡")
    print("Clearing the table...")
    hit_button['text'] = 'Clearing\nthe Table'
    # working_dots()  TODO: THREAD THIS
    while player_card_frame.winfo_children() or dealer_card_frame.winfo_children():
        if len(player_card_frame.winfo_children()) >= len(dealer_card_frame.winfo_children()):
            player_card_frame.winfo_children()[len(player_card_frame.winfo_children()) - 1].destroy()
        else:
            dealer_card_frame.winfo_children()[len(dealer_card_frame.winfo_children()) - 1].destroy()
        PlaySound.PlaySound('sounds\\cardSlide1.wav', PlaySound.SND_FILENAME
                            + PlaySound.SND_ASYNC)
        create_delay(400)
    bas_strat_button['text'] = "Check Basic\nStrategy"
    bas_strat_button['command'] = check_basic_strategy
    disable_buttons()


def create_delay(delay_time):  # TODO: Requires Threading
    for i in range(1, int(delay_time / 10) + 1):
        if cleanup or kill_delays:
            return
        mainWindow.after(10, mainWindow.update())


def new_round_timer():  # TODO: Requires Threading
    seconds = TIME_BETWEEN_ROUNDS
    hit_button['text'] = "Next Round\nwill begin\nshortly.\n{}" \
        .format(seconds)
    mainWindow.update()
    for i in range(seconds, 0, -1):
        if cleanup:
            return
        # Beep in the last 3 seconds
        hit_button['text'] = "Next Round\nwill begin\nshortly.\n{}" \
            .format(i)
        hit_button.update()
        if not ROUND_IN_SESSION and i <= 3:
            PlaySound.Beep(2400 - i * 300, 150)
            create_delay(850)
        elif i > 3:
            create_delay(1000)
        elif ROUND_IN_SESSION:
            return

    if not ROUND_IN_SESSION:
        new_round()


def hide_action_timer():
    global timer_label
    global timer_visible
    if not cleanup:
        timer_label.destroy()
        timer_label.update()
        timer_visible = False


def reset_action_timer():  # TODO: Requires Threading
    global timer_label
    global timer_visible
    timer_visible = True
    enable_buttons()
    seconds = ACTION_TIME
    timer_bg = tkinter.PhotoImage(file="graphics\\{}.png".format(seconds))
    timer_label = tkinter.Label(player_card_frame, image=timer_bg,
                                bg=FELT_COLOR)
    timer_label.pack(side='left')
    timer_label.pack()
    mainWindow.update()
    while seconds > 0 and timer_visible:
        if cleanup:
            return
        timer_bg.config(file="graphics\\{}.png".format(seconds))
        create_delay(1000)
        seconds -= 1
        # if seconds == 12:
        #     PlaySound.PlaySound('sounds\\hurry_up.wav',
        #                         PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        # if seconds <= 5:
        #     PlaySound.PlaySound('sounds\\{}.wav'.format(seconds),
        #                         PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        if not timer_visible:
            print("Action time BROKEN, if this is displayed in mass at"
                  " the end of the application, it's BAD.\nIt means that"
                  "the game is creating new instances of the timer and"
                  "deal functions\nand keeps the old instances in the stack,"
                  "without killing them off, for no apparent reason.\n"
                  "THIS MUST BE FIXED SOMEHOW!\n"
                  "THEY ALL NEED TO RUN ASYNCHRONOUSLY AND DIE SEPARATELY!")  # TODO: FIX THIS!
            return
    if not cleanup:
        if PLAYERS_TURN and seconds <= 0:
            disable_buttons()
            mainWindow.update()
            hide_action_timer()
        if check_basic_strategy() == hit_str or check_basic_strategy() == dd_str:
            deal_player()
        else:
            deal_dealer()


def reset_counted():
    global counted
    counted = {
        'A': '0',
        '2': '0',
        '3': '0',
        '4': '0',
        '5': '0',
        '6': '0',
        '7': '0',
        '8': '0',
        '9': '0',
        '10': '0',
        'J': '0',
        'Q': '0',
        'K': '0'
    }
    for card in deck:
        if not card[4]:
            counted[card[3]] = str(int(counted[card[3]]) + 1)

    row_counter = 0
    for key, value in counted.items():
        cheats_frame.winfo_children()[row_counter]['text'] = "{:<3} : {:>3}".format(key, value)
        row_counter += 1
    if is_cheatsheet_on:
        secondWindow.update()
    total = 0
    for value in counted.values():
        total += int(value)
    cheats_frame.winfo_children()[row_counter]['text'] = "{} left in the deck.".format(total)
    if not is_deck_empty():
        suit_label['text'] = '{}{}'.format(deck[0][3], deck[0][2])
        if deck[0][2] in '♥♦':
            suit_label['fg'] = "red"
        else:
            suit_label['fg'] = "black"
        if is_cheatsheet_on:
            secondWindow.update()


def init_stats_sheet():
    global suit_label
    global hc_for_cheatsheet
    global hc_suit_label
    global hide_ch_button
    global rounds_player_won
    global rounds_dealer_won
    global rounds_draw
    global current_round_num
    global player_bj_label
    global dealer_bj_label
    row_counter = 0
    for key, value in counted.items():
        tkinter.Label(cheats_frame, text="{:<3} : {:>3}".format(key, value),
                      background=RESULT_WIN_COLOR) \
            .grid(column=0, row=row_counter, sticky='nw')
        if is_cheatsheet_on:
            secondWindow.update()
        row_counter += 1
    total = 0
    for value in counted.values():
        total += int(value)
    tkinter.Label(cheats_frame, text="{} left in the deck.".format(total),
                  background=RESULT_WIN_COLOR) \
        .grid(column=0, row=row_counter, sticky='nw')
    row_counter += 1
    tkinter.Label(cheats_frame, text="Top card in the deck is: ",
                  background=RESULT_WIN_COLOR) \
        .grid(column=0, row=row_counter, sticky='nw')
    suit_label = tkinter.Label(cheats_frame,
                               text="{}{}".format(deck[0][3], deck[0][2]),
                               background=RESULT_WIN_COLOR)
    suit_label.grid(column=1, row=row_counter, sticky='nw')
    if deck[0][2] in '♥♦':
        suit_label['fg'] = "red"
    else:
        suit_label['fg'] = "black"
    hc_for_cheatsheet = tkinter.Label(
        cheats_frame, text="",
        background=RESULT_WIN_COLOR)
    row_counter += 1
    hc_for_cheatsheet.grid(column=0, row=row_counter, sticky='nw')
    hc_suit_label = tkinter.Label(cheats_frame, text="",
                                  background=RESULT_WIN_COLOR)
    hc_suit_label.grid(column=1, row=row_counter,
                       sticky='nw')
    if is_cheatsheet_on:
        secondWindow.update()

    hide_ch_button = tkinter.Button(stats_frame,
                                    text='Show me more',
                                    bg='black', fg='white',
                                    command=show_count)
    hide_ch_button.grid(row=0, column=0, columnspan=2, sticky='w')
    current_round_num = tkinter.Label(stats_frame, text='Round #1',
                                      fg='white', bg='navy', font=boldFont)
    current_round_num.grid(row=1, column=0, sticky='w')
    rounds_player_won = tkinter.Label(stats_frame, text='Rounds won:',
                                      fg='white', bg='navy')
    rounds_player_won.grid(row=2, column=0, sticky='w')
    rounds_dealer_won = tkinter.Label(stats_frame, text='Rounds lost:',
                                      fg='white', bg='navy')
    rounds_dealer_won.grid(row=3, column=0, sticky='w')
    rounds_draw = tkinter.Label(stats_frame, text='Rounds Draw:',
                                fg='white', bg='navy')
    rounds_draw.grid(row=4, column=0, sticky='w')
    player_bj_label = tkinter.Label(stats_frame, text='Player BLACKJACKS:',
                                    fg='white', bg='navy')
    player_bj_label.grid(row=5, column=0, sticky='w')
    dealer_bj_label = tkinter.Label(stats_frame, text='Dealer BLACKJACKS:',
                                    fg='white', bg='navy')
    dealer_bj_label.grid(row=6, column=0, sticky='w')
    secondWindow.update()
    secondWindow.maxsize(220, stats_frame.winfo_height())
    secondWindow.minsize(220, stats_frame.winfo_height())


def update_bj_stats():
    global dealer_bj_label, player_bj_label
    dealer_bj_label['text'] = "Dealer BLACKJACKS:\t{0}, {1:>3.2f}%". \
        format(dealer_bj_tally, dealer_bj_tally * 100 / total_rounds_tally)
    dealer_bj_label.update()
    player_bj_label['text'] = "Player BLACKJACKS:\t{0}, {1:>3.2f}%". \
        format(player_bj_tally, player_bj_tally * 100 / total_rounds_tally)
    player_bj_label.update()


def show_count():
    global hide_ch_button
    secondWindow.minsize(220, stats_frame.winfo_height() + cheats_frame.winfo_height())
    secondWindow.maxsize(220, stats_frame.winfo_height() + cheats_frame.winfo_height())
    hide_ch_button['text'] = "I'm no cheater!"
    hide_ch_button['command'] = hide_count
    secondWindow.update()


def hide_count():
    global hide_ch_button
    secondWindow.minsize(220, stats_frame.winfo_height())
    secondWindow.maxsize(220, stats_frame.winfo_height())
    hide_ch_button['text'] = "Show me more"
    hide_ch_button['command'] = show_count
    secondWindow.update()


def new_round():
    global deck
    global hand_is_soft
    global deck_ready
    global ROUND_IN_SESSION
    # if nrt.is_alive():
    #     nrt.join()
    #     print("------------------NRT KILLED----------")
    if not cleanup:
        ROUND_IN_SESSION = True
        hand_is_soft = False
        disable_buttons()
        bas_strat_button['command'] = check_basic_strategy
        deck_ready = False
        if is_cheatsheet_on:
            secondWindow.update()
        clear_table()
        print("New round commencing. Dealing cards.")
        # Deal first cards
        first_play()
        # fp_thread.run()


def is_deck_empty():
    """
        go through the deck and see if the 4th index of all the cards
        (a boolean that is true if the card was already dealt) is true.
        If so, that means that all the cards were dealt and
        a new deck is made from the discard pile (all the cards that
        were already dealt and are not in this current round).
        As soon as the first undealt card is found (4th index is
        false) deck_is_empty is made false, and the loop is broken
        to stop looking for more undealt cards.
    :return:
    """
    for card in deck:
        if not card[4]:
            return False
    return True


def refill_deck_if_empty():
    if is_deck_empty():
        disable_buttons()
        create_delay(500)
        random.shuffle(discard_pile)
        for card in discard_pile:
            deck.insert(0, card)
        discard_pile.clear()
        reset_hitnstand_button()
        tempstr = result['text']
        result_text.set('Deck has emptied! Shuffling the discard pile.')
        hit_button['text'] = 'Shuffling'
        PlaySound.PlaySound('sounds\\shufflemachine.wav',
                            PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        working_dots()
        hit_button['text'] = 'Shuffling'
        working_dots()
        result_text.set(tempstr)
        reset_counted()
        reset_hitnstand_button()
        if is_cheatsheet_on:
            secondWindow.update()
        if PLAYERS_TURN:
            enable_buttons()
        mainWindow.update()


def stats_sheet(card):
    global hc_for_cheatsheet
    counted[card[3]] = str(int(counted[card[3]]) - 1)
    row_counter = 0
    for key, value in counted.items():
        cheats_frame.winfo_children()[row_counter]['text'] = "{:<3} : {:>3}".format(key, value)
        row_counter += 1
    if is_cheatsheet_on:
        secondWindow.update()
    total = 0
    for value in counted.values():
        total += int(value)
    cheats_frame.winfo_children()[row_counter]['text'] = "{} left in the deck.".format(total)
    if not is_deck_empty():
        suit_label['text'] = '{}{}'.format(deck[0][3], deck[0][2])
        if deck[0][2] in '♥♦':
            suit_label['fg'] = "red"
        else:
            suit_label['fg'] = "black"
        if is_cheatsheet_on:
            secondWindow.update()


def deal_card(frame, hand):
    # pop the next card off the top of the deck
    next_card = deck.pop(0)
    next_card[4] = True
    deck.append(next_card)
    # add the image to a label and display the label
    PlaySound.PlaySound('sounds\\cardPlace{}.wav'.format(random.randint(1, 13)),
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    create_delay(70)
    card_obj = tkinter.Label(frame, image=next_card[1], borderwidth=0,
                             relief='raised', fg='white', background=FELT_COLOR)
    card_obj.pack(side='left', padx=(1, 3), pady=(1, 3))
    card_obj.pack_propagate(0)
    # create_delay(180)
    update_notif(hand, next_card)
    # now return the card's face value
    return next_card


def score_hand(hand):
    # Calculate the total score of all cards in the list.
    # Only one ace can have a value 11, and this will be reduced to 1 if
    # the hand is a bust.
    score = 0
    global hand_is_soft
    ace = False
    for next_card in hand:
        card_value = next_card[0]
        if card_value == 1 and not ace:
            ace = True
            card_value = 11
            hand_is_soft = True  # The hand becomes a soft one.
        score += card_value
        # if we would bust, check if there's a soft ace and subtract 10
        if score > 21 and ace:
            score -= 10
            hand_is_soft = False
            if "Ace will be counted as 1." not in result_text.get():
                result_text.set('{} {}'.format(result_text.get(), "Ace will be counted as 1."))
            ace = False  # The hand returns to being hard, since the ace is technically no longer an "Ace"
    return score


def flip_hole_card():
    global hc_for_cheatsheet
    global dealer_bj_tally
    dealer_hand.append(hole_card)
    hc_for_cheatsheet['text'] = ''
    hc_suit_label['text'] = ''
    PlaySound.PlaySound('sounds\\cardFlip.wav',
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    create_delay(300)
    first_card_obj['image'] = hole_card[1]
    if hole_card[0] == 1:
        result_text.set("Dealer's hole card was the {}{}. Value of 11."
                        .format(hole_card[3], hole_card[2]))
    else:
        result_text.set("Dealer's hole card was the {}{}. Value of {}."
                        .format(hole_card[3], hole_card[2], hole_card[0]))
    dealer_score = score_hand(dealer_hand)
    print("{} Current score - {}.".format(result_text.get(), dealer_score))
    dealer_score_label.set(dealer_score)


def check_for_ace(hand):
    count = 0
    for card in hand:
        if card[0] == 1:
            count += 1
    return count


def deal_dealer():
    global ROUND_IN_SESSION
    global PLAYERS_TURN
    global hand_is_soft
    global timer_strvar
    global timer_visible
    PLAYERS_TURN = False
    hand_is_soft = False
    global dealer_bj_tally
    if timer_visible:
        hide_action_timer()
    disable_buttons()
    if not player_bj:
        print("Player chose to stand on {}. Dealer's turn.".format(player_score_label.get()))
        flip_hole_card()
        if check_for_bj(dealer_hand, dealer_score_label.get()):
            dealer_bj_tally += 1
        update_bj_stats()
    dealer_score = score_hand(dealer_hand)
    create_delay(NAT_DELAY_TIME)
    compare_scores(player_score_label.get(), dealer_score)
    while 0 < dealer_score <= dealerstand_score and ROUND_IN_SESSION and not cleanup:
        next_card = deal_card(dealer_card_frame, dealer_hand)
        dealer_hand.append(next_card)
        dealer_score = score_hand(dealer_hand)
        dealer_score_label.set(dealer_score)
        if len(dealer_hand) == 2:
            if check_for_bj(dealer_hand, dealer_score):
                dealer_bj_tally += 1
            update_bj_stats()
        print("{} Current score - {}.".format(result_text.get(), dealer_score))
        stats_sheet(next_card)
        create_delay(NAT_DELAY_TIME)
        compare_scores(player_score_label.get(), dealer_score)


def compare_scores(player_score, dealer_score):
    global ROUND_IN_SESSION
    global total_rounds_tally
    # global fp_thread
    # if nrt.is_alive():
    #     nrt.join()
    if check_for_bj(dealer_hand, dealer_score):
        ROUND_IN_SESSION = False
        if not player_bj and not player_score == 21:
            result_text.set("Blackjack! Dealer wins! Better luck next round!")
            flash_bg_fg_widgets(6, RESULT_LOSE_COLOR, 'black', result, hit_button, stand_button,
                                bas_strat_button, new_game, leave_button, ch_button,
                                style='wavy', hand='dealer')
            player_lost()
        else:
            result_text.set("Dealer got 21 by BLACKJACK as well!")
            flash_bg_fg_widgets(6, RESULT_LOSE_COLOR, 'black', result, hit_button, stand_button,
                                bas_strat_button, new_game, leave_button, ch_button,
                                style='wavy', hand='dealer')
            dealer_score_no['fg'] = player_score_no['fg'] = WIN_COLOR
            dealer_score_no["font"] = font.Font(size=21, weight='bold')
            player_score_no["font"] = font.Font(size=21, weight='bold')
            sound_draw()
    if dealer_score == 21 and len(dealer_hand) > 2:
        ROUND_IN_SESSION = False
        result_text.set("Dealer reached 21!")
        create_delay(NAT_DELAY_TIME)
    if 21 > dealer_score >= dealerstand_score:
        ROUND_IN_SESSION = False
        if dealer_score == dealerstand_score:
            if dealer_hits_on_soft and hand_is_soft:
                result_text.set("Soft {}. Dealer must and will keep hitting.".format(dealerstand_score))
                print(result_text.get())
                create_delay(NAT_DELAY_TIME)
                ROUND_IN_SESSION = True
            else:
                result_text.set("Hard {}. Dealer must and will stand.".format(dealerstand_score))
                print("The Dealer's final score is {}.".format(dealer_score))
                create_delay(NAT_DELAY_TIME)
        else:
            result_text.set("Dealer must and will stand on or above hard {}.".format(dealerstand_score))
            print("The Dealer's final score is {}.".format(dealer_score))
            create_delay(NAT_DELAY_TIME)
    if dealer_score > 21:
        ROUND_IN_SESSION = False
    if ROUND_IN_SESSION:
        refill_deck_if_empty()
    else:
        if not check_for_bj(dealer_hand, dealer_score):
            if dealer_score > 21:
                result_text.set("Too many! Dealer busts! Player wins!")
                player_won()
            elif dealer_score < player_score:
                result_text.set("Player wins!")
                player_won()
            elif dealer_score > player_score:
                result_text.set("Dealer wins! Better luck next round!")
                player_lost()
            else:
                result_text.set("Draw!")
                dealer_score_no['fg'] = player_score_no['fg'] = WIN_COLOR
                dealer_score_no["font"] = font.Font(size=21, weight='bold')
                player_score_no["font"] = font.Font(size=21, weight='bold')
                sound_draw()
        print("{} The score was {} - {}.".format(
            result_text.get(), player_score, dealer_score))
        refill_deck_if_empty()
        enable_buttons()
        reset_shuffle_btn()
        reset_hitnstand_button()
        # fp_thread.join()
        new_round_timer()


def reset_shuffle_btn():
    bas_strat_button['command'] = shuffle
    bas_strat_button['text'] = "Shuffle and\nDeal Next Round"
    mainWindow.update()


def check_for_bj(hand, score):
    if score == 21 and len(hand) == 2:
        return True
    else:
        return False


def update_notif(whos_hand, next_card):
    if whos_hand == player_hand:
        name = "You were dealt"
    else:
        name = "Dealer drew"

    if next_card[0] == 1:
        if check_for_ace(whos_hand) >= 1:
            result_text.set("{} the {}{}. Value of 1."
                            .format(name, next_card[3], next_card[2]))
        else:
            result_text.set("{} the {}{}. Value of {}."
                            .format(name, next_card[3], next_card[2], 11))
    else:
        result_text.set("{} the {}{}. Value of {}."
                        .format(name, next_card[3], next_card[2], next_card[0]))


def deal_player():
    global player_bj
    global player_bj_tally
    global player_bj_label
    global ROUND_IN_SESSION
    global PLAYERS_TURN
    global dealer_bj_tally
    global timer_visible
    # if rat.is_alive():
    #     rat.join()
    # if nrt.is_alive():
    #     nrt.join()
    if PLAYERS_TURN and timer_visible:
        hide_action_timer()
    next_card = deal_card(player_card_frame, player_hand)
    player_hand.append(next_card)
    player_score = score_hand(player_hand)
    player_score_label.set(player_score)
    create_delay(180)
    print("{} Current score - {}.".format(result_text.get(), player_score))
    stats_sheet(next_card)
    player_bj = check_for_bj(player_hand, player_score)
    if player_bj:
        result_text.set("Winner winner, chicken dinner! BLACKJACK! Dealer will now try to match.")
        print(result_text.get())
        player_bj_tally += 1
        player_bj_label['text'] = "Player BLACKJACKS:\t{0}, {1:>3.2f}%" \
            .format(player_bj_tally, player_bj_tally * 100 / total_rounds_tally)
        player_bj_label.update()
        secondWindow.update()
        hit_button['text'] = 'BLACK'
        stand_button['text'] = 'JACK'
        flash_bg_fg_widgets(6, '#bf40bf', 'white', result, hit_button, stand_button,
                            bas_strat_button, new_game, leave_button, ch_button,
                            style='wavy', hand='player')
        PlaySound.PlaySound('sounds\\congratulations.wav',
                            PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        disable_buttons()
        player_score_no['fg'] = WIN_COLOR
        create_delay(300)
        refill_deck_if_empty()
        deal_dealer()
    else:
        if len(player_hand) == 2:
            player_bj_label['text'] = "Player BLACKJACKS:\t{0}, {1:>3.2f}%" \
                .format(player_bj_tally, player_bj_tally * 100 / total_rounds_tally)
            player_bj_label.update()
        if player_score == 21:
            disable_buttons()
            PLAYERS_TURN = False
            create_delay(NAT_DELAY_TIME)
            result_text.set("21! Congratulations! Dealer will now try to match.")
            print(result_text.get())
            hit_button['text'] = '2'
            stand_button['text'] = '1'
            player_score_no['fg'] = WIN_COLOR
            create_delay(NAT_DELAY_TIME)
            refill_deck_if_empty()
            deal_dealer()
        elif player_score > 21:  # To disable buttons before all delays
            disable_buttons()
            create_delay(NAT_DELAY_TIME)
            ROUND_IN_SESSION = False
            PLAYERS_TURN = False
            reset_shuffle_btn()
            result_text.set("Player busts! Dealer wins! Better luck next round!")
            print(result_text.get())
            player_lost()
            create_delay(NAT_DELAY_TIME)
            update_stats()
            flip_hole_card()
            if check_for_bj(dealer_hand, dealer_score_label.get()):
                dealer_bj_tally += 1
                flash_bg_fg_widgets(6, RESULT_LOSE_COLOR, 'black', result, hit_button, stand_button,
                                    bas_strat_button, new_game, leave_button, ch_button,
                                    style='wavy', hand='dealer')
                result_text.set("Dealer was holding BLACKJACK!")
                update_bj_stats()
                create_delay(NAT_DELAY_TIME)
            else:
                update_bj_stats()
            reset_hitnstand_button()
            refill_deck_if_empty()
            enable_buttons()
            # fp_thread.join()
            new_round_timer()
        refill_deck_if_empty()
        if PLAYERS_TURN:
            reset_action_timer()

    create_delay(NAT_DELAY_TIME)


def player_won():
    global p_w_tally
    global rounds_player_won
    mainWindow.update()
    p_w_tally += 1
    update_stats()
    dealer_score_no['fg'] = LOSE_COLOR
    result['bg'] = RESULT_WIN_COLOR
    # mainWindow.config(background=result['bg'])
    result['fg'] = 'navy'
    player_score_no["font"] = font.Font(size=21, weight='bold')
    player_score_no['fg'] = WIN_COLOR
    PlaySound.PlaySound('sounds\\win_.wav', PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    mainWindow.update()
    create_delay(NAT_DELAY_TIME)


def update_stats():
    rounds_dealer_won['text'] = "Rounds lost:\t\t{0}, {1:>3.2f}%" \
        .format(d_w_tally, d_w_tally * 100 / total_rounds_tally)
    rounds_player_won['text'] = "Rounds won:\t\t{0}, {1:>3.2f}%" \
        .format(p_w_tally, p_w_tally * 100 / total_rounds_tally)
    rounds_draw['text'] = "Rounds Draw:\t\t{}, {:>3.2f}%" \
        .format(draw_tally, draw_tally * 100 / total_rounds_tally)
    # dealer_bj_label['text'] = "Dealer BLACKJACKS:\t{0}, {1:>3.2f}%". \
    #     format(dealer_bj_tally, dealer_bj_tally * 100 / total_rounds_tally)
    # player_bj_label['text'] = "Player BLACKJACKS:\t{0}, {1:>3.2f}%" \
    #     .format(player_bj_tally, player_bj_tally * 100 / total_rounds_tally)
    secondWindow.update()


def player_lost():
    global d_w_tally
    global rounds_dealer_won
    mainWindow.update()
    d_w_tally += 1
    update_stats()
    result['bg'] = RESULT_LOSE_COLOR
    # mainWindow.config(background=result['bg'])
    dealer_score_no["font"] = font.Font(size=21, weight='bold')
    dealer_score_no['fg'] = WIN_COLOR
    player_score_no['fg'] = LOSE_COLOR
    PlaySound.PlaySound('sounds\\you_lose.wav', PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    disable_buttons()
    mainWindow.update()
    create_delay(NAT_DELAY_TIME)


def sound_draw():
    global draw_tally
    global rounds_draw
    draw_tally += 1
    update_stats()
    PlaySound.PlaySound('sounds\\draw.wav', PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    mainWindow.update()


def first_play():
    global dealer_hand
    global player_hand
    global deck_ready
    global PLAYERS_TURN
    global player_score_label
    global dealer_score_label
    global hole_card
    global hc_for_cheatsheet
    global hc_suit_label
    global first_card_obj
    global total_rounds_tally
    if not cleanup:
        total_rounds_tally += 1
        current_round_num['text'] = "Round #{}".format(total_rounds_tally)
        PlaySound.PlaySound("sounds\\ready.wav", PlaySound.SND_FILENAME)
        create_delay(300)
        player_hand = []
        dealer_hand = []
        deck_ready = False
        load_back_of_card()
        hit_button['text'] = "Dealing\nFirst cards"
        deal_player()
        next_card = deal_card(dealer_card_frame, dealer_hand)
        dealer_hand.append(next_card)
        if next_card[0] == 1:
            dealer_score_label.set(11)
        else:
            dealer_score_label.set(next_card[0])
        print("{} Current score - {}.".format(result_text.get(), dealer_score_label.get()))
        # result_text.set("Dealer drew the {}{}. With a value of {}."
        #                 .format(next_card[3], next_card[2], next_card[0]))
        stats_sheet(next_card)
        refill_deck_if_empty()
        create_delay(NAT_DELAY_TIME)
        deal_player()
        if not player_bj and not cleanup:
            hole_card = deck.pop(0)
            hole_card[4] = True
            deck.append(hole_card)
            # add the card image to a label and display the label while playing
            # a card place sound
            PlaySound.PlaySound('sounds\\cardPlace{}.wav'.format(random.randint(1, 5)),
                                PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
            create_delay(70)
            first_card_obj = tkinter.Label(
                dealer_card_frame,
                image=card_back_image, borderwidth=0, relief='raised',
                background=FELT_COLOR)
            first_card_obj.pack(side='left', padx=(1, 3), pady=(1, 3))
            result_text.set("Dealer drew his hole card.\t\tYour turn...")
            print(result_text.get())
            create_delay(180)
            hc_for_cheatsheet['text'] = "Dealer's hole card is: "
            hc_suit_label['text'] = "{}{}".format(hole_card[3], hole_card[2])
            if hole_card[2] in '♥♦':
                hc_suit_label['fg'] = "red"
            else:
                hc_suit_label['fg'] = "black"
            if is_cheatsheet_on:
                secondWindow.update()
            stats_sheet(hole_card)
            refill_deck_if_empty()
            PLAYERS_TURN = True
            reset_hitnstand_button()
            enable_buttons()
            reset_action_timer()


def flash_bg_fg_widgets(times, color1, color2, *items, style="default", hand="none"):
    temp = []
    for item in items:
        temp.append((item['fg'], item['bg']))
    if hand == "dealer":
        frame_to_flash = dealer_card_frame
    else:
        frame_to_flash = player_card_frame
    if style == "wavy":
        for i in range(1, times + 1):
            for item in items:
                frame_to_flash['bg'] = color2
                for card in frame_to_flash.winfo_children():
                    card['bg'] = color2
                item['bg'] = color1
                item['fg'] = invert_color(item, color1)
                if items.index(item) < len(items) - 2:
                    next_item = items.__getitem__(items.index(item) + 1)
                    next_item['bg'] = color2
                    next_item['fg'] = invert_color(item, color2)
                else:
                    items.__getitem__(0)['bg'] = color2
                    items.__getitem__(0)['fg'] = invert_color(item, color2)
                create_delay(10)
                frame_to_flash['bg'] = color1
                for card in frame_to_flash.winfo_children():
                    card['bg'] = color1
                item['fg'] = invert_color(item, color2)
                if items.index(item) < len(items) - 2:
                    next_item = items.__getitem__(items.index(item) + 1)
                    next_item['bg'] = color1
                    next_item['fg'] = invert_color(item, color1)
                else:
                    items.__getitem__(0)['bg'] = color1
                    items.__getitem__(0)['fg'] = invert_color(item, color1)
                create_delay(10)
                frame_to_flash['bg'] = FELT_COLOR
                for card in frame_to_flash.winfo_children():
                    card['bg'] = FELT_COLOR
                item['fg'] = temp[items.index(item)][0]
                item['bg'] = temp[items.index(item)][1]
                create_delay(10)
        # create_delay(300)
        for item in items:
            item['fg'] = temp[items.index(item)][0]
            item['bg'] = temp[items.index(item)][1]
    elif style == "default":
        for i in range(1, times + 1):
            for item in items:
                item['bg'] = color1
                item['fg'] = invert_color(item, color1)
                # create_delay(200/times)
            create_delay(360 / times)
            for item in items:
                item['bg'] = color2
                item['fg'] = invert_color(item, color2)
                # create_delay(200 / times)
            create_delay(360 / times)
        create_delay(300)
        for item in items:
            item['fg'] = temp[items.index(item)][0]
            item['bg'] = temp[items.index(item)][1]


def shuffle():
    global deck_ready
    # global fp_thread
    global ROUND_IN_SESSION
    if not cleanup:
        ROUND_IN_SESSION = True
        disable_buttons()
        clear_table()
        for card in discard_pile:
            deck.append(card)
        discard_pile.clear()
        random.shuffle(deck)
        print("Shuffling the deck...")
        hit_button['text'] = 'Shuffling'
        PlaySound.PlaySound('sounds\\shufflemachine.wav',
                            PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        working_dots()
        hit_button['text'] = 'Shuffling'
        working_dots()
        bas_strat_button['text'] = "Check Basic\nStrategy Guide"
        bas_strat_button['command'] = check_basic_strategy
        reset_counted()
        deck_ready = True
        # ---- SOME CARDS APPENDED TO THE DECK TO CONTROL SCORE CHECK TESTS ----
        # for i in range(1, 8):
        #     load_back_of_card()
        #     deck.insert(0, (0, card_back_image, ' sff', 'ace'))
        # deck.insert(0, {0: 5, 1: cards[41][1], 2: ' sff', 3: '2', 4: False})
        # deck.insert(0, {0: 5, 1: cards[43][1], 2: ' sff', 3: '2', 4: False})
        # deck.insert(0, {0: 10, 1: cards[48][1], 2: ' sff', 3: '2', 4: False})
        # deck.insert(0, {0: 8, 1: cards[7][1], 2: ' sff', 3: '2', 4: False})
        # deck.insert(0, {0: 10, 1: cards[35][1], 2: ' sff', 3: '2', 4: False})
        # deck.insert(0, {0: 4, 1: cards[3][1], 2: ' sff', 3: '2', 4: False})
        # deck.insert(0, {0: 1, 1: cards[13][1], 2: ' sff', 3: '2', 4: False})
        # deck.insert(0, {0: 10, 1: cards[9][1], 2: ' sff', 3: '2', 4: False})
        deck.insert(0, {0: 8, 1: cards[46][1], 2: ' sff', 3: '2', 4: False})
        deck.insert(0, {0: 10, 1: cards[35][1], 2: ' sff', 3: '2', 4: False})
        deck.insert(0, {0: 8, 1: cards[7][1], 2: ' sff', 3: '2', 4: False})
        deck.insert(0, {0: 1, 1: cards[13][1], 2: ' sff', 3: '2', 4: False})
        deck.insert(0, {0: 10, 1: cards[9][1], 2: ' sff', 3: '2', 4: False})
        # fp_thread.run()
        first_play()


def start_game():
    global deck_ready
    global ROUND_IN_SESSION
    ROUND_IN_SESSION = True
    disable_buttons()
    # hide_stats_sheet()
    PlaySound.PlaySound('sounds\\cardOpenPackage{}.wav'.format(random.randint(1, 2)),
                        PlaySound.SND_FILENAME)
    PlaySound.PlaySound('sounds\\cardTakeOutPackage{}.wav'.format(random.randint(1, 2)),
                        PlaySound.SND_FILENAME)
    PlaySound.PlaySound('sounds\\cardFan{}.wav'.format(random.randint(1, 2)),
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    deck_ready = False
    print("First round commencing")
    shuffle()
    mainWindow.mainloop()
    # fp_thread.start()
    # nrt.start()
    # rat.start()


def say_goodbye():
    global cleanup
    # nrt.join()
    # rat.join()
    # fp_thread.join()
    disable_buttons()
    result_text.set("Goodbye! See you next time! :)")
    print(result_text.get())
    PlaySound.PlaySound("sounds\\later{}.wav".format(random.randint(1, 4)),
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    if is_cheatsheet_on:
        secondWindow.update()
    create_delay(990)
    cleanup = True
    quit()


mainWindow = tkinter.Tk()
#     load_chosen_set(cards)
dealer_hand = []
player_hand = []
cards = []
for j in range(1, no_of_decks + 1):
    load_chosen_set(cards)
deck = list(cards)
discard_pile = []
boldFont = tkinter.font.Font(size=12, weight="bold")
no_decks_for_BS = no_of_decks
if 1 < no_of_decks < 4:
    no_decks_for_BS = 2
elif no_of_decks >= 4:
    no_decks_for_BS = 4

# Set up the GUI  TODO: Make this a separate init_GUI function

mainWindow.iconbitmap("graphics\\icon.ico")
secondWindow = tkinter.Toplevel()
secondWindow.iconbitmap("graphics\\icon.ico")
secondWindow.title("Counting cards!")
secondWindow.config(background='white')
stats_frame = tkinter.Frame(secondWindow, relief='raised', bd=2, width=220, bg='navy')
stats_frame.grid(row=0, column=0, sticky='we')
cheats_frame = tkinter.Frame(secondWindow, relief='raised', bd=2, bg=RESULT_WIN_COLOR)
cheats_frame.grid(row=1, column=0, sticky='we')
secondWindow.grid_columnconfigure(0, weight=1)
init_stats_sheet()
hide_count()
secondWindow.update()
mainWindow.title("Vit's Blackjack Table")
mainWindow.wm_attributes("-topmost", 1)
mainWindow.grid_columnconfigure(0, weight=1)
mainWindow.config(bg='#86592d')
# Load the background image
woodtexture = tkinter.PhotoImage(file="graphics\\background.png")
bglabel = tkinter.Label(mainWindow, image=woodtexture)
bglabel.place(x=0, y=0, relwidth=1, relheight=1)
# Load the images and create the deck
# for i in range(1, 3):  # Testing several decks in the main deck

result_text = tkinter.StringVar()
result_text.set("🂡🂫 Welcome to the BLACKJACK table! 🂫🂡")
result = tkinter.Label(mainWindow, background=RESULT_BG_COLOR, fg='white',
                       textvariable=result_text, font=font.Font(size=14),
                       relief='raised')
result.grid(row=0, column=0, columnspan=4, sticky='ew')
# Drawing the felt
card_frame = tkinter.Frame(mainWindow, height=card_frame_height * 2 + 5,
                           relief='groove', bg=FELT_COLOR, borderwidth='3')
card_frame.grid(row=1, column=0, sticky='wens', columnspan=4, rowspan=2)
# dealer score area
dealer_score_label = tkinter.IntVar()
dealer_score_obj = tkinter.Label(card_frame, text='Dealer Score:',
                                 background=FELT_COLOR, fg='white')
dealer_score_obj.grid(row=0, column=0, sticky='nwe', pady=4)
dealer_score_obj.place()
dealer_score_no = tkinter.Label(card_frame, textvariable=dealer_score_label,
                                font=font.Font(size=18), background=FELT_COLOR,
                                fg='white')
dealer_score_no.grid(row=1, column=0, sticky='n')
# embedded card_frame to hold the card images
dealer_card_frame = tkinter.Frame(card_frame, height=card_frame_height,
                                  background=FELT_COLOR, bd=1, relief="groove")
dealer_card_frame.grid(row=0, column=1, columnspan=2, sticky='ew', rowspan=2)

# dealer_card_frame.grid_propagate(0)
# Player's score area
player_score_label = tkinter.IntVar()
player_score_obj = tkinter.Label(card_frame, text='Player Score:',
                                 background=FELT_COLOR, fg='white')
player_score_obj.grid(row=2, column=0, sticky='new', pady=4)
player_score_no = tkinter.Label(card_frame,
                                textvariable=player_score_label,
                                font=font.Font(size=18), background=FELT_COLOR,
                                fg='white')
player_score_no.grid(row=3, column=0, sticky='n')
# embedded card_frame hold the card images
player_card_frame = tkinter.Frame(card_frame, height=card_frame_height,
                                  background=FELT_COLOR, bd=1, relief="groove")
player_card_frame.grid(row=2, column=1, columnspan=2, sticky='ew', rowspan=2)
timer_strvar = tkinter.StringVar()
card_frame.grid_columnconfigure(0, weight=0)
card_frame.grid_columnconfigure(1, weight=1)
mainWindow.update()
# Control panel area
button_frame = tkinter.Frame(mainWindow, relief='ridge', background='#333300',
                             borderwidth='3')
button_frame.grid(row=3, column=0)

hit_button = tkinter.Button(button_frame, text='HIT',
                            command=deal_player, state='disabled',
                            width=10, height=4, compound=tkinter.BOTTOM,
                            font=boldFont, bg=RESULT_WIN_COLOR)
hit_button.grid(row=0, column=0, rowspan=2, sticky='nws')
bas_strat_button = tkinter.Button(button_frame, text='Check Basic\nStrategy Guide',
                                  command=shuffle, bg=BTN_BG, height=2,
                                  width=12, font=font.Font(size=10))
bas_strat_button.grid(row=0, column=1, sticky='nsew')
ch_button = tkinter.Button(button_frame, text='Show\nStats sheet',
                           command=show_stats_sheet, bg=BTN_BG,
                           width=12, height=2, fg='black')
ch_button.grid(row=0, column=2, sticky='nsew')
new_game = tkinter.Button(button_frame, text='Deal\nNext Round', command=new_round,
                          font=font.Font(size=10), bg='#4d79ff', width=12,
                          height=2, fg='white')
new_game.grid(row=1, column=1, sticky='nsew')
leave_button = tkinter.Button(button_frame, text='Leave\nTable', font=font.Font(size=10),
                              command=say_goodbye, height=2, width=12,
                              bg='black', fg='white')
leave_button.grid(row=1, column=2, sticky='nsew')
leave_button.place()
stand_button = tkinter.Button(button_frame, text='STAND',
                              command=deal_dealer, state='normal',
                              width=10, font=boldFont, fg='white',
                              bg='#cc0000')
stand_button.grid(row=0, column=3, rowspan=2, sticky='nws')
button_frame.columnconfigure(1, minsize=20)
button_frame.columnconfigure(2, minsize=20)
# atexit.register(say_goodbye)
mainWindow.update()
mainWindow.geometry("{}x{}+265+100".format(wanted_window_width, button_frame.winfo_height() + result.winfo_height() +
                                           5 + int(card_frame_height * 2)))
mainWindow.minsize(wanted_window_width,
                   button_frame.winfo_height() + result.winfo_height() +
                   5 + int(card_frame_height * 2))
mainWindow.maxsize(wanted_window_width,
                   button_frame.winfo_height() + result.winfo_height() +
                   5 + int(card_frame_height * 2))
secondWindow.geometry("220x{}+45+100".format(mainWindow.winfo_height()))
mainWindow.update()
# nrt = threading.Thread(target=new_round_timer, daemon=True)
# rat = threading.Thread(target=reset_action_timer, daemon=True)
# fp_thread = threading.Thread(target=first_play, daemon=True)


if __name__ == "__main__":
    start_game()
