import atexit
import time

try:
    import tkinter
except ImportError:
    import Tkinter as tkinter
import concurrent.futures
import ctypes
import random
import sqlite3
import tkinter.font as font
from PIL import Image, ImageTk
import simpleaudio as sa
import winsound as PlaySound

ctypes.windll.shcore.SetProcessDpiAwareness(1)

if tkinter.TkVersion >= 8.6:  # tkinter version above 8.6 supports png files
    extension = 'png'
else:
    extension = 'ppm'

executor = concurrent.futures.ThreadPoolExecutor()
themes = {
    "oldschool": {
        "felt_color": "#339933",
        "timer_name": "oldschool",
        "shoe": "expressionism",
        "deck_backs": 1,
        "bg": "oldschoolBG.png",
        "armrest": "armrestoldschool.png",
        "scorebg": "oldschoolscorebg.png",
        "buttonbg": "oldschoolbuttonbg.png",
        "card_frame_lbl_fg": "white",
        "hit_btn_bg": "#FFD800",
        "hit_btn_fg": "black",
        "stand_btn_bg": '#cc0000',
        'stand_btn_fg': 'white',
        "new_round_bg": "#99b3ff",
        "new_round_fg": "black",
        "bas_strat_btn_bg": "#ffcc99",
        'lose_color': "#993300",
        'win_color': '#ffcc00',
        'timer_images': []

    },
    "casino": {
        "felt_color": "#992600",
        "timer_name": "casino",
        "shoe": "bicycle",
        "deck_backs": 3,
        "bg": "casinoBG.png",
        "armrest": "armrestcasino.png",
        "scorebg": "casinoscorebg.png",
        "buttonbg": "casinobuttonbg.png",
        "card_frame_lbl_fg": "white",
        "hit_btn_bg": "#FFD800",
        "hit_btn_fg": "black",
        "stand_btn_bg": '#331a00',
        'stand_btn_fg': 'white',
        "new_round_bg": "#ff0066",
        "new_round_fg": "black",
        "bas_strat_btn_bg": "white",
        'lose_color': "black",
        'win_color': '#ffcc00',
        'timer_images': []
    },
    "casino_blue": {
        "felt_color": "#3C53E0",
        "timer_name": "casino",
        "shoe": "casino2.0",
        "deck_backs": 1,
        "bg": "casino_blueBG.png",
        "armrest": "armrestcasinoblue.png",
        "scorebg": "aquascorebg.png",
        "buttonbg": "aquabuttonbg.png",
        "card_frame_lbl_fg": "black",
        "hit_btn_bg": "#FFD800",
        "hit_btn_fg": "black",
        "stand_btn_bg": '#331a00',
        'stand_btn_fg': 'white',
        "new_round_bg": "#ff0066",
        "new_round_fg": "black",
        "bas_strat_btn_bg": "white",
        'lose_color': "black",
        'win_color': '#009933',
        'timer_images': []
    },
    "aqua": {
        "felt_color": "#86fcc9",
        "timer_name": "aqua",
        "shoe": "aqua",
        "deck_backs": 9,
        "bg": "aquaBG.png",
        "armrest": "armrestaqua.png",
        "scorebg": "aquascorebg.png",
        "buttonbg": "aquabuttonbg.png",
        "card_frame_lbl_fg": "black",
        "hit_btn_bg": "#ffffe6",
        "hit_btn_fg": "black",
        "stand_btn_bg": '#000099',
        'stand_btn_fg': 'white',
        "new_round_bg": "#ffff80",
        "new_round_fg": "black",
        "bas_strat_btn_bg": "#b3b3ff",
        'lose_color': "#663300",
        'win_color': '#009933',
        'timer_images': []
    }

}

nrt_running = False
SET_MINIMUM_BET = 5
minimum_bet = SET_MINIMUM_BET
starting_total = 1000.00
card_frame_height = 164
# fp_thread = threading.Thread()
decks_left = object
current_act = ''
RESULT_BG_COLOR = "navy"  # Background color of the result label
ACTION_TIME = 25  # The time the dealer waits before the player forfeits his say
TIME_BETWEEN_ROUNDS = 20  # The time before the round is reset if the player doesn't reset it
nrt_seconds_left = TIME_BETWEEN_ROUNDS
players_turn = False  # Set to true whenever it's the player say
ROUND_IN_SESSION = False  # Set to true if cards are being dealt
RESULT_LOSE_COLOR = "#990000"  # Background color of result label if the player loses
RESULT_WIN_COLOR = 'gold'  # Background color of result label if the player wins
NAT_DELAY_TIME = 1000  # Natural delay time between result label updates
dealerstand_score = 17  # The score in which the dealer can't hit anymore
hand_is_soft = False  # True if a hand contains a soft ace (Value of 11)
dealer_hits_on_soft = True  # True if dealer can/must hit on Soft 17
kill_delays = False
current_count = None
deck_ready = True  # False if the shoe was dealt, not shuffled
player_bj = False  # True if the player got Blackjack
cleanup = False  # True if the player left the table, breaks all timer loops
card_back_image = ''  # Handler for the cards shoe back graphic
hole_card = tkinter.Widget  # Handler for dealer's hole card
suit_label = tkinter.Widget
hc_suit_label = tkinter.Widget
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
no_of_decks = 6  # How many decks of cards do you want in the shoe
no_of_backs = 0  # Number of backs pictures provided in each set
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


def flash_button(times, tag):
    image = felt.itemcget(tag, 'image')
    actvimage = felt.itemcget(tag, 'activeimage')
    for i in range(times + 1):
        felt.itemconfig(tag, image=actvimage, activeimage=image)
        time.sleep(0.05)
        felt.itemconfig(tag, image=image, activeimage=actvimage)
        time.sleep(0.05)


# noinspection PyUnboundLocalVariable
def check_basic_strategy_new() -> str:
    db = sqlite3.connect('E:\\coding\\Blackjack2.0\\basic_strategy.sqlite')
    str_to_sql = str(no_decks_for_BS) + str(int(dealer_hits_on_soft))
    d_score = dealer_score_var.get()
    if len(player_hand['cards']) <= 2:
        list_to_sort = sorted([player_hand['cards'][0][0], player_hand['cards'][1][0]])
        card1 = list_to_sort[0]
        card2 = list_to_sort[1]
        suggested_action = db.execute("SELECT action_{} FROM first_play WHERE "
                                      "card1 = ? AND card2 = ? AND dealers_card = ?"
                                      .format(str_to_sql),
                                      (card1, card2, d_score,)).fetchone()
    else:
        p_score = player_score_var.get()
        suggested_action = db.execute("SELECT action_{} FROM after_first_play WHERE "
                                      "player_score=? AND dealer_score=? AND hand_is"
                                      "_soft=?".format(str_to_sql),
                                      (p_score, d_score, str(int(hand_is_soft)),)).fetchone()
    suggested_action = list(suggested_action)
    db.close()
    if not felt.find_withtag(current_act):
        return suggested_action[0]
    else:
        while not hint_var.get() == "":
            time.sleep(0.1)
        if "stand" in suggested_action[0].casefold():
            sa.WaveObject.from_wave_file("sounds\\hint_stand.wav").play()
            # flash_bg_fg_widgets(6, 'white', '#bf40bf', stand_button, hint)
            button_to_flash = "stand"
        elif "hit" in suggested_action[0].casefold():
            sa.WaveObject.from_wave_file("sounds\\hint_hit.wav").play()
            # flash_bg_fg_widgets(6, 'white', '#bf40bf', hit_button, hint)
            button_to_flash = "hit"
        elif "double" in suggested_action[0].casefold():
            if not felt.itemcget('double', 'state') == 'hidden':
                sa.WaveObject.from_wave_file("sounds\\hint_dd.wav").play()
                # flash_bg_fg_widgets(6, 'white', '#bf40bf', dd_button, hint)
                button_to_flash = "double"
            else:
                suggested_action[0] = "You should have Doulbed-down, but you " \
                                      "don't have the cash, so Hit."
                sa.WaveObject.from_wave_file("sounds\\hint_hit.wav").play()
                # flash_bg_fg_widgets(6, 'white', '#bf40bf', hit_button, hint)
                button_to_flash = "hit"
        elif "surrender" in suggested_action[0].casefold():
            sa.WaveObject.from_wave_file('sounds\\chipLay2.wav').play()
            # flash_bg_fg_widgets(6, 'white', 'black', surrender_button, hint)
            button_to_flash = "surrender"
        elif "split" in suggested_action[0].casefold():
            if not felt.itemcget('split', 'state') == 'hidden':
                sa.WaveObject.from_wave_file("sounds\\chipLay3.wav").play()
                button_to_flash = "split"
            else:
                suggested_action[0] = "You should have Split, but you " \
                                      "don't have the cash, so Hit."
                sa.WaveObject.from_wave_file("sounds\\hint_hit.wav").play()
                button_to_flash = "hit"
        hint_var.set(suggested_action[0])
        flash_button(6, button_to_flash)
        time.sleep(1)
        hint_var.set("")
    hint_queue_var.set(hint_queue_var.get() - 1)
    print(hint_queue_var.get())  # TODO: delete this
    return suggested_action[0]


def load_chosen_set(card_images):
    global no_of_backs
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
            name = 'decks\\{}\\{}0{}.{}'.format(themes[theme.get()]['shoe'], suit, str(card), extension)
            image = tkinter.PhotoImage(file=name)
            img_open = Image.open(name)
            rotated_image = img_open.rotate(270, expand=1)
            rot_card = ImageTk.PhotoImage(rotated_image)
            card_images.append({0: card, 1: image, 2: suits[suit],
                                3: card_names[card].upper(), 4: False, 5: rot_card})

        for card in range(10, 14):
            name = 'decks\\{}\\{}{}.{}'.format(themes[theme.get()]['shoe'], suit, str(card), extension)
            image = tkinter.PhotoImage(file=name)
            img_open = Image.open(name)
            rotated_image = img_open.rotate(270, expand=1)
            rot_card = ImageTk.PhotoImage(rotated_image)
            card_images.append({0: 10, 1: image, 2: suits[suit],
                                3: card_names[card].upper(), 4: False, 5: rot_card})


randed_back = 0


def load_back_of_card():
    global card_back_image
    global randed_back
    randed_back = random.randint(1, themes[theme.get()]['deck_backs'])
    card_back_image = tkinter.PhotoImage(
        file="decks\\{}\\back{}.{}".format(
            themes[theme.get()]['shoe'],
            randed_back,
            extension))


def invert_color(item, color):  # Invert color
    if type(color) == str:
        rgb = item.winfo_rgb(color)
    else:
        rgb = color
    rgb = (65535 - rgb[0], 65535 - rgb[1], 65535 - rgb[2])
    tk_rgb = "#%04x%04x%04x" % rgb
    return tk_rgb


