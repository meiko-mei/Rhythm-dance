import pgzrun
import os
from random import randint
import sqlite3

db_conn = sqlite3.connect("dance_game_scores.db")
db_cursor = db_conn.cursor()

# Create a table to store scores if it doesn't exist
db_cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT,
        score INTEGER
    )
''')

#Centers the window and sets the window size
os.environ['SDL_VIDEO_CENTERED'] = '1'
WIDTH = 800
HEIGHT = 600
CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2

move_list = []
display_list = []

score = 0
current_move = 0
count = 4
dance_length = 4

say_dance = False
show_countdown = True
moves_complete = False
game_over = False

show_highscores = False 
score_recorded = False  

#draws the pictures to the window
dancer = Actor("dancer-start.png")
dancer.pos = CENTER_X + 5, CENTER_Y - 40
up = Actor("up.png")
up.pos = CENTER_X, CENTER_Y + 110
right = Actor("right.png")
right.pos = CENTER_X + 60, CENTER_Y + 170
down = Actor("down.png")
down.pos = CENTER_X, CENTER_Y + 230
left = Actor("left.png")
left.pos = CENTER_X - 60, CENTER_Y + 170

SHOW_HIGH_SCORES_TEXT_RECT = Rect(CENTER_X - 100, 400, 200, 30)

MENU = 0
PLAYING = 1
GAME_OVER = 2
HIGH_SCORES = 3
 
player_name=''

current_state = MENU
def draw_menu():

    screen.clear()
    screen.blit("stage.png", (0, 0))
    screen.draw.text("RHYTHM ON!", color="black", topleft=(CENTER_X - 150, 150), fontsize=75)
    screen.draw.text("Press SPACE to start", color="black", topleft=(CENTER_X - 100, 250), fontsize=30)
    
def draw():
    if current_state == MENU:
        draw_menu()
        screen.draw.filled_rect(Rect(CENTER_X - 95, 390, 190, 40), "white")
        screen.draw.text("Show High Scores", color="black", topleft=(CENTER_X - 90, 400), fontsize=30)
    elif current_state == PLAYING:
        draw_playing()
    elif current_state == GAME_OVER:
        draw_game_over()
    elif current_state == HIGH_SCORES:
        draw_high_scores()
    if show_highscores:
        draw_high_scores()

def draw_playing():
    global game_over, score, say_dance
    global count, show_countdown
    
    if not game_over:
        screen.clear()
        screen.blit("stage.png", (0, 0))
        dancer.draw()
        up.draw()
        down.draw()
        right.draw()
        left.draw()
        screen.draw.text("Score: " + str(score), color="black", topleft=(10, 10))

        if say_dance:
            screen.draw.text("Dance!", color="black", topleft=(CENTER_X - 65, 150), fontsize=60)

        if show_countdown:
            screen.draw.text(str(count), color="black", topleft=(CENTER_X - 8, 150), fontsize=60)

    else:
        draw_game_over()

def draw_game_over():
    global score, player_name, score_recorded, show_highscores, current_state
    current_state = GAME_OVER

    screen.clear()
    screen.blit("stage", (0, 0))
    screen.draw.text("Score: " + str(score), color="black", topleft=(10, 10))
    screen.draw.text("GAME OVER!", color="black", topleft=(CENTER_X - 130, 220), fontsize=60)

    if player_name == "":
        # Display input box for player's name
        player_name = input("Enter your name: ")

    if player_name != "" and not score_recorded:
        # Insert the score and player name into the database
        db_cursor.execute("INSERT INTO scores (player_name, score) VALUES (?, ?)", (player_name, score))
        db_conn.commit()
        print("Score recorded in the database.")
        score_recorded = True

    screen.draw.text("Show High Scores", color="black", topleft=(CENTER_X - 100, 400), fontsize=30)
    if show_highscores:
        draw_high_scores()   

def draw_high_scores():
    global db_cursor

    screen.clear()
    screen.blit("stage.png", (0, 0))

    # Draw a white rectangle as the background for high scores
    white_rect_width = 300
    white_rect_height = 300
    white_rect_pos = (CENTER_X - white_rect_width / 2, 20)
    screen.draw.filled_rect(Rect(white_rect_pos, (white_rect_width, white_rect_height)), "white")

    screen.draw.text("High Scores", color="black", topleft=(CENTER_X - 80, 50), fontsize=40)

    # Retrieve the top 10 unique scores from the database
    db_cursor.execute("SELECT DISTINCT player_name, MAX(score) as max_score FROM scores GROUP BY player_name ORDER BY max_score DESC LIMIT 10")
    scores = db_cursor.fetchall()

    # Display scores in a tabular format
    y_position = 100  # Adjust the starting Y position as needed

    # Draw headers
    screen.draw.text("Player Name", color="black", topleft=(CENTER_X - 120, y_position), fontsize=20)
    screen.draw.text("High Score", color="black", topleft=(CENTER_X +40, y_position), fontsize=20)
    y_position += 30

    for row in scores:
        player_name, player_score = row[0], row[1]
        screen.draw.text(player_name, color="black", topleft=(CENTER_X - 100, y_position), fontsize=20)
        screen.draw.text(str(player_score), color="black", topleft=(CENTER_X + 50, y_position), fontsize=20)
        y_position += 30  # Adjust the Y increment as needed

        
def on_mouse_down(pos, button):
    global show_highscores, current_state

    # Check if the mouse click is within the area of the "Show High Scores" text
    if SHOW_HIGH_SCORES_TEXT_RECT.collidepoint(pos):
        show_highscores = True
        draw_high_scores() 

def on_key_down(key):
    global current_state

    if key == keys.SPACE and current_state == MENU:
        current_state = PLAYING
        generate_moves()
        music.play("vanishing-horizon")

def reset_dancer():
    global game_over
    if not game_over:
        dancer.image = "dancer-start.png"
        up.image = "up.png"
        right.image = "right.png"
        down.image = "down.png"
        left.image = "left.png"
    return

def update_dancer(move):
    global game_over
    if not game_over:
        if move == 0:
            up.image = "up-lit.png"
            dancer.image = "dancer-up.png"
            clock.schedule(reset_dancer, 0.5)
        elif move == 1:
            right.image = "right-lit.png"
            dancer.image = "dancer-right.png"
            clock.schedule(reset_dancer, 0.5)
        elif move == 2:
            down.image = "down-lit.png"
            dancer.image = "dancer-down.png"
            clock.schedule(reset_dancer, 0.5)
        else:
            left.image = "left-lit.png"
            dancer.image = "dancer-left.png"
            clock.schedule(reset_dancer, 0.5)

    return

def display_moves():
    global move_list, display_list, dance_length
    global say_dance, show_countdown, current_move

    if display_list:
        this_move = display_list[0]
        display_list = display_list[1:]

        if this_move == 0:
            update_dancer(0)
            clock.schedule(display_moves, 1)
        elif this_move == 1:
            update_dancer(1)
            clock.schedule(display_moves, 1)
        elif this_move == 2:
            update_dancer(2)
            clock.schedule(display_moves, 1)
        else:
            update_dancer(3)
            clock.schedule(display_moves, 1)
    else:
        say_dance = True
        show_countdown = False
    return

#just the timer
def countdown():
    global count, game_over, show_countdown

    if count > 1:
        count = count - 1
        clock.schedule(countdown, 1)
    else:
        show_countdown = False
        display_moves()
    return


def generate_moves(): # updated hehe finally
    global move_list, dance_length, count
    global show_countdown, say_dance

    count = 4
    move_list = []
    say_dance = False

    for move in range(0, dance_length):
        rand_move = randint(0, 3)
        move_list.append(rand_move)
        display_list.append(rand_move)

    show_countdown = True
    countdown()

def next_move():
    global dance_length, current_move, moves_complete
    if current_move < dance_length - 1:
        current_move = current_move + 1
    else:
        moves_complete = True
    return

#KEY PRESSES to see if right or wrong move
def on_key_up(key):
    global score, game_over, move_list, current_move

    if key == keys.UP:
        update_dancer(0)
        if move_list[current_move] == 0:
            score = score + 1
            next_move()
        else:
            game_over = True

    elif key == keys.RIGHT:
        update_dancer(1)
        if move_list[current_move] == 1:
            score = score + 1
            next_move()
        else:
            game_over = True

    elif key == keys.DOWN:
        update_dancer(2)
        if move_list[current_move] == 2:
            score = score + 1
            next_move()
        else:
            game_over = True

    elif key == keys.LEFT:
        update_dancer(3)
        if move_list[current_move] == 3:
            score = score + 1
            next_move()
        else:
            game_over = True

    return

def update():
    global game_over, current_move, moves_complete, current_state
    if not game_over:
        if moves_complete:
            generate_moves()
            moves_complete = False
            current_move = 0
    else:
        music.stop()
        current_state = GAME_OVER

def on_close():
    # Close the database connection when the game is closing
    db_conn.close()
print(os.path.abspath('z'))
pgzrun.go()