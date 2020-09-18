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
RESULT_LOSE_COLOR = "#990000"  # Background color of result label if the player loses
RESULT_WIN_COLOR = 'gold'  # Background color of result label if the player wins
NAT_DELAY_TIME = 1300  # Natural delay time between result label updates
dealerstand_score = 17  # The score in which the dealer can't hit anymore
hand_is_soft = False  # True if a hand contains a soft ace (Value of 11)
dealer_hits_on_soft = True  # True if dealer can hit on Soft 17
deck_ready = True  # False if the deck was dealt, not shuffled
player_bj = False  # True if the player got Blackjack
card_back_image = ''  # Handler for the cards deck back graphic
hole_card = ''  # Handler for dealer's hole card
first_card_obj = ''  # Handler for dealer's hold card label
card_frame_height = 0  # Handler for both card rows
no_of_backs = 0  # Number of backs pictures provided in each set
chosen_deck = 1  # The deck chosen in options by the player, assigned below
wanted_window_width = 0  # Wanted window width dependant on the chosen deck
available_decks = {  # Dictionary containing all decks assigned by:
    # (Name for filepath, no_of_backs, card_frame_height,
    # wanted_window_width)
    1: ("aqua", 13, 139, 90 * 6 + 110),
    2: ("casino", 2, 184, 130 * 6 + 110),
    3: ("newwave", 6, 124, 79 * 6 + 110),
    4: ("origin", 4, 111, 74 * 7 + 110)
}
counted = {}


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
            available_decks[chosen_deck][0], random.randint(1, no_of_backs),
            extension))


def disable_buttons():
    stand_button['state'] = leave_button['state'] \
        = new_game['state'] = hit_button['state'] \
        = shuffle_button['state'] = 'disabled'
    mainWindow.update()


def reenable_buttons():
    stand_button['state'] = shuffle_button['state'] = 'normal'
    leave_button['state'] = new_game['state'] = 'normal'
    hit_button['state'] = 'normal'
    mainWindow.update()


def working_dots():
    """
    Creates the cool process bar like dots on the big button.
    Lasts 2.75 seconds while sounds are playing.
    :return:
    """
    shuffle_button['text'] = shuffle_button['text'] + '\n'
    for i in range(1, 12):
        shuffle_button['text'] = shuffle_button['text'] + '.'
        mainWindow.after(250, mainWindow.update())


def move_to_discard_pile():
    for i in range(len(deck) - 1, -1, -1):
        if deck[i][4]:
            deck[i][4] = False
            discard_pile.append(deck[i])
            deck.pop(i)
    print("{}\n{}".format(len(deck), len(discard_pile)))