def working_dots():
    """
    Creates the cool process bar like dots on the big button.
    Lasts 3 seconds while a sound is playing.
    :return:
    """
    # bas_strat_button['text'] = bas_strat_button['text'] + '\n'
    # for i in range(1, 13):
    #     bas_strat_button['text'] = bas_strat_button['text'] + '.'
    #     create_delay(250)
    pass


def show_stats_sheet():
    global is_cheatsheet_on
    show_stats_button['text'] = "Hide Stats Sheet (s)"
    show_stats_button['command'] = hide_stats_sheet
    is_cheatsheet_on = True
    mainWindow.update()
    secondWindow.update()
    secondWindow.deiconify()


def hide_stats_sheet():
    global is_cheatsheet_on
    secondWindow.withdraw()
    is_cheatsheet_on = False
    show_stats_button['text'] = "Show Stats Sheet (s)"
    show_stats_button['command'] = show_stats_sheet
    mainWindow.update()


def set_newround_and_shuffle_buttons():
    # hit_button['text'] = "ready"
    # stand_button['text'] = 'Shuffle First'
    # hit_button['command'] = trigger_newround
    # hit_button['bg'] = stand_button['bg'] = themes[theme.get()]['new_round_bg']
    # stand_button['command'] = trigger_shuffle
    # stand_button['fg'] = 'black'

    mainWindow.update()


# noinspection PyUnusedLocal
def trigger_newround(event='event'):
    global ROUND_IN_SESSION
    ROUND_IN_SESSION = True
    felt.itemconfig("ready", activeimage=ready_btn_clk_img, image=ready_btn_clk_img)
    felt.update()
    time.sleep(0.025)
    felt.itemconfig("ready", activeimage=ready_actvbtn_img, image=ready_btn_img)
    felt.update()
    time.sleep(0.025)
    felt.itemconfig("end", state="hidden")
    result_text.set("Next hand starting now.")
    executor.submit(new_round)


# noinspection PyUnusedLocal
def trigger_shuffle(event='event'):
    felt.itemconfig("newshoe", activeimage=newshoe_btn_clk_img, image=newshoe_btn_clk_img)
    felt.update()
    time.sleep(0.025)
    felt.itemconfig("newshoe", activeimage=newshoe_actvbtn_img, image=newshoe_btn_img)
    felt.update()
    time.sleep(0.025)
    felt.itemconfig("end", state="hidden")
    executor.submit(shuffle)


# noinspection PyUnusedLocal
def trigger_stand(event='event'):
    if len(player_hand['cards']) == 2:
        hide_special_options()
    if tiktok_playback:
        # noinspection PyUnresolvedReferences
        if tiktok_playback.is_playing():
            tiktok_playback.stop()
    felt.itemconfig("stand", activeimage=stand_btn_clk_img, image=stand_btn_clk_img)
    felt.itemconfig("normal_action", state="disabled")
    felt.update()
    time.sleep(0.05)
    felt.itemconfig("stand", activeimage=stand_actvbtn_img, image=stand_btn_img)
    executor.submit(hide_action_timer)
    deal_dealer()


def hide_action_buttons():
    felt.itemconfig("stand", image=stand_btn_img)
    felt.itemconfig("button", state="hidden")
    # felt.moveto("hit", button_row_posx, button_row_posy)
    # felt.moveto("stand", button_row_posx + 36, button_row_posy)
    # felt.moveto("help", button_row_posx + 72, button_row_posy)


# noinspection PyUnusedLocal
def trigger_hit(event='event'):
    if len(player_hand['cards']) == 2:
        hide_special_options()
    if tiktok_playback:
        if tiktok_playback.is_playing():
            tiktok_playback.stop()
    felt.itemconfig("hit", activeimage=hit_btn_clk_img, image=hit_btn_clk_img)
    felt.itemconfig("normal_action", state="disabled")
    executor.submit(hide_action_timer)
    felt.update()
    time.sleep(0.05)
    felt.itemconfig("hit", activeimage=hit_actvbtn_img, image=hit_btn_img)
    felt.itemconfig("special", state="hidden")
    deal_player()


def move_to_discard_pile():
    for i in range(len(shoe) - 1, -1, -1):
        if shoe[i][4]:
            shoe[i][4] = False
            discard_pile.append(shoe[i])
            shoe.pop(i)


table_cleared = True
clearing_table = False


def clear_table():
    global player_bj
    global dealer_hand
    global player_hand
    global clearing_table
    global table_cleared
    clearing_table = True
    result_text.set(
        f"Hand #{total_rounds_tally} finished. {outcome}")
    player_bj = False
    move_to_discard_pile()
    player_score_var.set(0)
    dealer_score_var.set(0)
    result['bg'] = RESULT_BG_COLOR
    result['fg'] = 'white'
    felt.moveto(dealer_score_digits, dealer_score_digits_orig_pos[0], dealer_score_digits_orig_pos[1])
    # felt.moveto(player_score_digits, player_score_digits_orig_pos[0], player_score_digits_orig_pos[1])
    felt.itemconfig(dealer_score_digits, font=font.Font(size=18), fill=themes[theme.get()]['card_frame_lbl_fg'])
    felt.itemconfig(player_score_digits, font=font.Font(size=18), fill=themes[theme.get()]['card_frame_lbl_fg'])
    print("Clearing the table...")
    hint_var.set('Clearing Player\'s Hand\n')
    how_many_dots = 30 // len(player_hand['items'])
    count_dots_added = 0
    for item in player_hand['items']:
        randed = random.randint(0, 1)
        count_dots_added += how_many_dots
        felt.delete(item)
        if not player_hand['items']:
            if count_dots_added < 30:
                hint_var.set(hint_var.get() + str("." * (30 - count_dots_added + how_many_dots)))
            elif count_dots_added >= 30:
                hint_var.set(hint_var.get() + str("." * (30 - (count_dots_added - how_many_dots))))
        else:
            hint_var.set(hint_var.get() + str("." * how_many_dots))
        cards_slides[randed].play()
        create_delay(50)
    create_delay(200)
    hint_var.set('Clearing Dealer\'s Hand\n')
    count_dots_added = 0
    how_many_dots = 30 // len(dealer_hand['items'])
    for item in reversed(dealer_hand['items']):
        randed = random.randint(0, 1)
        count_dots_added += how_many_dots
        felt.delete(item)
        if not dealer_hand['items']:
            if count_dots_added < 30:
                hint_var.set(hint_var.get() + str("." * (30 - count_dots_added + how_many_dots)))
            elif count_dots_added >= 30:
                hint_var.set(hint_var.get() + str("." * (30 - (count_dots_added - how_many_dots))))
        else:
            hint_var.set(hint_var.get() + str("." * how_many_dots))
        cards_slides[randed].play()
        create_delay(50)
    dealer_hand = {"cards": [], "items": []}
    player_hand = {"cards": [], "items": []}
    PlaySound.PlaySound("sounds\\discardPile.wav", PlaySound.SND_FILENAME)
    table_cleared = True
    clearing_table = False
    create_delay(200)
    hint_var.set("")


def create_delay(delay_time, *items):
    for i in range(1, int(delay_time / 10) + 1):
        if cleanup or kill_delays:
            return
        if items:
            for item in items:
                item.after(10, item.update())
            # mainWindow.after(10, [item.update() for item in items])
        else:
            mainWindow.after(10, mainWindow.update())


def new_round_timer():
    global nrt_running
    global nrt_seconds_left
    global ROUND_IN_SESSION
    seconds = nrt_seconds_left
    nrt_running = True
    i = seconds
    while i > 0 and placed_bet_var.get() >= minimum_bet and not ROUND_IN_SESSION:
        if cleanup:
            nrt_running = False
            print("BROKEN BY QUIT!")  # TODO: Remove this
            return
        if not clearing_table:
            result_text.set("Next hand will start in {}".format(i))
        mainWindow.update()
        nrt_seconds_left = i
        i -= 1
        # Beep in the last 3 seconds
        if not ROUND_IN_SESSION and i <= 3:
            PlaySound.Beep(2400 - i * 300, 150)
            time.sleep(0.85)
        elif i > 3:
            time.sleep(1)
        else:
            nrt_running = False
            print("BROKEN BY PLAYER!")  # TODO: Remove this
            return
    else:
        print("BROKEN!")  # TODO: Remove this
    nrt_running = False
    if i == 0 and placed_bet_var.get() >= minimum_bet and not ROUND_IN_SESSION:
        return trigger_newround()


