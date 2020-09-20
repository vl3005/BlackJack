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

LOSE_COLOR = '#453841'  # The score digits color in case the player loses
WIN_COLOR = '#FFD800'  # The score digits color in case the player win
FELT_COLOR = '#339933'  # The color of the table felt
RESULT_BG_COLOR = "navy"  # Background color of the result label
ACTION_TIME = 24  # The time the dealer waits before the player forfeits his say
BTN_BG = '#ffecb3'  # Standard background color for the buttons
timer_visible = False  # Set to true if the timer is displayed
PLAYERS_TURN = False  # Set to true whenever it's the player say
timer_label = None  # Holder for the timer
ROUND_IN_SESSION = False  # Set to true if cards are being dealt
RESULT_LOSE_COLOR = "#990000"  # Background color of result label if the player loses
RESULT_WIN_COLOR = 'gold'  # Background color of result label if the player wins
NAT_DELAY_TIME = 1270  # Natural delay time between result label updates
dealerstand_score = 17  # The score in which the dealer can't hit anymore
hand_is_soft = False  # True if a hand contains a soft ace (Value of 11)
dealer_hits_on_soft = True  # True if dealer can/must hit on Soft 17
deck_ready = True  # False if the deck was dealt, not shuffled
player_bj = False  # True if the player got Blackjack
cleanup = False  # True if the player left the table, breaks all timer loops
card_back_image = ''  # Handler for the cards deck back graphic
hole_card = ''  # Handler for dealer's hole card
first_card_obj = ''  # Handler for dealer's hole card label
hc_for_cheatsheet = ''  # The label that show's the dealer's hole card in the cheat sheet
is_cheatsheet_on = False  # True if the cheat sheet is currently displayed
card_frame_height = 0  # Handler for both card rows
no_of_backs = 0  # Number of backs pictures provided in each set
counted = {}  # Dictionary containing the cheatsheet stats
chosen_deck = 5  # The deck chosen in options by the player, assigned below
wanted_window_width = 0  # Wanted window width dependant on the chosen deck
available_decks = {  # Dictionary containing all decks assigned by:
    # (Name for filepath, no_of_backs, card_frame_height,
    # wanted_window_width)
    1: ("aqua", 13, 139, 90 * 7 + 90),
    2: ("casino", 2, 184, 130 * 7 + 90),
    3: ("newwave", 6, 124, 79 * 6 + 110),
    4: ("origin", 4, 111, 74 * 7 + 110),
    5: ("bicycle", 3, 164, 115 * 7 + 90),
    6: ("broadwalk", 1, 164, 115 * 7 + 90),
    7: ("charlie", 2, 164, 115 * 7 + 90)
}


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


def disable_buttons():
    stand_button['state'] = leave_button['state'] \
        = new_game['state'] = hit_button['state'] \
        = shuffle_button['state'] = ch_button['state'] = 'disabled'


def enable_buttons():
    if ROUND_IN_SESSION:
        stand_button['state'] = hit_button['state'] = 'normal'
        leave_button['state'] = ch_button['state'] = 'normal'
        new_game['state'] = shuffle_button['state'] = 'disabled'
    else:
        stand_button['state'] = hit_button['state'] = 'disabled'
        leave_button['state'] = ch_button['state'] = 'normal'
        new_game['state'] = shuffle_button['state'] = 'normal'


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


def show_cheatsheet():
    global is_cheatsheet_on
    ch_button['text'] = "Hide\nCheatsheet"
    ch_button['command'] = hide_cheatsheet
    is_cheatsheet_on = True
    mainWindow.update()
    secondWindow.update()
    secondWindow.deiconify()


def hide_cheatsheet():
    global is_cheatsheet_on
    secondWindow.withdraw()
    is_cheatsheet_on = False
    ch_button['text'] = "Show\nCheatsheet"
    ch_button['command'] = show_cheatsheet
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
    shuffle_button['text'] = "Round in\nSession"
    disable_buttons()


def create_delay(delay_time):  # TODO: Requires Threading
    for i in range(1, int(delay_time / 10) + 1):
        if cleanup:
            break
        mainWindow.after(10, mainWindow.update())


def new_round_timer():  # TODO: Requires Threading
    seconds = 12
    hit_button['text'] = "Next Round\nwill start in\n{}" \
        .format(seconds)
    mainWindow.update()
    for i in range(seconds, 0, -1):
        if cleanup:
            break
        if not ROUND_IN_SESSION:
            hit_button['text'] = "Next Round\nwill start in\n{}" \
                .format(i)
            create_delay(1000)
        else:
            break

    if not ROUND_IN_SESSION:
        new_round()