def clear_table():
    global dealer_hand
    global player_hand
    global dealer_card_frame
    global player_card_frame
    global player_bj
    player_bj = False
    move_to_discard_pile()
    dealer_card_frame.destroy()
    player_card_frame.destroy()
    dealer_card_frame = tkinter.Frame(card_frame, height=card_frame_height, background=FELT_COLOR)
    dealer_card_frame.grid(row=0, column=1, sticky='ew', rowspan=2)
    player_card_frame = tkinter.Frame(card_frame, height=card_frame_height, background=FELT_COLOR)
    player_card_frame.grid(row=2, column=1, sticky='ew', rowspan=2)
    player_score_label.set(0)
    dealer_score_label.set(0)
    result['bg'] = RESULT_BG_COLOR
    result['fg'] = 'white'
    dealer_score_no['fg'] = 'white'
    player_score_no['fg'] = 'white'
    dealer_score_no["font"] = font.Font(size=18)
    player_score_no["font"] = font.Font(size=18)
    result_text.set("🂡 Welcome to the BLACKJACK table! 🂫")
    disable_buttons()
    mainWindow.after(150, mainWindow.update())
    if not deck_ready:
        PlaySound.PlaySound('sounds\\cardClear.wav', PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        shuffle_button['text'] = 'Clearing\nthe Table'
        working_dots()
        shuffle_button['text'] = "Round in\nSession"


def reset_counted():
    global counted
    counted = {
        'A': '4',
        '2': '4',
        '3': '4',
        '4': '4',
        '5': '4',
        '6': '4',
        '7': '4',
        '8': '4',
        '9': '4',
        '10': '4',
        'J': '4',
        'Q': '4',
        'K': '4'
    }
    for card in deck:
        if card[4]:
            counted[card[3]] = str(int(counted[card[3]]) - 1)
    row_counter = 0
    for key, value in counted.items():
        tkinter.Label(secondWindow, text="{} : {}".format(key, value),
                      background=RESULT_BG_COLOR, fg='white') \
            .grid(column=0, row=row_counter, sticky='n')
        secondWindow.update()
        row_counter += 1


def new_round():
    global deck
    global deck_ready
    global dealer_hand
    global player_hand
    shuffle_button['state'] = 'disabled'
    stand_button['state'] = 'normal'
    hit_button['state'] = 'normal'
    dealer_hand = []
    player_hand = []
    disable_buttons()
    shuffle_button['command'] = shuffle
    deck_ready = False
    secondWindow.update()
    clear_table()
    # Deal first cards
    first_play()


def refill_deck():
    deck_is_empty = True
    for card in deck:
        # go through the deck and see if the 4th index of all the cards
        # (a boolean that is true if the card was already dealt or not)
        # is true, if so, that means that all the cards were dealt and
        # a new deck is made from the discard pile (all the cards that
        # were already dealt and are not in this current round)
        # as soon as the first undealt card is found (4th index is
        # false) deck_is_empty is made false, and the loop is broken
        # to stop looking for more undealt cards.
        if not card[4]:
            deck_is_empty = False
            break
    if deck_is_empty:

        random.shuffle(discard_pile)
        for card in discard_pile:
            deck.insert(0, card)
        reset_counted()
        discard_pile.clear()
        disable_buttons()
        print(discard_pile, '\ndiscard_pile is shuffled')
        result_text.set('Deck has emptied! Shuffling the discard pile.')
        shuffle_button['text'] = 'Shuffling'
        PlaySound.PlaySound('sounds\\riffle{}.wav'.format(random.randint(1, 4)),
                            PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        working_dots()
        PlaySound.PlaySound('sounds\\cardShuffle.wav',
                            PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        shuffle_button['text'] = 'Shuffling'
        working_dots()
        shuffle_button['text'] = 'Round in\nSession'
        secondWindow.update()
        reenable_buttons()
        mainWindow.update()


def cheat_sheet(card):
    counted[card[3]] = str(int(counted[card[3]]) - 1)
    row_counter = 0
    for key, value in counted.items():
        tkinter.Label(secondWindow, text="{} : {}".format(key, value),
                      background=RESULT_BG_COLOR, fg='white') \
            .grid(column=0, row=row_counter, sticky='n')
        secondWindow.update()
        row_counter += 1
    total = 0
    refill_deck()
    for value in counted.values():
        total += int(value)
    tkinter.Label(secondWindow, text="{} cards left unknown.".format(total),
                  background=RESULT_BG_COLOR, fg='white') \
        .grid(column=0, row=row_counter, sticky='n')
    row_counter += 1
    tkinter.Label(secondWindow, text="Next card will be the {}{}".format(deck[0][3], deck[0][2]),
                  background=RESULT_BG_COLOR, fg='white') \
        .grid(column=0, row=row_counter, sticky='n')
    secondWindow.update()


def deal_card(frame, hand):
    refill_deck()
    # pop the next card off the top of the deck
    next_card = deck.pop(0)
    next_card[4] = True
    deck.append(next_card)
    cheat_sheet(next_card)
    # add the image to a label and display the label
    PlaySound.PlaySound('sounds\\cardPlace{}.wav'.format(random.randint(1, 13)),
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    mainWindow.after(300, mainWindow.update())
    card_obj = tkinter.Label(frame, image=next_card[1], borderwidth=0, relief='raised',
                             background=FELT_COLOR)
    # card_obj.place(anchor='nw',)                            #TODO: SOLVE THIS SOMEHOW!
    card_obj.pack(side='left', padx=(1, 3), pady=(1, 3))
    card_obj.pack_propagate(0)

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
    dealer_hand.append(hole_card)
    PlaySound.PlaySound('sounds\\cardFlip.wav',
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    mainWindow.after(300, mainWindow.update())
    first_card_obj['image'] = hole_card[1]
    if hole_card[0] == 1:
        result_text.set("Dealer's hole was the {}{}. Value of 11."
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
    disable_buttons()
    global hand_is_soft
    hand_is_soft = False
    if not player_bj:
        flip_hole_card()
    mainWindow.after(NAT_DELAY_TIME, mainWindow.update())
    dealer_score = score_hand(dealer_hand)
    while 0 < dealer_score <= dealerstand_score:
        if dealer_score == dealerstand_score:
            if dealer_hits_on_soft and hand_is_soft:
                result_text.set("Soft {}. Dealer must keep hitting.".format(dealerstand_score))
                mainWindow.after(NAT_DELAY_TIME, mainWindow.update())
            else:
                result_text.set("Dealer will stand on or above {}.".format(dealerstand_score))
                mainWindow.after(NAT_DELAY_TIME, mainWindow.update())
                break
        next_card = deal_card(dealer_card_frame, dealer_hand)
        dealer_hand.append(next_card)
        dealer_score = score_hand(dealer_hand)
        dealer_score_label.set(dealer_score)
        mainWindow.after(NAT_DELAY_TIME, mainWindow.update())
    if 21 > dealer_score > dealerstand_score:
        result_text.set("Dealer will stand on or above {}.".format(dealerstand_score))
        mainWindow.after(NAT_DELAY_TIME, mainWindow.update())
    player_score = score_hand(player_hand)
    check_final(player_score, dealer_score)


def check_final(player_score, dealer_score):  # TODO: Change all the code to call the two outcome functions
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
    reenable_buttons()
    stand_button['state'] = hit_button['state'] = 'disabled'
    reset_shuffle_btn()
    mainWindow.update()


def reset_shuffle_btn():
    shuffle_button['command'] = shuffle
    shuffle_button['text'] = "Shuffle\nand Deal"
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
    next_card = deal_card(player_card_frame, player_hand)
    player_hand.append(next_card)
    player_score = score_hand(player_hand)
    player_score_label.set(player_score)
    player_bj = check_for_bj(player_hand, player_score)

    if not player_bj:
        if player_score == 21:
            disable_buttons()
            mainWindow.after(NAT_DELAY_TIME, mainWindow.update())
            result_text.set("21! Congratulations! Dealer will now try to match.")
            player_score_no['fg'] = WIN_COLOR
            mainWindow.after(NAT_DELAY_TIME, mainWindow.update())
            deal_dealer()
        elif player_score > 21:  # To disable buttons before all delays
            disable_buttons()
            mainWindow.after(NAT_DELAY_TIME, mainWindow.update())
        else:
            mainWindow.after(NAT_DELAY_TIME, mainWindow.update())

        if player_score > 21:
            reset_shuffle_btn()
            result_text.set("Player busts! Dealer wins! Better luck next round!")
            player_lost()
            mainWindow.after(NAT_DELAY_TIME * 2, mainWindow.update())
            flip_hole_card()
            reenable_buttons()
            hit_button['state'] = 'disabled'
            stand_button['state'] = 'disabled'


def player_won():
    mainWindow.update()
    dealer_score_no['fg'] = LOSE_COLOR
    result['bg'] = RESULT_WIN_COLOR
    result['fg'] = 'navy'
    player_score_no["font"] = font.Font(size=21, weight='bold')
    player_score_no['fg'] = WIN_COLOR
    PlaySound.PlaySound('sounds\\win.wav', PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    mainWindow.update()


def player_lost():
    mainWindow.update()
    result['bg'] = RESULT_LOSE_COLOR
    dealer_score_no["font"] = font.Font(size=21, weight='bold')
    dealer_score_no['fg'] = WIN_COLOR
    player_score_no['fg'] = LOSE_COLOR
    PlaySound.PlaySound('sounds\\lose.wav', PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
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
    global player_score_label
    global dealer_score_label
    global hole_card
    global first_card_obj
    player_hand = []
    dealer_hand = []
    deck_ready = False
    load_back_of_card()
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
    mainWindow.after(NAT_DELAY_TIME, mainWindow.update())
    deal_player()
    if not player_bj:
        refill_deck()
        hole_card = deck.pop(0)
        hole_card[4] = True
        deck.append(hole_card)
        cheat_sheet(hole_card)
        # add the card image to a label and display the label while playing
        # a card place sound
        PlaySound.PlaySound('sounds\\cardPlace{}.wav'.format(random.randint(1, 5)),
                            PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
        mainWindow.after(300, mainWindow.update())
        first_card_obj = tkinter.Label(dealer_card_frame, image=card_back_image, borderwidth=0, relief='raised',
                                       background=FELT_COLOR)
        first_card_obj.pack(side='left', padx=(1, 3), pady=(1, 3))
        result_text.set("Dealer drew his hole card.\t\tYour turn...")
        reenable_buttons()
        shuffle_button['state'] = new_game['state'] = 'disabled'
    else:
        result_text.set("Blackjack! Congratulations! Dealer will now try to match.")
        disable_buttons()
        player_score_no['fg'] = WIN_COLOR
        mainWindow.after(NAT_DELAY_TIME, mainWindow.update())
        deal_dealer()


def shuffle():
    global deck_ready
    disable_buttons()
    clear_table()
    for card in discard_pile:
        deck.append(card)
    discard_pile.clear()
    reset_counted()
    random.shuffle(deck)
    shuffle_button['text'] = 'Shuffling'
    PlaySound.PlaySound('sounds\\riffle{}.wav'.format(random.randint(1, 4)),
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    working_dots()
    PlaySound.PlaySound('sounds\\cardShuffle.wav',
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    shuffle_button['text'] = 'Shuffling'
    working_dots()
    shuffle_button['text'] = 'Round in\nSession'
    deck_ready = True
    # ---- SOME CARDS APPENDED TO THE DECK TO CONTROL SCORE CHECK TESTS ----
    # for i in range(1, 8):
    #     load_back_of_card()
    #     deck.insert(0, (0, card_back_image, ' sff', 'ace'))
    # deck.insert(0, (6, card_back_image, ' sff', 'ACfffeE'))
    # deck.insert(0, (10, card_back_image, ' sff', 'TEN'))
    # deck.insert(0, (1, card_back_image, ' sff', 'efe'))
    # deck.insert(0, (1, card_back_image, ' sff', 'ACE'))
    first_play()


def start_game():
    global deck_ready
    disable_buttons()
    reset_counted()
    PlaySound.PlaySound('sounds\\cardOpenPackage{}.wav'.format(random.randint(1, 2)),
                        PlaySound.SND_FILENAME)
    PlaySound.PlaySound('sounds\\cardTakeOutPackage{}.wav'.format(random.randint(1, 2)),
                        PlaySound.SND_FILENAME)
    PlaySound.PlaySound('sounds\\cardFan{}.wav'.format(random.randint(1, 2)),
                        PlaySound.SND_FILENAME + PlaySound.SND_ASYNC)
    shuffle()
    deck_ready = False
    secondWindow.update()
    mainWindow.mainloop()
    secondWindow.mainloop()


def say_goodbye():
    disable_buttons()
    result['bg'] = "#bf40bf"
    result['fg'] = "#99ccff"
    result_text.set("Goodbye! See you next time! :)")
    mainWindow.after(NAT_DELAY_TIME, mainWindow.update())
    mainWindow.quit()


dealer_hand = []
player_hand = []
cards = []

# Set up the GUI  TODO: Make this a separate init_GUI function
mainWindow = tkinter.Tk()
secondWindow = tkinter.Tk()
secondWindow.title("Counting cards!")
mainWindow.title("Vit's Blackjack Table")
mainWindow.grid_columnconfigure(0, weight=1)
mainWindow.config(background=FELT_COLOR)
# Load the images and create the deck
load_chosen_set(cards)
deck = list(cards)
discard_pile = []

# Drawing the top line
result_text = tkinter.StringVar()
result_text.set("Welcome to the BLACKJACK table!")
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
# player_card_frame.grid_propagate(0)
mainWindow.update()
# Control panel area
button_frame = tkinter.Frame(mainWindow, relief='ridge', background=FELT_COLOR,
                             borderwidth='3')
button_frame.grid(row=3, column=0, sticky='sw')

shuffle_button = tkinter.Button(button_frame, text='Shuffling',
                                command=shuffle, state='disabled',
                                width=10, font=font.Font(size=12))
shuffle_button.grid(row=0, column=0, rowspan=3, sticky='nws')
stand_button = tkinter.Button(button_frame, text='STAND',
                              command=deal_dealer)
stand_button.grid(row=0, column=1, sticky='ew')
hit_button = tkinter.Button(button_frame, text='HIT',
                            command=deal_player)
hit_button.grid(row=0, column=2, sticky='ew')
new_game = tkinter.Button(button_frame, text='Keep playing', command=new_round)
new_game.grid(row=1, column=1, columnspan=2, sticky='ew')
leave_button = tkinter.Button(button_frame, text='Leave Table', command=say_goodbye)
leave_button.grid(row=2, column=1, columnspan=2, sticky='ew')
leave_button.place()
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
print(mainWindow.winfo_height())
secondWindow.geometry("180x{}+85+100".format(mainWindow.winfo_height()))
mainWindow.update()
secondWindow.update()
print(secondWindow.winfo_reqheight())

if __name__ == "__main__":
    start_game()