def reset_action_timer():
    global current_act
    global tiktok_playback
    timer_visible = True
    milliseconds = ACTION_TIME * 1000
    timer_posx = int(felt.coords(player_hand["items"][len(player_hand["items"]) - 1])[0]) + DISTANCE_X + 39
    timer_posy = int(felt.coords(player_hand["items"][len(player_hand["items"]) - 1])[1]) - 50
    timer_obj = felt.create_image(timer_posx, timer_posy, anchor='sw',
                                  tags=f'timer{timer_posx}')
    felt.tag_raise('button')
    felt.itemconfig("normal_action", state='normal')
    current_act = f'timer{timer_posx}'
    next_frame = 0
    while milliseconds >= 0 and felt.find_withtag(f'timer{timer_posx}'):
        if cleanup:
            if tiktok_playback.is_playing():
                tiktok_playback.stop()
            return
        if theme.get() == "oldschool":
            felt.itemconfigure(timer_obj, image=oldschooltimer_animation[next_frame])
            milliseconds -= 200
            next_frame += 1
            time.sleep(0.2)
        else:
            felt.itemconfigure(timer_obj, image=themes[theme.get()]['timer_images'][milliseconds // 1000])
            milliseconds -= 1000
            time.sleep(1)
        if milliseconds == 4000:
            tiktok_playback = tiktok_wav.play()
        if milliseconds == 0 and felt.find_withtag(f'timer{timer_posx}'):
            if not theme.get() == 'oldschool':
                felt.itemconfigure(timer_obj, image=themes[theme.get()]['timer_images'][0])
            PlaySound.PlaySound("sounds\\timesup.wav",
                                PlaySound.SND_FILENAME)
            break
        if not felt.find_withtag(f'timer{timer_posx}'):
            if tiktok_playback.is_playing():
                tiktok_playback.stop()
            return
    if not cleanup and players_turn and felt.find_withtag(f'timer{timer_posx}'):
        hide_action_timer()
        if "hit" in check_basic_strategy_new().casefold() \
                or "double" in check_basic_strategy_new().casefold():
            return trigger_hit()
        elif player_score_var.get() >= 16:
            return trigger_stand()
        else:
            return trigger_hit()
    else:
        return


# noinspection PyUnresolvedReferences
def hide_action_timer():
    felt.delete(felt.find_withtag(current_act))


# noinspection PyUnresolvedReferences
def update_count(next_card):
    global count
    global decks_left
    returning_count = count[0]
    cards_left = count[1]
    decks_left_no = count[2]
    if cards_left == 0:
        cards_left = 52
        count[2] = decks_left_no = decks_left_no - 1
    if 2 <= next_card[0] <= 6:
        returning_count += 1
    elif 10 <= next_card[0] <= 11 or next_card[0] == 1:
        returning_count -= 1

    if decks_left_no < 0:
        decks_left_no = no_of_decks
    if decks_left_no == 0:
        count[3] = returning_count
    else:
        count[3] = int(returning_count * 10 / (decks_left_no + cards_left / 52)) / 10  # True count
    cards_left -= 1
    if is_shoe_empty():
        count[0] = 0
    else:
        count[0] = returning_count
    count[1] = cards_left
    decks_left['text'] = "{}, (+{} uncounted)".format(decks_left_no, cards_left)

    current_count['text'] = returning_count
    cheats_frame.update()


def reset_counted():
    global counted, count
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
    total = 0
    for card in shoe:
        if not card[4]:
            counted[card[3]] = str(int(counted[card[3]]) + 1)
            total += 1
    count[1] = total % 52
    row_counter = 0
    for key, value in counted.items():
        cheats_frame.winfo_children()[row_counter]['text'] = "{:<3} : {:>3}".format(key, value)
        row_counter += 1
    if is_cheatsheet_on:
        secondWindow.update()
    cheats_frame.winfo_children()[row_counter]['text'] = "{} left in the shoe.".format(total)
    if not is_shoe_empty():
        suit_label['text'] = '{}{}'.format(shoe[0][3], shoe[0][2])
        if shoe[0][2] in '♥♦':
            suit_label['fg'] = "red"
        else:
            suit_label['fg'] = "black"
        if is_cheatsheet_on:
            secondWindow.update()


def init_stats_sheet():
    global suit_label
    global hc_for_cheatsheet
    global hc_suit_label
    global decks_left
    global hide_ch_button
    global current_count
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
    tkinter.Label(cheats_frame, text="{} left in the shoe.".format(total),
                  background=RESULT_WIN_COLOR) \
        .grid(column=0, row=row_counter, sticky='nw')
    row_counter += 1
    tkinter.Label(cheats_frame, text="Top card in the shoe is: ",
                  background=RESULT_WIN_COLOR) \
        .grid(column=0, row=row_counter, sticky='nw')
    suit_label = tkinter.Label(cheats_frame,
                               text="{}{}".format(shoe[0][3], shoe[0][2]),
                               background=RESULT_WIN_COLOR)
    suit_label.grid(column=1, row=row_counter, sticky='nw')
    if shoe[0][2] in '♥♦':
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
    row_counter += 1
    tkinter.Label(cheats_frame, text='Current count: ', height=1, background=RESULT_WIN_COLOR) \
        .grid(column=0, row=row_counter, sticky='nw')
    current_count = tkinter.Label(cheats_frame, text='', height=1,
                                  background=RESULT_WIN_COLOR)
    current_count.grid(column=1, row=row_counter,
                       sticky='nw')
    row_counter += 1
    dl_label = tkinter.Label(cheats_frame, text='Decks left: ', height=1, background=RESULT_WIN_COLOR)
    dl_label.grid(column=0, row=row_counter, sticky='nw')
    decks_left = tkinter.Label(cheats_frame, text='', height=1,
                               background=RESULT_WIN_COLOR)
    decks_left.grid(column=1, row=row_counter, sticky='nw')
    if is_cheatsheet_on:
        secondWindow.update()

    hide_ch_button = tkinter.Button(stats_frame,
                                    text='Show me more',
                                    bg='black', fg='white',
                                    command=show_count_sheet)
    hide_ch_button.grid(row=0, column=0, columnspan=2, sticky='w')
    mainWindow.bind('<Control-Alt-s>', lambda event: hide_ch_button.invoke())
    current_round_num = tkinter.Label(stats_frame, text='Hand #1',
                                      fg='white', bg='navy', font=boldFont)
    current_round_num.grid(row=1, column=0, sticky='w')
    rounds_player_won = tkinter.Label(stats_frame, text='Hands won:',
                                      fg='white', bg='navy')
    rounds_player_won.grid(row=2, column=0, sticky='w')
    rounds_dealer_won = tkinter.Label(stats_frame, text='Hands lost:',
                                      fg='white', bg='navy')
    rounds_dealer_won.grid(row=3, column=0, sticky='w')
    rounds_draw = tkinter.Label(stats_frame, text='Hands Pushed:',
                                fg='white', bg='navy')
    rounds_draw.grid(row=4, column=0, sticky='w')
    player_bj_label = tkinter.Label(stats_frame, text='Player BLACKJACKS:',
                                    fg='white', bg='navy')
    player_bj_label.grid(row=5, column=0, sticky='w')
    dealer_bj_label = tkinter.Label(stats_frame, text='Dealer BLACKJACKS:',
                                    fg='white', bg='navy')
    dealer_bj_label.grid(row=6, column=0, sticky='w')
    reset_counted()
    secondWindow.update()
    secondWindow.maxsize(300, stats_frame.winfo_height())
    secondWindow.minsize(300, stats_frame.winfo_height())


def update_bj_stats():
    global dealer_bj_label, player_bj_label
    dealer_bj_label['text'] = "Dealer BLACKJACKS:\t{0}, {1:>3.2f}%". \
        format(dealer_bj_tally, dealer_bj_tally * 100 / total_rounds_tally)
    dealer_bj_label.update()
    player_bj_label['text'] = "Player BLACKJACKS:\t{0}, {1:>3.2f}%". \
        format(player_bj_tally, player_bj_tally * 100 / total_rounds_tally)
    player_bj_label.update()


def show_hide_hint_frame(varname, index, mode):
    if mainWindow.getvar(varname) != "":
        hint_frame.place(relx=0.5, rely=0.45, anchor='n')
    else:
        hint_frame.place_forget()


def trigger_show_count(event):
    if hint_queue_var.get() < 2:
        hint_queue_var.set(hint_queue_var.get() + 1)
        executor.submit(show_count)
    print(hint_queue_var.get())


def show_count():
    while not hint_var.get() == "":
        time.sleep(0.1)
    current_str = f"The running count is {count[0]} and the true count is {count[3]}."
    hint_var.set(current_str)
    time.sleep(2)
    if hint_var.get() == current_str:
        hint_var.set("")
    hint_queue_var.set(hint_queue_var.get() - 1)
    print(hint_queue_var.get())


def show_count_sheet():
    global hide_ch_button
    secondWindow.minsize(300, stats_frame.winfo_height() + cheats_frame.winfo_height())
    secondWindow.maxsize(300, stats_frame.winfo_height() + cheats_frame.winfo_height())
    hide_ch_button['text'] = "I'm no cheater!"
    hide_ch_button['command'] = hide_count_sheet
    secondWindow.update()


def hide_count_sheet():
    global hide_ch_button
    secondWindow.minsize(300, stats_frame.winfo_height())
    secondWindow.maxsize(300, stats_frame.winfo_height())
    hide_ch_button['text'] = "Show me more"
    hide_ch_button['command'] = show_count_sheet
    secondWindow.update()


def allow_betting():
    global minimum_bet
    if not table_cleared:
        executor.submit(trigger_clt)
    if bankroll.get() > 0 or placed_bet_var.get() > 0:
        if placed_bet_var.get() >= minimum_bet and total_rounds_tally:
            felt.itemconfig("end", state='normal')
            trigger_nrt(str(placed_bet_var), 0, "write")
            create_delay(NAT_DELAY_TIME // 2)
        elif placed_bet_var.get() >= minimum_bet:
            felt.itemconfig("ready", state='normal')
        else:
            felt.itemconfig("end", state='disabled')
        for stack in chip_stacks.allBetStacks:
            chip_stacks.BetStack.assign_binds(stack)
        felt.tag_raise("end")
        sa.WaveObject.from_wave_file(f"sounds\\betsplease{random.randint(1, 3)}.wav").play()
        # placed_bet_label['text'] = "Your bet:"
        result['bg'] = RESULT_BG_COLOR
        result['fg'] = 'white'
        if bankroll.get() < minimum_bet:
            minimum_bet = bankroll.get()
        else:
            minimum_bet = SET_MINIMUM_BET
        mainWindow.update()
        result_text.set("Place your bet.")
    else:
        executor.submit(trigger_clt)
        result_text.set("GAME OVER!")
        felt.tag_raise("gameover")
        felt.itemconfig("gameover", state='normal')


def reset_everything(event):
    global rounds_player_won
    global total_rounds_tally
    global p_w_tally
    global d_w_tally
    global draw_tally
    global rounds_dealer_won
    global rounds_draw
    global player_bj_tally
    global dealer_bj_tally
    felt.itemconfig("buyin", activeimage=buyin_btn_clk_img, image=buyin_btn_clk_img)
    felt.update()
    time.sleep(0.025)
    felt.itemconfig("buyin", activeimage=buyin_actvbtn_img, image=buyin_btn_img)
    felt.update()
    time.sleep(0.025)
    felt.itemconfig("gameover", state="hidden")
    # TODO: insert buyin function for chip_stacks class
    p_w_tally = 0
    draw_tally = 0
    d_w_tally = 0
    player_bj_tally = 0
    dealer_bj_tally = 0
    rounds_player_won['text'] = "Hands won:"
    rounds_dealer_won['text'] = "Hands lost:"
    rounds_draw['text'] = "Hands pushed:"
    total_rounds_tally = 0
    stats_sheet(shoe[0])
    dealer_bj_label['text'] = "Delaer BLACKJACKS:"
    player_bj_label['text'] = "Player BLACKJACKS:"
    allow_betting()


def trigger_clt():
    seconds = 3
    time.sleep(3)
    while seconds > 0 and not clearing_table and not table_cleared:
        hint_var.set(f"Clearing the table in {seconds}")
        time.sleep(1)
        seconds -= 1
    else:
        if not table_cleared and not clearing_table:
            clear_table()


# noinspection PyUnusedLocal
def trigger_nrt(varname, index, mode):
    global nrt_seconds_left
    if mainWindow.getvar(varname) >= minimum_bet:
        felt.itemconfig("ready", state='normal')
        if total_rounds_tally:
            felt.itemconfig("newshoe", state='normal')
        if not nrt_running:
            executor.submit(new_round_timer)
    else:
        result_text.set(f"Waiting for minimum bet. ({minimum_bet})")
        felt.itemconfig("end", state='disabled')


def trigger_check_bas_strat(event):
    if players_turn:
        if hint_queue_var.get() < 2:
            hint_queue_var.set(hint_queue_var.get() + 1)
            felt.itemconfig("help", activeimage=help_btn_clk_img, image=help_btn_clk_img)
            felt.update()
            executor.submit(check_basic_strategy_new)
            time.sleep(0.05)
            felt.itemconfig("help", image=help_btn_img, activeimage=help_actvbtn_img)
        print(hint_queue_var.get())


def no_more_bets():
    for stack in chip_stacks.allBetStacks:
        chip_stacks.BetStack.remove_binds(stack)
    # placed_bet_label['text'] = "Current Pot:"
    # placed_bet_no['fg'] = themes[theme.get()]['card_frame_lbl_fg']
    while clearing_table:
        time.sleep(0.2)


def new_round():
    global shoe
    global hand_is_soft
    global deck_ready
    global player_hand
    global dealer_hand
    global ROUND_IN_SESSION
    global total_rounds_tally
    if not cleanup:
        hand_is_soft = False
        deck_ready = False
        total_rounds_tally += 1
        no_more_bets()
        if not table_cleared and not clearing_table:
            clear_table()
        sa.WaveObject.from_wave_file("sounds\\ready.wav").play().wait_done()
        current_round_num['text'] = "Hand #{}".format(total_rounds_tally)
        print("Hand #{} commencing.".format(total_rounds_tally))
        if is_cheatsheet_on:
            secondWindow.update()
        mainWindow.bind('<Return>', lambda event: trigger_hit)
        mainWindow.bind('<plus>', lambda event: trigger_stand)
        mainWindow.bind('0', trigger_check_bas_strat)
        mainWindow.bind('7', double_down)
        mainWindow.bind('9', lambda event: surrender)
        create_delay(500)
        return first_play()


def is_shoe_empty():
    """
        go through the shoe and see if the 4th index of all the cards
        (a boolean that is true if the card was already dealt) is true.
        If so, that means that all the cards were dealt and
        a new shoe is made from the discard pile (all the cards that
        were already dealt and are not in this current Hand).
        As soon as the first undealt card is found (4th index is
        false) deck_is_empty is made false, and the loop is broken
        to stop looking for more undealt cards.
    :return:
    """
    for card in shoe:
        if not card[4]:
            return False
    return True


def refill_shoe_if_empty():
    global count
    if is_shoe_empty():
        felt.itemconfig("button", state="disabled")
        create_delay(500)
        random.shuffle(discard_pile)
        for card in discard_pile:
            shoe.insert(0, card)
        discard_pile.clear()
        tempstr = result_text.get()
        result_text.set('Deck has emptied! Shuffling the discard pile.')
        hint_var.set("Shuffling...")
        sa.WaveObject.from_wave_file('sounds\\shufflemachine.wav').play().wait_done()
        result_text.set(tempstr)
        hint_var.set("")
        count = [0, 0, no_of_decks, 0.0]
        reset_counted()
        if is_cheatsheet_on:
            secondWindow.update()
        felt.itemconfig("button", state="normal")
        mainWindow.update()


def hide_special_options():
    felt.itemconfig("special", state='hidden')


def show_special_options():
    if bankroll.get() >= placed_bet_var.get():
        if player_hand['cards'][0][3] == player_hand['cards'][1][3]:
            felt.itemconfig('special', state='normal')
            # felt.moveto('surrender', button_row_posx + 30, button_row_posy + 40)
            felt.moveto('double', button_row_posx + 18, button_row_posy)
            felt.moveto('split', button_row_posx + 56, button_row_posy)
        else:
            felt.itemconfig('double', state='normal')
            felt.itemconfig('surrender', state='normal')
            # felt.moveto('surrender', button_row_posx + 50, button_row_posy)
            felt.moveto('double', button_row_posx + 18, button_row_posy)
    else:
        felt.itemconfig('surrender', state='normal')
        # felt.moveto('surrender', button_row_posx + 30, button_row_posy)


def surrender(event):
    global ROUND_IN_SESSION
    global players_turn
    if players_turn:
        felt.itemconfig("surrender", activeimage=surrender_btn_clk_img, image=surrender_btn_clk_img)
        felt.itemconfig("button", state="disabled")
        felt.update()
        time.sleep(0.05)
        felt.itemconfig("surrender", activeimage=surrender_actvbtn_img, image=surrender_btn_img)
        felt.update()
        felt.itemconfig("button", state="hidden")
        executor.submit(hide_action_timer)
        ROUND_IN_SESSION = False
        players_turn = False
        chip_stacks.pay_player(player_bj, value=placed_bet_var.get() / 2)
        create_delay(300)
        trigger_nrt(str(placed_bet_var), 0, "write")
        chip_stacks.take_away_bets()
        amount = int(placed_bet_var.get() / 2)
        result_text.set(f"Player surrendered. You lost {amount} credits.")
        result['bg'] = RESULT_LOSE_COLOR
        result['fg'] = 'white'
        create_delay(NAT_DELAY_TIME)
        flip_hole_card()
        allow_betting()


def double_down(event):
    global players_turn
    global dealer_bj_tally
    global ROUND_IN_SESSION
    if players_turn:
        players_turn = False
        felt.itemconfig("double", activeimage=double_btn_clk_img, image=double_btn_clk_img)
        felt.itemconfig("button", state="disabled")
        felt.update()
        time.sleep(0.05)
        felt.itemconfig("double", activeimage=double_actvbtn_img, image=double_btn_img)
        felt.update()
        felt.itemconfig("button", state="hidden")
        if tiktok_playback:
            # noinspection PyUnresolvedReferences
            if tiktok_playback.is_playing():
                tiktok_playback.stop()
        executor.submit(hide_action_timer)
        hide_action_buttons()
        result_text.set("Player is Doubling Down. GOOD LUCK!")
        sa.WaveObject.from_wave_file(f"sounds\\chipsCollide{random.randint(1, 3)}.wav").play()
        placed_bet_var.set(int(placed_bet_var.get() * 2))
        create_delay(600)
        deal_card(1, dd=True)
        refill_shoe_if_empty()
        mainWindow.update()
        create_delay(NAT_DELAY_TIME)
        if player_score_var.get() > 21:  # To disable buttons before all delays
            create_delay(NAT_DELAY_TIME)
            ROUND_IN_SESSION = False
            players_turn = False
            result_text.set("Player busts! Dealer wins! Better luck next Hand!")
            print(result_text.get())
            create_delay(NAT_DELAY_TIME)
            update_stats()
            flip_hole_card()
            player_lost()
            allow_betting()
        else:
            deal_dealer()


def stats_sheet(card):
    global hc_for_cheatsheet
    global count
    counted[card[3]] = str(int(counted[card[3]]) - 1)
    row_counter = 0
    for key, value in counted.items():
        cheats_frame.winfo_children()[row_counter]['text'] = "{:<3} : {:>3}".format(key, value)
        row_counter += 1
    if is_cheatsheet_on:
        secondWindow.update()
    total = 0
    for card in shoe:
        if not card[4]:
            total += 1
    cheats_frame.winfo_children()[row_counter]['text'] = "{} left in the shoe.".format(total)
    if not is_shoe_empty():
        suit_label['text'] = '{}{}'.format(shoe[0][3], shoe[0][2])
        if shoe[0][2] in '♥♦':
            suit_label['fg'] = "red"
        else:
            suit_label['fg'] = "black"
        if is_cheatsheet_on:
            secondWindow.update()


def deal_card(not_dealer, dd=False):
    global first_card_obj
    # pop the next card off the top of the shoe
    next_card = shoe.pop(0)
    next_card[4] = True
    shoe.append(next_card)
    player_card_x_pos = int((mainWindow.winfo_width() / 2) - 59 + DISTANCE_X * len(player_hand['items']))
    player_card_y_pos = int(mainWindow.winfo_height() * 0.537 - DISTANCE_Y * len(player_hand['items']))
    dealer_card_x_pos = int((mainWindow.winfo_width() / 2 + 59) - 118 * len(dealer_hand['items']))
    dealer_card_y_pos = show_stats_button.winfo_height() + 8
    PlaySound.PlaySound('sounds\\cardPlace{}.wav'.format(random.randint(1, 5)),
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    create_delay(400)
    if not_dealer:
        player_hand['cards'].append(next_card)
        if not dd:
            card_img = felt.create_image(player_card_x_pos, player_card_y_pos, image=next_card[1],
                                         anchor='s', tags=f"card{len(player_hand['cards'])}")
            # felt.move(player_score_digits, 0, -DISTANCE_Y)
        else:
            card_img = felt.create_image(player_card_x_pos + DISTANCE_X, player_card_y_pos - DISTANCE_Y * 2,
                                         image=next_card[5], anchor='se')
            # felt.move(player_score_digits, 0, -(DISTANCE_Y + 20))

        player_hand['items'].append(card_img)
        update_count(next_card)
    else:
        if len(dealer_hand['items']) == 0:
            card_img = felt.create_image(dealer_card_x_pos, dealer_card_y_pos,
                                         image=card_back_image, anchor='nw',
                                         tags='hole_card')
        else:
            update_count(next_card)
            dealer_hand['cards'].append(next_card)
            card_img = felt.create_image(dealer_card_x_pos, dealer_card_y_pos,
                                         image=next_card[1], anchor='nw')
        felt.move(dealer_score_digits, -118, 0)
        dealer_hand['items'].append(card_img)
    if not_dealer:
        player_score_var.set(score_hand(player_hand))
    elif len(dealer_hand['cards']) > 0:
        dealer_score_var.set(score_hand(dealer_hand))
    # create_delay(180)
    if players_turn or dealers_turn:
        result_text.set(update_notif(not_dealer, next_card))
    # now return the card's face value
    return next_card


def score_hand(hand):
    # Calculate the total score of all cards in the list.
    # Only one ace can have a value 11, and this will be reduced to 1 if
    # the hand is a bust.
    score = 0
    global hand_is_soft
    ace = False
    for next_card in hand['cards']:
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
            ace = False  # The hand returns to being hard, since the ace is technically no longer an "Ace"
    return score


def flip_hole_card():
    global hc_for_cheatsheet
    global dealer_bj_tally
    dealer_hand['cards'].insert(0, hole_card)
    hc_for_cheatsheet['text'] = ''
    hc_suit_label['text'] = ''
    mainWindow.update()
    PlaySound.PlaySound('sounds\\cardFlip.wav',
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    create_delay(55)
    for i in range(3, 20, 3):
        animated_flip = tkinter.PhotoImage(file=f"decks\\{themes[theme.get()]['shoe']}\\back{randed_back}flip.gif",
                                           format="gif -index {}".format(i))
        felt.itemconfig(felt.find_withtag('hole_card'), image=animated_flip)
        mainWindow.after(10, mainWindow.update())
    animated_flip = tkinter.PhotoImage(file="")
    felt.itemconfig(felt.find_withtag('hole_card'), image=animated_flip)
    mainWindow.after(10, mainWindow.update())
    create_delay(224)
    update_count(hole_card)
    felt.itemconfig(felt.find_withtag('hole_card'), image=hole_card[1])
    if hole_card[0] == 1:
        result_text.set("Dealer's hole card was the {}{}. Value of 11."
                        .format(hole_card[3], hole_card[2]))
    else:
        result_text.set("Dealer's hole card was the {}{}. Value of {}."
                        .format(hole_card[3], hole_card[2], hole_card[0]))
    dealer_score = score_hand(dealer_hand)
    print("{} Current score - {}.".format(result_text.get(), dealer_score))
    dealer_score_var.set(dealer_score)


def check_for_ace(whos_hand):
    ace_count = 0
    if whos_hand:
        for card in player_hand['cards']:
            if card[0] == 1:
                ace_count += 1
    else:
        for card in dealer_hand['cards']:
            if card[0] == 1:
                ace_count += 1
    return ace_count


dealers_turn = False


def deal_dealer():
    global ROUND_IN_SESSION
    global players_turn
    global hand_is_soft
    global dealers_turn
    global dealer_bj_tally
    dealers_turn = True
    players_turn = False
    hand_is_soft = False
    hide_action_buttons()
    if not player_bj:
        print("Player chose to stand on {}. Dealer's turn.".format(player_score_var.get()))
        flip_hole_card()
        if check_for_bj(dealer_hand, dealer_score_var.get()):
            dealer_bj_tally += 1
        update_bj_stats()
    dealer_score = dealer_score_var.get()
    create_delay(NAT_DELAY_TIME * 0.66)
    compare_scores(player_score_var.get(), dealer_score)
    while 0 < dealer_score <= dealerstand_score and ROUND_IN_SESSION and not cleanup:
        next_card = deal_card(0)
        dealer_score = dealer_score_var.get()
        if len(dealer_hand['cards']) == 2:
            if check_for_bj(dealer_hand, dealer_score):
                dealer_bj_tally += 1
            update_bj_stats()
        print("{} Current score - {}.".format(result_text.get(), dealer_score))
        stats_sheet(next_card)
        create_delay(NAT_DELAY_TIME * 0.66)
        compare_scores(player_score_var.get(), dealer_score)


def compare_scores(player_score, dealer_score):
    global ROUND_IN_SESSION
    global dealers_turn
    global total_rounds_tally
    # global fp_thread
    # if nrt.is_alive():
    #     nrt.join()
    if dealer_score == 21:
        ROUND_IN_SESSION = False
        result_text.set("Dealer reached 21!")
        create_delay(NAT_DELAY_TIME)
    if 21 > dealer_score >= dealerstand_score:
        ROUND_IN_SESSION = False
        if dealer_score == dealerstand_score:
            if dealer_hits_on_soft and hand_is_soft:
                result_text.set("Soft {}. Dealer must keep hitting.".format(dealerstand_score))
                print(result_text.get())
                create_delay(NAT_DELAY_TIME)
                ROUND_IN_SESSION = True
            else:
                result_text.set("Hard {}. Dealer must stand.".format(dealerstand_score))
                print("The Dealer's final score is {}.".format(dealer_score))
                create_delay(NAT_DELAY_TIME)
        else:
            result_text.set("Dealer must stand on or above hard {}.".format(dealerstand_score))
            print("The Dealer's final score is {}.".format(dealer_score))
            create_delay(NAT_DELAY_TIME)
    if dealer_score > 21:
        result_text.set("That's too many!")
        create_delay(NAT_DELAY_TIME)
        ROUND_IN_SESSION = False
    if ROUND_IN_SESSION:
        refill_shoe_if_empty()
    else:
        dealers_turn = False
        if not check_for_bj(dealer_hand, dealer_score):
            if dealer_score > 21:
                result_text.set("Dealer busts! Player wins!")
                player_won()
            elif dealer_score < player_score:
                result_text.set("Player wins!")
                player_won()
            elif dealer_score > player_score:
                result_text.set("Dealer wins! Better luck next Hand!")
                player_lost()
            else:
                result_text.set("Push!")
                felt.itemconfig(player_score_digits, fill=WIN_COLOR,
                                font=font.Font(size=21, weight='bold'))
                felt.itemconfig(dealer_score_digits, fill=WIN_COLOR,
                                font=font.Font(size=21, weight='bold'))

                sound_draw()
        print("{} The score was {} - {}.".format(
            result_text.get(), player_score, dealer_score))
        refill_shoe_if_empty()
        allow_betting()


def check_for_bj(hand, score):
    if score == 21 and len(hand['cards']) == 2:
        return True
    else:
        return False


def update_notif(whos_hand, next_card):
    if whos_hand:
        name = "You were dealt"
    else:
        name = "Dealer drew"

    if next_card[0] == 1:
        if check_for_ace(whos_hand) >= 1:
            str_to_print = "{} the {}{}. Value of 1." \
                .format(name, next_card[3], next_card[2])
        else:
            str_to_print = "{} the {}{}. Value of 11." \
                .format(name, next_card[3], next_card[2])
    else:
        str_to_print = "{} the {}{}. Value of {}." \
            .format(name, next_card[3], next_card[2], next_card[0])
    return str_to_print


def deal_player():
    global player_bj
    global player_bj_tally
    global player_bj_label
    global ROUND_IN_SESSION
    global players_turn
    global dealer_bj_tally
    next_card = deal_card(1)
    player_score = player_score_var.get()
    if player_score < 10:
        update_bj_stats()
    stats_sheet(next_card)
    create_delay(NAT_DELAY_TIME // 4)
    print("{} Current score - {}.".format(update_notif(player_hand, next_card), player_score))
    if players_turn:
        if len(player_hand['cards']) == 2:
            player_bj_label['text'] = "Player BLACKJACKS:\t{0}, {1:>3.2f}%" \
                .format(player_bj_tally, player_bj_tally * 100 / total_rounds_tally)
            player_bj_label.update()
        if player_score == 21:
            hide_action_buttons()
            players_turn = False
            create_delay(NAT_DELAY_TIME)
            result_text.set("21! Congratulations! Dealer will now try to match.")
            print(result_text.get())
            felt.itemconfig(player_score_digits, fill=WIN_COLOR)
            create_delay(NAT_DELAY_TIME)
            refill_shoe_if_empty()
            deal_dealer()
        elif player_score > 21:
            hide_action_buttons()
            create_delay(NAT_DELAY_TIME)
            ROUND_IN_SESSION = False
            players_turn = False
            result_text.set("Player busts! Dealer wins! Better luck next Hand!")
            print(result_text.get())
            player_lost()
            create_delay(NAT_DELAY_TIME)
            update_stats()
            flip_hole_card()
            if check_for_bj(dealer_hand, dealer_score_var.get()):
                dealer_bj_tally += 1
                sa.WaveObject.from_wave_file(f"sounds\\dealer_bj{random.randint(1, 2)}.wav").play()
                flash_bg_fg_widgets(10, RESULT_LOSE_COLOR, 'black', result,
                                    leave_button, show_stats_button,
                                    style='wavy')
                result_text.set("Dealer was holding BLACKJACK!")
                update_bj_stats()
                create_delay(NAT_DELAY_TIME)
            else:
                update_bj_stats()
            refill_shoe_if_empty()
            create_delay(700)
            allow_betting()
        refill_shoe_if_empty()
        if players_turn:
            # felt.move("button", 0, -DISTANCE_Y)
            result_text.set(
                result_text.get() + " {} vs {}. Your call.".format(player_score_var.get(), dealer_score_var.get()))
            executor.submit(reset_action_timer)


outcome = ''


def player_won():
    global p_w_tally
    global rounds_player_won
    global outcome
    mainWindow.update()
    p_w_tally += 1
    outcome = f"Player won {player_score_var.get()} to {dealer_score_var.get()}."
    result['bg'] = RESULT_WIN_COLOR
    result['fg'] = 'navy'
    felt.itemconfig(dealer_score_digits, font=font.Font(size=18, overstrike=1, weight='bold'), fill=LOSE_COLOR)
    felt.itemconfig(player_score_digits, font=font.Font(size=18, underline=1, weight='bold'), fill=WIN_COLOR)
    update_stats()
    if player_bj:
        sa.WaveObject.from_wave_file("sounds\\player_BJ.wav").play()
        flash_bg_fg_widgets(10, '#bf40bf', 'white', result, leave_button, show_stats_button,
                            style='wavy')
        win_amount = int(placed_bet_var.get() * 1.5)
    else:
        sa.WaveObject.from_wave_file(f'sounds\\jasonwin_{random.randint(1, 3)}.wav').play()
        flash_bg_fg_widgets(6, RESULT_WIN_COLOR, 'white', result)
        win_amount = int(placed_bet_var.get() * 1)
    chip_stacks.pay_player(player_bj)
    result_text.set(f"You won {win_amount} credits.")

    mainWindow.update()


def update_stats():
    rounds_dealer_won['text'] = "Hands lost:\t\t{0}, {1:>3.2f}%" \
        .format(d_w_tally, d_w_tally * 100 / total_rounds_tally)
    rounds_player_won['text'] = "Hands won:\t\t{0}, {1:>3.2f}%" \
        .format(p_w_tally, p_w_tally * 100 / total_rounds_tally)
    rounds_draw['text'] = "Hands pushed:\t\t{}, {:>3.2f}%" \
        .format(draw_tally, draw_tally * 100 / total_rounds_tally)
    secondWindow.update()


def player_lost(by_bj=False):
    global d_w_tally
    global rounds_dealer_won
    global outcome
    mainWindow.update()
    d_w_tally += 1
    outcome = f"Player lost {player_score_var.get()} to {dealer_score_var.get()}."
    update_stats()
    result['bg'] = RESULT_LOSE_COLOR
    felt.itemconfig(dealer_score_digits, fill=WIN_COLOR,
                    font=font.Font(size=18, weight='bold', underline=1))
    felt.itemconfig(player_score_digits, fill=LOSE_COLOR,
                    font=font.Font(size=18, weight='bold', overstrike=1))
    # sa.WaveObject.from_wave_file('sounds\\you_lose.wav').play()
    if by_bj:
        sa.WaveObject.from_wave_file(f"sounds\\dealer_bj{random.randint(1, 2)}.wav").play()
        flash_bg_fg_widgets(10, RESULT_LOSE_COLOR, 'black', leave_button,
                            show_stats_button, result, style='wavy')
    else:
        sa.WaveObject.from_wave_file(f'sounds\\jasonlose_{random.randint(1, 3)}.wav').play()
        flash_bg_fg_widgets(6, RESULT_LOSE_COLOR, 'black', result)
    chip_stacks.take_away_bets()
    sa.WaveObject.from_wave_file("sounds\\chipsHandle{}.wav".format(random.randint(1, 5))).play()
    mainWindow.update()


def sound_draw():
    global draw_tally
    global rounds_draw
    global outcome
    draw_tally += 1
    outcome = f"Hand was pushed on {player_score_var.get()}."
    update_stats()
    sa.WaveObject.from_wave_file('sounds\\draw.wav').play()
    mainWindow.update()


def first_play():
    global dealer_hand, player_hand, deck_ready, players_turn
    global dealer_bj_tally, player_bj, ROUND_IN_SESSION
    global player_score_var, dealer_score_var
    global hole_card
    global hc_for_cheatsheet
    global hc_suit_label
    global first_card_obj
    global total_rounds_tally, player_bj_tally
    global nrt_seconds_left
    global table_cleared
    if not cleanup:
        deck_ready = False
        load_back_of_card()
        deal_player()
        table_cleared = False
        hole_card = deal_card(0)
        if hole_card[2] in '♥♦':
            hc_suit_label['fg'] = "red"
        else:
            hc_suit_label['fg'] = "black"
        if is_cheatsheet_on:
            secondWindow.update()
        stats_sheet(hole_card)
        create_delay(NAT_DELAY_TIME // 3)
        hc_for_cheatsheet['text'] = "Dealer's hole card is: "
        hc_suit_label['text'] = "{}{}".format(hole_card[3], hole_card[2])
        refill_shoe_if_empty()
        nrt_seconds_left = TIME_BETWEEN_ROUNDS
        deal_player()
        next_card = deal_card(0)
        if next_card[0] == 1:
            dealer_score_var.set(11)
        else:
            dealer_score_var.set(next_card[0])
        print("{} Current score - {}.".format(update_notif(0, next_card), dealer_score_var.get()))
        if dealer_score_var.get() < 10:
            update_bj_stats()
        stats_sheet(next_card)
        player_bj = check_for_bj(player_hand, player_score_var.get())
        if player_bj:
            result_text.set("Winner Winner, Chicken Dinner!")
            print(result_text.get())
            player_bj_tally += 1
            player_bj_label['text'] = "Player BLACKJACKS:\t{0}, {1:>3.2f}%" \
                .format(player_bj_tally, player_bj_tally * 100 / total_rounds_tally)
            player_bj_label.update()
            secondWindow.update()
            hide_action_buttons()
            felt.itemconfig(player_score_digits, fill=WIN_COLOR)
            create_delay(NAT_DELAY_TIME // 2)
            if dealer_score_var.get() < 10:
                player_won()
                flip_hole_card()
                players_turn = False
                ROUND_IN_SESSION = False
            else:
                result_text.set("Checking for good Blackjack...")
                flip_hole_card()
                players_turn = False
                ROUND_IN_SESSION = False
                create_delay(800)
                if dealer_score_var.get() == 21:
                    dealer_bj_tally += 1
                    update_bj_stats()
                    result_text.set("Dealer got BLACKJACK as well! It's a Push.")
                    felt.itemconfig(player_score_digits, fill=WIN_COLOR,
                                    font=font.Font(size=18, weight='bold'))
                    felt.itemconfig(dealer_score_digits, fill=WIN_COLOR,
                                    font=font.Font(size=18, weight='bold'))
                    sa.WaveObject.from_wave_file(f"sounds\\dealer_bj{random.randint(1, 2)}.wav").play()
                    flash_bg_fg_widgets(10, RESULT_LOSE_COLOR, 'black', leave_button,
                                        show_stats_button, result, style='wavy')
                    sound_draw()
                    create_delay(NAT_DELAY_TIME)
                else:
                    result_text.set("Dealer didn't have BLACKJACK, Player's BLACKJACK Wins!")
                    player_won()
                    create_delay(NAT_DELAY_TIME)
            allow_betting()
        elif dealer_score_var.get() >= 10:
            dealer_hand['cards'].insert(0, hole_card)
            result_text.set("Dealer peaks for Blackjack.")
            score_to_check = score_hand(dealer_hand)
            dealer_hand['cards'].pop(0)
            create_delay(700)
            if score_to_check == 21:
                dealer_bj_tally += 1
                update_bj_stats()
                flip_hole_card()
                ROUND_IN_SESSION = False
                result_text.set("Blackjack! Dealer wins! Better luck next Hand!")
                # sa.WaveObject.from_wave_file(f"sounds\\ouch{random.randint(1, 4)}.wav").play()
                player_lost(by_bj=True)
                allow_betting()
            else:
                result_text.set("Nobody home.")
                refill_shoe_if_empty()
                create_delay(700)
                result_text.set("{},{} vs the Dealer's {}. Your call.".
                                format(player_hand['cards'][0][3], player_hand['cards'][1][3],
                                       dealer_hand['cards'][0][3]))
                print(result_text.get())
                ROUND_IN_SESSION = True
                players_turn = True
                show_special_options()
                executor.submit(reset_action_timer)
        else:
            refill_shoe_if_empty()
            create_delay(600)
            result_text.set("{},{} vs the Dealer's {}. Your call.".
                            format(player_hand['cards'][0][3], player_hand['cards'][1][3], dealer_hand['cards'][0][3]))
            print(result_text.get())
            ROUND_IN_SESSION = True
            players_turn = True
            show_special_options()
            executor.submit(reset_action_timer)


# noinspection PyUnboundLocalVariable
def flash_bg_fg_widgets(times, color1, color2, *items, style="default"):
    temp = []
    for item in items:
        temp.append((item['fg'], item['bg']))

    if style == "default":  # DEFAULT FLASH
        for i in range(1, times + 1):
            for item in items:
                item['bg'] = color1
                item['fg'] = invert_color(item, color1)
                # create_delay(200/times)
            create_delay(240 / times, item)
            for item in items:
                item['bg'] = color2
                item['fg'] = invert_color(item, color2)
                # create_delay(200 / times)
            create_delay(240 / times, item)
        create_delay(120, item)
        for item in items:
            item['fg'] = temp[items.index(item)][0]
            item['bg'] = temp[items.index(item)][1]
    # WAVY FLASH
    elif style == "wavy":
        for i in range(1, times + 1):
            for item in items:
                item['bg'] = color1
                item['fg'] = invert_color(item, color1)
                if items.index(item) < len(items) - 2:
                    next_item = items.__getitem__(items.index(item) + 1)
                    next_item['bg'] = color2
                    next_item['fg'] = invert_color(item, color2)
                else:
                    items.__getitem__(0)['bg'] = color2
                    items.__getitem__(0)['fg'] = invert_color(item, color2)
                create_delay(10, item)
                item['fg'] = invert_color(item, color2)
                if items.index(item) < len(items) - 2:
                    next_item = items.__getitem__(items.index(item) + 1)
                    next_item['bg'] = color1
                    next_item['fg'] = invert_color(item, color1)
                else:
                    items.__getitem__(0)['bg'] = color1
                    items.__getitem__(0)['fg'] = invert_color(item, color1)
                create_delay(10, item)
                item['fg'] = temp[items.index(item)][0]
                item['bg'] = temp[items.index(item)][1]
                create_delay(10, item)
        # create_delay(300)
        for item in items:
            item['fg'] = temp[items.index(item)][0]
            item['bg'] = temp[items.index(item)][1]


def change_d_score(varname, index, mode):
    global dealer_score_digits_img
    if mainWindow.getvar(varname) == 0:
        felt.itemconfigure(dealer_score_digits, state='hidden')
        felt.itemconfig(dealer_score_digits_img, state='hidden')
    else:
        felt.itemconfigure(dealer_score_digits, state='normal', text=mainWindow.getvar(varname))
        felt.itemconfig(dealer_score_digits_img, state='normal')
        felt.moveto(dealer_score_digits_img, felt.coords(dealer_score_digits)[0] - 39,
                    felt.coords(dealer_score_digits)[1] - 43)
        felt.lower(dealer_score_digits_img, dealer_score_digits)


def change_p_score(varname, index, mode):
    global player_score_digits_img
    if mainWindow.getvar(varname) == 0:
        felt.itemconfigure(player_score_digits, state='hidden')
        felt.itemconfig(player_score_digits_img, state='hidden')
    else:
        felt.itemconfigure(player_score_digits, state='normal', text=mainWindow.getvar(varname))
        felt.itemconfig(player_score_digits_img, state='normal')
        felt.moveto(player_score_digits_img, felt.coords(player_score_digits)[0] - 39,
                    felt.coords(player_score_digits)[1] - 43)
        felt.lower(player_score_digits_img, player_score_digits)


def shuffle():
    global deck_ready
    global count
    global ROUND_IN_SESSION
    if not cleanup:
        ROUND_IN_SESSION = True
        if not table_cleared and not clearing_table:
            clear_table()
        while clearing_table:
            time.sleep(0.1)
        for card in discard_pile:
            shoe.append(card)
        discard_pile.clear()
        count = [0, 0, no_of_decks, 0.0]
        random.shuffle(shoe)
        hint_var.set("Shuffling...")
        print("Shuffling the shoe...")
        sa.WaveObject.from_wave_file('sounds\\shufflemachine.wav').play().wait_done()
        reset_counted()
        deck_ready = True
        hint_var.set("")
        trigger_newround('event')


def say_goodbye():
    global cleanup
    hint_var.set("Shutting down...")
    result_text.set("Goodbye! See you next time! :)")
    executor.shutdown()
    print(result_text.get())
    if is_cheatsheet_on:
        secondWindow.update()
    create_delay(990)
    cleanup = True


mainWindow = tkinter.Tk()
import chip_stacks

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
mainWindow.overrideredirect(1)
secondWindow.overrideredirect(1)
theme = tkinter.StringVar(mainWindow, 'oldschool')
LOSE_COLOR = themes[theme.get()]['lose_color']  # The score digits color in case the player loses
WIN_COLOR = themes[theme.get()]['win_color']  # The score digits color in case the player win
FELT_COLOR = tkinter.StringVar(mainWindow, themes[theme.get()]['felt_color'])  # The color of the table felt
bas_str_btn_bg = themes[theme.get()]['bas_strat_btn_bg']  # Standard background color for the buttons
boldFont = tkinter.font.Font(size=15, weight="bold")
count = [0, 0, no_of_decks, 0.0]
shoe = []
cards = []
load_chosen_set(cards)
for j in range(1, no_of_decks + 1):
    for card_ in cards:
        shoe.append(card_)
init_stats_sheet()
dealer_hand = {"cards": [], "items": []}
player_hand = {"cards": [], "items": []}
cards_slides = [sa.WaveObject.from_wave_file("sounds\\cardSlide2.wav"),
                sa.WaveObject.from_wave_file("sounds\\cardSlide3.wav")
                ]
discard_pile = []
no_decks_for_BS = no_of_decks
if 1 < no_of_decks < 4:
    no_decks_for_BS = 2
elif no_of_decks >= 4:
    no_decks_for_BS = 4
mainWindow.geometry("{}x{}+0+0".format(mainWindow.winfo_screenwidth(),  # //4 * 3,
                                       mainWindow.winfo_screenheight()))  # //4 * 3))
DISTANCE_X = 40
DISTANCE_Y = 28

mainWindow.resizable(False, False)
secondWindow.update()
mainWindow.title("Vit's Blackjack Table")
secondWindow.wm_attributes("-topmost", 1)
mainWindow.grid_columnconfigure(0, weight=1)
mainWindow.config(bg='#86592d')
mainWindow.pack_propagate(0)

felt = tkinter.Canvas(mainWindow, height=int(mainWindow.winfo_height()),  # * 0.66),
                      width=mainWindow.winfo_width(), highlightthickness=0,
                      bg=FELT_COLOR.get(), cursor="hand2")  # , relief='groove', borderwidth='3')
felt.pack(side='top')
felt.propagate(0)
# if round(mainWindow.winfo_screenwidth() / mainWindow.winfo_screenheight(), 2) == 1.78:
#     bgimagepath = Image.open(f"graphics\\{theme.get()}BG16x9.png")
# else:
# bgimagepath = Image.open(f"graphics\\{theme.get()}BG.jpg")
bgimagepath = Image.open(f"graphics\\{themes[theme.get()]['bg']}")
# if not mainWindow.winfo_screenheight() == 1080:
#     bgimagepath = bgimagepath.resize((mainWindow.winfo_width(),
#                                       int(mainWindow.winfo_width() //
#                                           (bgimagepath.width / bgimagepath.height))), Image.LANCZOS)

bgimage = ImageTk.PhotoImage(bgimagepath)
felt.create_image(mainWindow.winfo_width() // 2, mainWindow.winfo_height() // 2,
                  image=bgimage, tags="back_image")
armrest_path = Image.open(f"graphics\\{themes[theme.get()]['armrest']}")
armrest_img = ImageTk.PhotoImage(armrest_path)
felt.create_image(mainWindow.winfo_width() // 2, mainWindow.winfo_height(),
                  image=armrest_img, tags='armrest', anchor='s', state='disabled')

upper_frame = tkinter.Frame(felt, width=mainWindow.winfo_width())
upper_frame.place(x=0, y=0, anchor='nw')
show_stats_button = tkinter.Button(upper_frame, text='Hide Stats Sheet (s)',
                                   command=hide_stats_sheet, bg='black',
                                   width=12, height=2, fg='white',
                                   font=font.Font(size=10), wraplength=100)
show_stats_button.pack(side='left', anchor='nw')
result_frame = tkinter.Frame(upper_frame,
                             height=show_stats_button.winfo_reqheight(),
                             width=mainWindow.winfo_width() - 2 * show_stats_button.winfo_reqwidth())
result_frame.pack(side='left')  # , fill=tkinter.BOTH, expand=1)
result_frame.pack_propagate(0)

# show_stats_button.grid(row=0, column=0, sticky='nsew')
mainWindow.update()
result_text = tkinter.StringVar()
result_text.set("🂡🂫 Welcome to the BLACKJACK table! 🂫🂡")

result = tkinter.Label(result_frame, background=RESULT_BG_COLOR, fg='white',
                       textvariable=result_text, font=font.Font(size=14),
                       relief='raised', height=1)
result.pack(fill=tkinter.BOTH, expand=1)
leave_button = tkinter.Button(upper_frame, text='Leave Table (Esc)', font=font.Font(size=10),
                              command=quit, height=2, width=12, wraplength=100,
                              bg='black', fg='white')
leave_button.pack(side='left', anchor="ne")
mainWindow.bind('Escape', quit)
mainWindow.update()

print("now", felt.winfo_height())  # TODO: Remove this
hint_var = tkinter.StringVar(mainWindow, "")
hint_queue_var = tkinter.IntVar(mainWindow, 0)
hint_frame = tkinter.Frame(felt, relief='raised', bd=2)
hint_var.trace_add("write", show_hide_hint_frame)
hint = tkinter.Label(hint_frame, font=boldFont, textvariable=hint_var,
                     fg=themes[theme.get()]['stand_btn_fg'], bg=RESULT_BG_COLOR,
                     compound='bottom', padx=5, pady=2)
hint.pack(side='top', fill=tkinter.BOTH, expand=1)
betting_frame = tkinter.Frame(felt, height=100, width=780,
                              bg=FELT_COLOR.get(), highlightthickness=2,
                              highlightcolor=themes[theme.get()]['card_frame_lbl_fg'],
                              relief='groove', bd=2)
betting_frame.place(y=mainWindow.winfo_height() * (960/1080), relx=0.5, anchor='center')
felt.columnconfigure(0, weight=1)

bankroll = tkinter.DoubleVar()
bankroll.set(int(starting_total))
player_total_label = tkinter.Label(betting_frame, text='Your total:',
                                   background=FELT_COLOR.get(), fg=themes[theme.get()]['card_frame_lbl_fg'])
player_total_label.grid(row=0, column=0, sticky='s', pady=4)
player_total_no = tkinter.Label(betting_frame,  # width=12,
                                textvariable=bankroll,
                                font=font.Font(size=18), background=FELT_COLOR.get(),
                                fg=themes[theme.get()]['card_frame_lbl_fg'])
player_total_no.grid(row=1, column=0, sticky='wes', pady=4)
placed_bet_var = tkinter.DoubleVar(mainWindow, 0)
placed_bet_var.trace_add('write', trigger_nrt)

chip_stacks.load_everything(felt, mainWindow, placed_bet_var, bankroll)
felt.tag_raise('armrest')
#
# placed_bet_label = tkinter.Label(betting_frame, text='Place your bet:',
#                                  background=FELT_COLOR.get(), fg=themes[theme.get()]['card_frame_lbl_fg'])
# placed_bet_label.grid(row=0, column=2, sticky='s', pady=4)
#
# placed_bet_no = tkinter.Label(betting_frame, bd=0, textvariable=placed_bet_var, width=12,
#                               font=font.Font(size=18), background=FELT_COLOR.get(),
#                               fg=themes[theme.get()]['card_frame_lbl_fg'])
# placed_bet_no.grid(row=1, column=2, sticky='es', pady=4)

hit_btn_path = Image.open("graphics\\hit2.png")
hit_actvbtn_path = Image.open("graphics\\hitactive2.png")
hit_btn_clk_path = Image.open("graphics\\hitclick2.png")
hit_btn_img = ImageTk.PhotoImage(image=hit_btn_path)
hit_actvbtn_img = ImageTk.PhotoImage(image=hit_actvbtn_path)
hit_btn_clk_img = ImageTk.PhotoImage(image=hit_btn_clk_path)
stand_btn_path = Image.open("graphics\\stand2.png")
stand_actvbtn_path = Image.open("graphics\\standactive2.png")
stand_btn_clk_path = Image.open("graphics\\standclick2.png")
stand_btn_img = ImageTk.PhotoImage(image=stand_btn_path)
stand_actvbtn_img = ImageTk.PhotoImage(image=stand_actvbtn_path)
stand_btn_clk_img = ImageTk.PhotoImage(image=stand_btn_clk_path)
help_btn_path = Image.open("graphics\\help2.png")
help_actvbtn_path = Image.open("graphics\\helpactive2.png")
help_btn_clk_path = Image.open("graphics\\helpclick2.png")
help_btn_img = ImageTk.PhotoImage(image=help_btn_path)
help_actvbtn_img = ImageTk.PhotoImage(image=help_actvbtn_path)
help_btn_clk_img = ImageTk.PhotoImage(image=help_btn_clk_path)
double_btn_path = Image.open("graphics\\double.png")
double_actvbtn_path = Image.open("graphics\\doubleactive.png")
double_btn_clk_path = Image.open("graphics\\doubleclick.png")
double_btn_img = ImageTk.PhotoImage(image=double_btn_path)
double_actvbtn_img = ImageTk.PhotoImage(image=double_actvbtn_path)
double_btn_clk_img = ImageTk.PhotoImage(image=double_btn_clk_path)
split_btn_path = Image.open("graphics\\split.png")
split_actvbtn_path = Image.open("graphics\\splitactive.png")
split_btn_clk_path = Image.open("graphics\\splitclick.png")
split_btn_img = ImageTk.PhotoImage(image=split_btn_path)
split_actvbtn_img = ImageTk.PhotoImage(image=split_actvbtn_path)
split_btn_clk_img = ImageTk.PhotoImage(image=split_btn_clk_path)
surrender_btn_path = Image.open("graphics\\surrender2.png")
surrender_actvbtn_path = Image.open("graphics\\surrenderactive2.png")
surrender_btn_clk_path = Image.open("graphics\\surrenderclick2.png")
surrender_btn_img = ImageTk.PhotoImage(image=surrender_btn_path)
surrender_actvbtn_img = ImageTk.PhotoImage(image=surrender_actvbtn_path)
surrender_btn_clk_img = ImageTk.PhotoImage(image=surrender_btn_clk_path)
ready_btn_path = Image.open("graphics\\ready2.png")
ready_actvbtn_path = Image.open("graphics\\readyactive2.png")
ready_btn_clk_path = Image.open("graphics\\readyclick2.png")
ready_disabled_path = Image.open("graphics\\readydisabled2.png")
ready_disabled_img = ImageTk.PhotoImage(image=ready_disabled_path)
ready_btn_img = ImageTk.PhotoImage(image=ready_btn_path)
ready_actvbtn_img = ImageTk.PhotoImage(image=ready_actvbtn_path)
ready_btn_clk_img = ImageTk.PhotoImage(image=ready_btn_clk_path)
newshoe_btn_path = Image.open("graphics\\newshoe.png")
newshoe_actvbtn_path = Image.open("graphics\\newshoeactive.png")
newshoe_btn_clk_path = Image.open("graphics\\newshoeclick.png")
newshoe_disabled_path = Image.open("graphics\\newshoedisabled.png")
newshoe_disabled_img = ImageTk.PhotoImage(image=newshoe_disabled_path)
newshoe_btn_img = ImageTk.PhotoImage(image=newshoe_btn_path)
newshoe_actvbtn_img = ImageTk.PhotoImage(image=newshoe_actvbtn_path)
newshoe_btn_clk_img = ImageTk.PhotoImage(image=newshoe_btn_clk_path)
buyin_btn_path = Image.open("graphics\\buyin.png")
buyin_actvbtn_path = Image.open("graphics\\buyinactive.png")
buyin_btn_clk_path = Image.open("graphics\\buyinclick.png")
buyin_btn_img = ImageTk.PhotoImage(image=buyin_btn_path)
buyin_actvbtn_img = ImageTk.PhotoImage(image=buyin_actvbtn_path)
buyin_btn_clk_img = ImageTk.PhotoImage(image=buyin_btn_clk_path)
leave_btn_path = Image.open("graphics\\leave.png")
leave_actvbtn_path = Image.open("graphics\\leaveactive.png")
leave_btn_clk_path = Image.open("graphics\\leaveclick.png")
leave_btn_img = ImageTk.PhotoImage(image=leave_btn_path)
leave_actvbtn_img = ImageTk.PhotoImage(image=leave_actvbtn_path)
leave_btn_clk_img = ImageTk.PhotoImage(image=leave_btn_clk_path)
button_row_posx = mainWindow.winfo_width() // 2 - 240  # + 55
button_row_posy = mainWindow.winfo_height() // 2 + 10
buttongbg = Image.open(f"graphics\\{themes[theme.get()]['buttonbg']}")
buttongbg_img = ImageTk.PhotoImage(image=buttongbg)
buttonbg_obj = felt.create_image(button_row_posx - 6, button_row_posy - 48,
                                 image=buttongbg_img, anchor='nw',
                                 tags=("button", "normal_action"), state="hidden")

hit_btn_obj = felt.create_image(mainWindow.winfo_width() * (1106 / 2560), mainWindow.winfo_height() * (960 / 1080),
                                image=hit_btn_img, activeimage=hit_actvbtn_img,
                                tags=("button", "hit", "normal_action"), state="hidden")
stand_btn_obj = felt.create_image(mainWindow.winfo_width() * (1454 / 2560), mainWindow.winfo_height() * (960 / 1080),
                                  image=stand_btn_img, activeimage=stand_actvbtn_img,
                                  tags=("button", "stand", "normal_action"), state="hidden")
help_btn_obj = felt.create_image(mainWindow.winfo_width() * (913 / 2560), mainWindow.winfo_height() * (949 / 1080),
                                 image=help_btn_img, activeimage=help_actvbtn_img,
                                 tags=("button", "help", "normal_action"), state="hidden")
double_btn_obj = felt.create_image(button_row_posx + 18, button_row_posy + 40, image=double_btn_img,
                                   activeimage=double_actvbtn_img, anchor='sw',
                                   tags=("button", "double", "special"), state="hidden")
split_btn_obj = felt.create_image(button_row_posx + 54, button_row_posy + 40, image=split_btn_img,
                                  activeimage=split_actvbtn_img, anchor='sw',
                                  tags=("button", "split", "special"), state="hidden")
surrender_btn_obj = felt.create_image(mainWindow.winfo_width() * (1647 / 2560),
                                      mainWindow.winfo_height() * (949 / 1080),
                                      image=surrender_btn_img, activeimage=surrender_actvbtn_img,
                                      tags=("button", "surrender", "special"), state="hidden")
ready_btn_obj = felt.create_image(mainWindow.winfo_width() * (1106 / 2560), mainWindow.winfo_height() * (960 / 1080),
                                  image=ready_btn_img, disabledimage=ready_disabled_img,
                                  activeimage=ready_actvbtn_img,
                                  tags=("ready", "end"), state="disabled")
newshoe_btn_obj = felt.create_image(mainWindow.winfo_width() * 0.54, mainWindow.winfo_height() * 0.8,
                                    image=newshoe_btn_img, disabledimage=newshoe_disabled_img,
                                    activeimage=newshoe_actvbtn_img, anchor='nw',
                                    tags=("newshoe", "end"), state="disabled")
buyin_btn_obj = felt.create_image(mainWindow.winfo_width() / 2 - 76, mainWindow.winfo_height() / 2 + 20,
                                  image=buyin_btn_img,
                                  activeimage=buyin_actvbtn_img, anchor='ne',
                                  tags=("buyin", "gameover"), state="hidden")
leave_btn_obj = felt.create_image(mainWindow.winfo_width() / 2 + 76, mainWindow.winfo_height() / 2 + 20,
                                  image=leave_btn_img,
                                  activeimage=leave_actvbtn_img, anchor='nw',
                                  tags=("leave", "gameover"), state="hidden")
felt.tag_bind("hit", "<ButtonPress-1>", trigger_hit)
felt.tag_bind("stand", "<ButtonPress-1>", trigger_stand)
felt.tag_bind("help", "<ButtonPress-1>", trigger_check_bas_strat)
felt.tag_bind("help", "<ButtonPress-3>", trigger_show_count)
felt.tag_bind("surrender", "<ButtonPress-1>", surrender)
felt.tag_bind("double", "<ButtonPress-1>", double_down)
felt.tag_bind("ready", "<ButtonPress-1>", trigger_newround)
felt.tag_bind("newshoe", "<ButtonPress-1>", trigger_shuffle)
felt.tag_bind("buyin", "<ButtonPress-1>", reset_everything)
felt.tag_bind("leave", "<ButtonPress-1>", quit)
mainWindow.bind('<asterisk>', lambda event: trigger_show_count(event))
felt.grid_propagate(0)
print("this", felt.winfo_height())  # TODO: Remove this
player_score_digits_orig_pos = (mainWindow.winfo_width() // 2 - 186,
                                mainWindow.winfo_height() // 2 - 86)
dealer_score_digits_orig_pos = ((mainWindow.winfo_width() // 2) + 115, 130)
dealer_score_var = tkinter.IntVar()
dealer_score_var.trace_add('write', change_d_score)
player_score_var = tkinter.IntVar()
player_score_var.trace_add('write', change_p_score)
color_up = tkinter.Radiobutton(felt.master, text="Color up.", value=True,
                               variable=chip_stacks.color_up_var,
                               indicatoron=False)
match_color = tkinter.Radiobutton(felt.master, text="Match Colors.", value=False,
                                  variable=chip_stacks.color_up_var,
                                  indicatoron=False)
felt.create_window(300, 300, window=color_up, anchor='sw')
felt.create_window(300, 300, window=match_color, anchor='nw')
score_digits_bgpath = Image.open(f"graphics\\{themes[theme.get()]['scorebg']}")
score_digits_bg = ImageTk.PhotoImage(image=score_digits_bgpath)
dealer_score_digits_img = felt.create_image(dealer_score_digits_orig_pos,
                                            image=score_digits_bg,
                                            anchor='center',
                                            tags="dealer_score")
player_score_digits_img = felt.create_image(player_score_digits_orig_pos,
                                            image=score_digits_bg,
                                            tags="player_score")

dealer_score_digits = felt.create_text(dealer_score_digits_orig_pos,
                                       fill=themes[theme.get()]['card_frame_lbl_fg'],
                                       font=font.Font(size=18), text=dealer_score_var.get(),
                                       anchor='center', justify='center')
player_score_digits = felt.create_text(player_score_digits_orig_pos, font=font.Font(size=18),
                                       fill=themes[theme.get()]['card_frame_lbl_fg'],
                                       text=player_score_var.get(), justify='center')
player_score_var.set(0)
dealer_score_var.set(0)
atexit.register(say_goodbye)

mainWindow.update()

secondWindow.geometry("300x{}+120+0".format(mainWindow.winfo_height()))
secondWindow.lift()
hide_count_sheet()
tiktok_wav = sa.WaveObject.from_wave_file('sounds\\stopwatch-old1.wav')
tiktok_playback = []
oldschooltimer_animation = []
for j in range(125):
    result_text.set(f"Loading stopwatch animation ({round((j / 124) * 100, 2)}%)")
    result.update()
    timer_bg = tkinter.PhotoImage(file="graphics\\stopwatch1.gif",
                                  format=f"gif -index {j}")
    oldschooltimer_animation.append(timer_bg)
for item in themes.keys():
    if not item == 'oldschool':
        for i in range(26):
            result_text.set(f"Loading timers animation ({round((i / 25) * 100, 2)}%)")
            result.update()
            timer_bg = tkinter.PhotoImage(file=f"graphics\\{themes[item]['timer_name']}{i}.png")
            themes[item]['timer_images'].append(timer_bg)

result_text.set("")

random.shuffle(shoe)

# shoe.insert(0, {0: cards[24][0], 1: cards[24][1], 2: cards[24][2], 3: cards[24][3], 4: cards[24][4], 5: cards[24][5]})
# shoe.insert(1, {0: cards[26][0], 1: cards[26][1], 2: cards[26][2], 3: cards[26][3], 4: cards[26][4], 5: cards[26][5]})
# shoe.insert(2, {0: cards[9][0], 1: cards[9][1], 2: cards[9][2], 3: cards[9][3], 4: cards[9][4], 5: cards[9][5]})
# shoe.insert(3, {0: cards[7][0], 1: cards[7][1], 2: cards[7][2], 3: cards[7][3], 4: cards[7][4], 5: cards[7][5]})
# shoe.insert(4, {0: cards[9][0], 1: cards[9][1], 2: cards[9][2], 3: cards[9][3], 4: cards[9][4], 5: cards[9][5]})
# shoe.insert(6, {0: cards[26][0], 1: cards[26][1], 2: cards[26][2], 3: cards[26][3], 4: cards[26][4], 5: cards[26][5]})
# shoe.insert(2, {0: cards[51][0], 1: cards[51][1], 2: cards[51][2], 3: cards[51][3], 4: cards[51][4], 5: cards[51][5]})
# shoe.insert(3, {0: cards[51][0], 1: cards[51][1], 2: cards[51][2], 3: cards[51][3], 4: cards[51][4], 5: cards[51][5]})
# shoe.insert(2, {0: 1, 1: cards[0][1], 2: cards[0][2], 3: cards[0][3], 4: cards[0][4], 5: cards[0][5]})
# shoe.insert(3, {0: 1, 1: cards[0][1], 2: cards[0][2], 3: cards[0][3], 4: cards[0][4], 5: cards[0][5]})
# shoe.insert(3, {0: 1, 1: cards[0][1], 2: cards[0][2], 3: cards[0][3], 4: cards[0][4], 5:cards[0][5]})
# shoe.insert(0, {0: 9, 1: cards[8][1], 2: 'H', 3: 'A', 4: False})
# shoe.insert(2, {0: 9, 1: cards[21][1], 2: 'H', 3: 'A', 4: False})
mainWindow.update()
allow_betting()
mainWindow.mainloop()