def hide_action_timer():
    global timer_label
    global timer_visible
    if not cleanup:
        timer_label.destroy()
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
    while seconds > 0:
        if cleanup:
            break
        timer_bg.config(file="graphics\\{}.png".format(seconds))
        create_delay(1000)
        seconds -= 1
        if seconds == 12:
            PlaySound.PlaySound('sounds\\hurry_up.wav',
                                PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        if seconds <= 5:
            PlaySound.PlaySound('sounds\\{}.wav'.format(seconds),
                                PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        if not PLAYERS_TURN:
            break
    if not cleanup:
        if PLAYERS_TURN and seconds <= 0:
            disable_buttons()
            mainWindow.update()
        if player_score_label.get() <= 16 and len(player_hand) <= 2:
            deal_player()
        else:
            hide_action_timer()
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
    for child in secondWindow.winfo_children():
        if child is not hc_for_cheatsheet:
            child.destroy()
    for key, value in counted.items():
        tkinter.Label(secondWindow, text="{:<3} : {:>3}".format(key, value),
                      background=RESULT_WIN_COLOR) \
            .grid(column=0, row=row_counter, sticky='nw')
        if not is_cheatsheet_on:
            secondWindow.update()
        row_counter += 1
    total = 0
    for value in counted.values():
        total += int(value)
    tkinter.Label(secondWindow, text="{} left in the deck.".format(total),
                  background=RESULT_WIN_COLOR) \
        .grid(column=0, row=row_counter, sticky='nw')
    row_counter += 1
    tkinter.Label(secondWindow, text="Top card in the deck is {}{}".format(deck[0][3], deck[0][2]),
                  background=RESULT_WIN_COLOR) \
        .grid(column=0, row=row_counter, sticky='nw')
    if not is_cheatsheet_on:
        secondWindow.update()


def new_round():
    global deck
    global deck_ready
    global ROUND_IN_SESSION
    ROUND_IN_SESSION = True
    disable_buttons()
    shuffle_button['command'] = shuffle
    deck_ready = False
    if not is_cheatsheet_on:
        secondWindow.update()
    clear_table()

    # Deal first cards
    first_play()


def refill_deck_if_empty():
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
    deck_is_empty = True
    for card in deck:
        if not card[4]:
            deck_is_empty = False
            break
    if deck_is_empty:
        player_score = score_hand(player_hand)
        dealer_score = score_hand(dealer_hand)
        dealer_score_label.set(dealer_score)
        player_score_label.set(player_score)
        create_delay(NAT_DELAY_TIME)
        random.shuffle(discard_pile)
        for card in discard_pile:
            deck.insert(0, card)
        discard_pile.clear()
        disable_buttons()
        reset_hitnstand_button()
        tempstr = result['text']
        result_text.set('Deck has emptied! Shuffling the discard pile.')
        hit_button['text'] = 'Shuffling'
        PlaySound.PlaySound('sounds\\riffle{}.wav'.format(random.randint(1, 4)),
                            PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        working_dots()
        PlaySound.PlaySound('sounds\\cardShuffle.wav',
                            PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        hit_button['text'] = 'Shuffling'
        working_dots()
        result_text.set(tempstr)
        reset_counted()
        reset_hitnstand_button()
        shuffle_button['text'] = 'Round in\nSession'
        if not is_cheatsheet_on:
            secondWindow.update()
        if PLAYERS_TURN:
            enable_buttons()
        mainWindow.update()


def cheat_sheet(card):
    global hc_for_cheatsheet
    counted[card[3]] = str(int(counted[card[3]]) - 1)
    row_counter = 0
    # for child in secondWindow.winfo_children():
    #     if child is not hc_for_cheatsheet:
    #         child.destroy()
    for key, value in counted.items():
        # tkinter.Label(secondWindow, text="{:<3} : {:>3}".format(key, value),
        #               background=RESULT_WIN_COLOR) \
        #     .grid(column=0, row=row_counter, sticky='nw')
        secondWindow.winfo_children()[row_counter]['text'] = "{:<3} : {:>3}".format(key, value)
        row_counter += 1
    if is_cheatsheet_on:
        secondWindow.update()
    total = 0
    for value in counted.values():
        total += int(value)
    secondWindow.winfo_children()[row_counter]['text'] = "{} left in the deck.".format(total)
    refill_deck_if_empty()
    row_counter += 1
    secondWindow.winfo_children()[row_counter]['text'] = \
        "Top card in the deck is {}{}".format(deck[0][3], deck[0][2])
    if not is_cheatsheet_on:
        secondWindow.update()


def deal_card(frame, hand):
    # pop the next card off the top of the deck
    next_card = deck.pop(0)
    next_card[4] = True
    deck.append(next_card)
    # add the image to a label and display the label
    PlaySound.PlaySound('sounds\\cardPlace{}.wav'.format(random.randint(1, 13)),
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    create_delay(250)
    card_obj = tkinter.Label(frame, image=next_card[1], borderwidth=0,
                             relief='raised', background=FELT_COLOR)
    card_obj.pack(side='left', padx=(1, 3), pady=(1, 3))
    card_obj.pack_propagate(0)
    update_notif(hand, next_card)
    cheat_sheet(next_card)
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
    dealer_hand.append(hole_card)
    hc_for_cheatsheet.destroy()
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
    if timer_visible:
        hide_action_timer()
    disable_buttons()
    timer_strvar.set(str(ACTION_TIME))
    hand_is_soft = False
    if not player_bj:
        flip_hole_card()
    create_delay(NAT_DELAY_TIME)
    dealer_score = score_hand(dealer_hand)
    while 0 < dealer_score <= dealerstand_score:
        if dealer_score == dealerstand_score:
            if dealer_hits_on_soft and hand_is_soft:
                result_text.set("Soft {}. Dealer must keep hitting.".format(dealerstand_score))
                create_delay(NAT_DELAY_TIME)
            else:
                result_text.set("Dealer will stand on or above {}.".format(dealerstand_score))
                create_delay(NAT_DELAY_TIME)
                ROUND_IN_SESSION = False
                break
        next_card = deal_card(dealer_card_frame, dealer_hand)
        dealer_hand.append(next_card)
        dealer_score = score_hand(dealer_hand)
        dealer_score_label.set(dealer_score)
        create_delay(NAT_DELAY_TIME)
    if 21 > dealer_score > dealerstand_score:
        result_text.set("Dealer will stand on or above {}.".format(dealerstand_score))
        create_delay(NAT_DELAY_TIME)
    player_score = score_hand(player_hand)
    check_final(player_score, dealer_score)


def check_final(player_score, dealer_score):
    global ROUND_IN_SESSION
    ROUND_IN_SESSION = False
    if player_score > 21:
        result_text.set("Dealer wins by player Bust! Better luck next round!")
        player_lost()
    elif dealer_score > 21:
        result_text.set("Dealer busts! Player wins!")
        player_won()
    elif dealer_score < player_score:
        result_text.set("Player wins!")
        player_won()
    elif dealer_score > player_score:
        player_lost()
        if len(dealer_hand) == 2 and dealer_score == 21:
            result_text.set("Blackjack! Dealer wins! Better luck next round!")
        else:
            result_text.set("Dealer wins! Better luck next round!")
    else:
        result_text.set("Draw!")
        dealer_score_no['fg'] = player_score_no['fg'] = WIN_COLOR
        dealer_score_no["font"] = font.Font(size=21, weight='bold')
        player_score_no["font"] = font.Font(size=21, weight='bold')
        sound_draw()
    enable_buttons()
    reset_shuffle_btn()
    new_round_timer()
    mainWindow.update()


def reset_shuffle_btn():
    shuffle_button['command'] = shuffle
    shuffle_button['text'] = "Shuffle and\nDeal Next Round"
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
    global ROUND_IN_SESSION
    global PLAYERS_TURN
    global timer_visible
    if PLAYERS_TURN and timer_visible:
        hide_action_timer()
    next_card = deal_card(player_card_frame, player_hand)
    player_hand.append(next_card)
    player_score = score_hand(player_hand)
    player_score_label.set(player_score)
    player_bj = check_for_bj(player_hand, player_score)
    if not player_bj:
        if player_score == 21:
            disable_buttons()
            ROUND_IN_SESSION = False
            PLAYERS_TURN = False
            # if timer_visible:
            #     hide_action_timer()
            create_delay(NAT_DELAY_TIME)
            result_text.set("21! Congratulations! Dealer will now try to match.")
            hit_button['text'] = '2'
            stand_button['text'] = '1'
            player_score_no['fg'] = WIN_COLOR
            create_delay(NAT_DELAY_TIME)
            deal_dealer()
        elif player_score > 21:  # To disable buttons before all delays
            disable_buttons()
            create_delay(NAT_DELAY_TIME)

        if player_score > 21:
            ROUND_IN_SESSION = False
            PLAYERS_TURN = False
            # if timer_visible:
            #     hide_action_timer()
            reset_shuffle_btn()
            result_text.set("Player busts! Dealer wins! Better luck next round!")
            player_lost()
            mainWindow.after(NAT_DELAY_TIME * 2, mainWindow.update())
            flip_hole_card()
            enable_buttons()
            new_round_timer()

        if PLAYERS_TURN:
            reset_action_timer()

        create_delay(NAT_DELAY_TIME)


def player_won():
    mainWindow.update()
    dealer_score_no['fg'] = LOSE_COLOR
    result['bg'] = RESULT_WIN_COLOR
    # mainWindow.config(background=result['bg'])
    result['fg'] = 'navy'
    player_score_no["font"] = font.Font(size=21, weight='bold')
    player_score_no['fg'] = WIN_COLOR
    PlaySound.PlaySound('sounds\\win_.wav', PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    mainWindow.update()


def player_lost():
    mainWindow.update()
    result['bg'] = RESULT_LOSE_COLOR
    # mainWindow.config(background=result['bg'])
    dealer_score_no["font"] = font.Font(size=21, weight='bold')
    dealer_score_no['fg'] = WIN_COLOR
    player_score_no['fg'] = LOSE_COLOR
    PlaySound.PlaySound('sounds\\you_lose.wav', PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    disable_buttons()
    mainWindow.update()


def sound_draw():
    mainWindow.update()
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
    global first_card_obj

    if not cleanup:
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
        if not next_card[3] == 'A':
            result_text.set("Dealer drew the {}{}. With a value of {}."
                            .format(next_card[3], next_card[2], next_card[0]))
        else:
            result_text.set("Dealer drew the {}{}. With a value of 11."
                            .format(next_card[3], next_card[2]))
        create_delay(NAT_DELAY_TIME)
        deal_player()
        if not player_bj:
            hole_card = deck.pop(0)
            hole_card[4] = True
            deck.append(hole_card)
            # add the card image to a label and display the label while playing
            # a card place sound
            PlaySound.PlaySound('sounds\\cardPlace{}.wav'.format(random.randint(1, 5)),
                                PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
            create_delay(300)
            first_card_obj = tkinter.Label(
                dealer_card_frame,
                image=card_back_image, borderwidth=0, relief='raised',
                background=FELT_COLOR)
            first_card_obj.pack(side='left', padx=(1, 3), pady=(1, 3))
            result_text.set("Dealer drew his hole card.\t\tYour turn...")
            cheat_sheet(hole_card)
            hc_for_cheatsheet = tkinter.Label(
                secondWindow, text="Dealer's hole card is {}{}"
                .format(hole_card[3], hole_card[2]),
                background=RESULT_WIN_COLOR)
            hc_for_cheatsheet.grid(column=0, row=16, sticky='nw')
            PLAYERS_TURN = True
            reset_hitnstand_button()
            enable_buttons()
            reset_action_timer()
        else:
            result_text.set("Blackjack! Congratulations! Dealer will now try to match.")
            PlaySound.PlaySound('sounds\\congratulations.wav',
                                PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
            hit_button['text'] = 'BLACK'
            stand_button['text'] = 'JACK'
            disable_buttons()
            player_score_no['fg'] = WIN_COLOR
            create_delay(NAT_DELAY_TIME)
            deal_dealer()


def shuffle():
    global deck_ready
    global ROUND_IN_SESSION
    ROUND_IN_SESSION = True
    disable_buttons()
    clear_table()
    for card in discard_pile:
        deck.append(card)
    discard_pile.clear()
    random.shuffle(deck)
    hit_button['text'] = 'Shuffling'
    PlaySound.PlaySound('sounds\\riffle{}.wav'.format(random.randint(1, 4)),
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    working_dots()
    PlaySound.PlaySound('sounds\\cardShuffle.wav',
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    hit_button['text'] = 'Shuffling'
    working_dots()
    reset_counted()
    deck_ready = True
    # ---- SOME CARDS APPENDED TO THE DECK TO CONTROL SCORE CHECK TESTS ----
    # for i in range(1, 8):
    #     load_back_of_card()
    #     deck.insert(0, (0, card_back_image, ' sff', 'ace'))
    # deck.insert(0, {0: 2, 1: card_back_image, 2: ' sff', 3: '2', 4: False})
    # deck.insert(0, {0: 6, 1: card_back_image, 2: ' sff', 3: '2', 4: False})
    # deck.insert(0, {0: 8, 1: card_back_image, 2: ' sff', 3: '2', 4: False})
    # deck.insert(0, {0: 1, 1: card_back_image, 2: ' sff', 3: '2', 4: False})
    # deck.insert(0, {0: 1, 1: card_back_image, 2: ' sff', 3: '2', 4: False})
    first_play()


def start_game():
    global deck_ready
    global ROUND_IN_SESSION
    ROUND_IN_SESSION = True
    disable_buttons()
    hide_cheatsheet()
    reset_counted()
    mainWindow.after(1, lambda: mainWindow.focus_force())
    PlaySound.PlaySound('sounds\\cardOpenPackage{}.wav'.format(random.randint(1, 2)),
                        PlaySound.SND_FILENAME)
    PlaySound.PlaySound('sounds\\cardTakeOutPackage{}.wav'.format(random.randint(1, 2)),
                        PlaySound.SND_FILENAME)
    PlaySound.PlaySound('sounds\\cardFan{}.wav'.format(random.randint(1, 2)),
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    deck_ready = False
    shuffle()
    mainWindow.mainloop()
    secondWindow.mainloop()


def say_goodbye():
    global cleanup

    disable_buttons()
    result['bg'] = "#bf40bf"
    # mainWindow.config(background=result['bg'])
    result['fg'] = "#99ccff"
    result_text.set("Goodbye! See you next time! :)")
    PlaySound.PlaySound("sounds\\later{}.wav".format(random.randint(1, 4)),
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    if not is_cheatsheet_on:
        secondWindow.update()
    create_delay(NAT_DELAY_TIME)
    cleanup = True
    quit()


dealer_hand = []
player_hand = []
cards = []

# Set up the GUI  TODO: Make this a separate init_GUI function
mainWindow = tkinter.Tk()
secondWindow = tkinter.Tk()
secondWindow.title("Counting cards!")
secondWindow.config(background=RESULT_WIN_COLOR)
mainWindow.title("Vit's Blackjack Table")
mainWindow.grid_columnconfigure(0, weight=1)
mainWindow.config(bg='#86592d')
# Load the background image
bgimage = tkinter.PhotoImage(file="graphics\\background.png")
bglabel = tkinter.Label(mainWindow, image=bgimage)
bglabel.place(x=0, y=0, relwidth=1, relheight=1)
# Load the images and create the deck
# for i in range(1, 3):  # Testing several decks in the main deck
#     load_chosen_set(cards)
load_chosen_set(cards)
deck = list(cards)
discard_pile = []
boldFont = tkinter.font.Font(size=12, weight="bold")
# Drawing the top line
result_text = tkinter.StringVar()
result_text.set("🂡🂫 Welcome to the BLACKJACK table! 🂫🂡")
result = tkinter.Label(mainWindow, background=RESULT_BG_COLOR, fg='white',
                       textvariable=result_text, font=font.Font(size=14),
                       relief='raised')
result.grid(row=0, column=0, columnspan=4, sticky='ew')
# Drawing the felt
card_frame = tkinter.Frame(mainWindow, height=card_frame_height * 2 + 5,
                           relief='ridge', bg=FELT_COLOR, borderwidth='3')
card_frame.grid(row=1, column=0, sticky='wens', columnspan=4, rowspan=2)
# card_frame.grid_propagate(0)
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
                                  background=FELT_COLOR)
dealer_card_frame.grid(row=0, column=1, sticky='ew', rowspan=2)

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
                                  background=FELT_COLOR)
player_card_frame.grid(row=2, column=1, sticky='ew', rowspan=2)
timer_strvar = tkinter.StringVar()
# player_card_frame.grid_propagate(0)
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
shuffle_button = tkinter.Button(button_frame, text='Shuffle and\nDeal Next Round',
                                command=shuffle, bg=BTN_BG, height=2,
                                width=12, font=font.Font(size=10))
shuffle_button.grid(row=0, column=1, sticky='nsew')
ch_button = tkinter.Button(button_frame, text='Show\nCheatsheet',
                           command=show_cheatsheet, bg=BTN_BG,
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

mainWindow.update()
mainWindow.geometry("{}x{}+265+100".format(wanted_window_width, button_frame.winfo_height() + result.winfo_height() +
                                           5 + int(card_frame_height * 2)))
mainWindow.minsize(wanted_window_width,
                   button_frame.winfo_height() + result.winfo_height() +
                   5 + int(card_frame_height * 2))
mainWindow.maxsize(wanted_window_width,
                   button_frame.winfo_height() + result.winfo_height() +
                   5 + int(card_frame_height * 2))
secondWindow.geometry("180x{}+85+100".format(mainWindow.winfo_height()))
mainWindow.update()

if __name__ == "__main__":
    start_game()
