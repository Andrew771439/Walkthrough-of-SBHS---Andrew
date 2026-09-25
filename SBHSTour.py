import pygame
import json
import os

pygame.init()


class pos:   
    """Small reusable 2-D position value used by the tour."""

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __iter__(self):
        return iter((self.x, self.y))

    def __repr__(self):
        return f"pos({self.x}, {self.y})"

    def copy(self):
        return pos(self.x, self.y)

    def as_tuple(self):
        return self.x, self.y

    def distance_to(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def __eq__(self, other):
        if not isinstance(other, pos):
            return NotImplemented
        return self.x == other.x and self.y == other.y


# --------------------------------------------------
# WINDOW
# --------------------------------------------------

WIDTH = 1580
HEIGHT = 920

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SBHS Tour")

clock = pygame.time.Clock()


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ldtk_path = os.path.join(
    BASE_DIR,
    "Science block",
    "Walkthrough_of_ScienceBlock.ldtk"
)

map_image_path = os.path.join(
    BASE_DIR,
    "Science block",
    "Assets",
    "Science_Block.png"
)

player_image_path = os.path.join(
    BASE_DIR,
    "Science block",
    "Assets",
    "Science_Student.png"
)

biology_image_path = os.path.join(
    BASE_DIR,
    "Science block",
    "Assets",
    "Biology_Teacher.png"
)

chemistry_image_path = os.path.join(
    BASE_DIR,
    "Science block",
    "Assets",
    "Chemistry_Teacher.png"
)

physics_image_path = os.path.join(
    BASE_DIR,
    "Science block",
    "Assets",
    "Physics_Teacher.png"
)

student_image_path = os.path.join(
    BASE_DIR,
    "Science block",
    "Assets",
    "Science_Student.png"
)

player_front_path = os.path.join(
    BASE_DIR,
    "Science block",
    "Assets",
    "Front_facing",
    "spritesheet.png"
)

player_back_path = os.path.join(
    BASE_DIR,
    "Science block",
    "Assets",
    "Back_facing",
    "spritesheet.png"
)

player_left_path = os.path.join(
    BASE_DIR,
    "Science block",
    "Assets",
    "Left_facing",
    "spritesheet.png"
)

player_right_path = os.path.join(
    BASE_DIR,
    "Science block",
    "Assets",
    "Right_facing",
    "spritesheet.png"
)


# --------------------------------------------------
# LOAD LDTK
# --------------------------------------------------

with open(ldtk_path, "r") as file:
    map_data = json.load(file)

print("LDtk map loaded!")


science_level = None

for level in map_data["levels"]:

    if level["identifier"] == "Science_block":
        science_level = level
        break


if science_level is None:

    print("ERROR: Science_block level not found")

    pygame.quit()

    raise SystemExit


# --------------------------------------------------
# LOAD IMAGES
# --------------------------------------------------

NPC_OFFSET_X = 0
NPC_OFFSET_Y = 0


map_image = pygame.image.load(
    map_image_path
).convert_alpha()


player_image = pygame.image.load(
    player_image_path
).convert_alpha()

player_image = pygame.transform.scale(
    player_image,
    (40, 40)
)


MAP_WIDTH = map_image.get_width()
MAP_HEIGHT = map_image.get_height()


biology_image = pygame.image.load(
    biology_image_path
).convert_alpha()

chemistry_image = pygame.image.load(
    chemistry_image_path
).convert_alpha()

physics_image = pygame.image.load(
    physics_image_path
).convert_alpha()

student_image = pygame.image.load(
    student_image_path
).convert_alpha()


biology_image = pygame.transform.scale(
    biology_image,
    (40, 40)
)

chemistry_image = pygame.transform.scale(
    chemistry_image,
    (40, 40)
)

physics_image = pygame.transform.scale(
    physics_image,
    (40, 40)
)

student_image = pygame.transform.scale(
    student_image,
    (40, 40)
)

player_front_sheet = pygame.image.load(
    player_front_path
).convert_alpha()

player_back_sheet = pygame.image.load(
    player_back_path
).convert_alpha()

player_left_sheet = pygame.image.load(
    player_left_path
).convert_alpha()

player_right_sheet = pygame.image.load(
    player_right_path
).convert_alpha()

def split_spritesheet(sheet, frame_width, frame_height, frame_count):   #USed AI alot here to help with sprite set up and animation difficulties.
    # Split one horizontal spritesheet into individually scaled animation frames.

    frames = []

    for i in range(frame_count):

        frame = sheet.subsurface(
            pygame.Rect(
                i * frame_width,
                0,
                frame_width,
                frame_height
            )
        )

        scale = 40 / frame_height

        new_width = int(frame_width * scale)
        new_height = 40

        frame = pygame.transform.scale(
            frame,
            (new_width, new_height)
        )

        frames.append(frame)

    return frames

player_front_frames = split_spritesheet(
    player_front_sheet,
    32,
    32,
    8
)

player_back_frames = split_spritesheet(
    player_back_sheet,
    16,
    30,
    8
)

player_left_frames = split_spritesheet(
    player_left_sheet,
    15,
    30,
    8
)

player_right_frames = split_spritesheet(
    player_right_sheet,
    15,
    30,
    8
)

# --------------------------------------------------
# LOAD COLLISIONS
# --------------------------------------------------

collision_rects = []

COLLISION_OFFSET_X = -63
COLLISION_OFFSET_Y = -35


for layer in science_level["layerInstances"]:

    if layer["__identifier"] == "Collisions":

        grid_size = layer["__gridSize"]
        cols = layer["__cWid"]

        for index, value in enumerate(layer["intGridCsv"]):

            if value == 1:

                grid_x = index % cols
                grid_y = index // cols

                collision_rects.append(
                    pygame.Rect(
                        grid_x * grid_size + COLLISION_OFFSET_X,
                        grid_y * grid_size + COLLISION_OFFSET_Y,
                        grid_size,
                        grid_size
                    )
                )


print(
    "Collision cells loaded:",
    len(collision_rects)
)


# --------------------------------------------------
# FIND PLAYER SPAWN
# --------------------------------------------------

player_x = 0
player_y = -5


for layer in science_level["layerInstances"]:

    if layer["__identifier"] == "Spawn_and_teleport":

        for entity in layer["entityInstances"]:

            if entity["__identifier"] == "Science_block_spawn":

                for field in entity["fieldInstances"]:

                    if (
                        field["__identifier"] == "SpawnID"
                        and
                        field["__value"] == "Science_Block_Initial"
                    ):

                        player_x = entity["px"][0] - 16
                        player_y = entity["px"][1] - 32


print(
    "Player spawn:",
    player_x,
    player_y
)

# --------------------------------------------------
# MOCK TELEPORT SCREEN
# --------------------------------------------------

show_next_area = False
show_teleport_prompt = False
was_in_teleport = False

teleport_yes_button = pygame.Rect(
    WIDTH // 2 - 130,
    HEIGHT // 2 + 40,
    110,
    50
)

teleport_no_button = pygame.Rect(
    WIDTH // 2 + 20,
    HEIGHT // 2 + 40,
    110,
    50
)

teleport_rect = pygame.Rect(
    1472,
    512,
    80,
    80
)

finish_tour_button = pygame.Rect(
    WIDTH // 2 - 110,
    HEIGHT // 2 + 100,
    220,
    60
)


# --------------------------------------------------
# PLAYER
# --------------------------------------------------

PLAYER_SPEED = 3

player_direction = "front"
player_frame = 0
player_animation_timer = 0
player_animation_speed = 8

player_rect = pygame.Rect(
    player_x,
    player_y,
    40,
    40
)


# --------------------------------------------------
# COLLISION FUNCTIONS
# --------------------------------------------------

#USed Ai a little and COnners code help to create the collision functions for the player movement and wall collisions.

def move_player_x(amount):
    # Move horizontally, then stop the player at the first wall they touch.

    player_rect.x += amount

    for wall in collision_rects:

        if player_rect.colliderect(wall):

            if amount > 0:
                player_rect.right = wall.left

            elif amount < 0:
                player_rect.left = wall.right


def move_player_y(amount):
    # Move vertically, then stop the player at the first wall they touch.

    player_rect.y += amount

    for wall in collision_rects:

        if player_rect.colliderect(wall):

            if amount > 0:
                player_rect.bottom = wall.top

            elif amount < 0:
                player_rect.top = wall.bottom


# --------------------------------------------------
# LOAD NPCS
# --------------------------------------------------

npcs = []


for layer in science_level["layerInstances"]:

    if layer["__identifier"] == "Spawn_and_teleport":

        for entity in layer["entityInstances"]:

            if entity["__identifier"] == "Sprites":

                npc_id = None
                npc_name = None
                npc_dialogue = None

                for field in entity["fieldInstances"]:

                    if field["__identifier"] == "NPCid":
                        npc_id = field["__value"]

                    elif field["__identifier"] == "Sprite_name":
                        npc_name = field["__value"]

                    elif field["__identifier"] == "Dialogue":
                        npc_dialogue = field["__value"]


                if npc_id is not None:

                    npcs.append({

                        "id": npc_id,

                        "name": npc_name,

                        "dialogue": npc_dialogue,

                        "x": entity["px"][0],

                        "y": entity["px"][1]

                    })


# --------------------------------------------------
# LOAD INTERACTABLES
# --------------------------------------------------

interactables = []


for layer in science_level["layerInstances"]:

    if layer["__identifier"] == "Interactables":

        for entity in layer["entityInstances"]:

            if entity["__identifier"] == "Interactables":

                interaction_type = None
                interaction_id = None
                interaction_message = None


                for field in entity["fieldInstances"]:

                    if field["__identifier"] == "interactionType":

                        interaction_type = field["__value"]

                    elif field["__identifier"] == "interactionID":

                        interaction_id = field["__value"]

                    elif field["__identifier"] == "message":

                        interaction_message = field["__value"]

                if interaction_id == "Bin":
                  continue


                interactables.append({

                    "type": interaction_type,

                    "id": interaction_id,

                    "message": interaction_message,

                    "x": entity["px"][0],

                    "y": entity["px"][1]

                })


print(
    "Interactables loaded:",
    len(interactables)
)


# --------------------------------------------------
# CAMERA
# --------------------------------------------------

camera_x = 0
camera_y = 0


# --------------------------------------------------
# INTERACTION SETTINGS
# --------------------------------------------------

font = pygame.font.Font(
    None,
    32
)

small_font = pygame.font.Font(
    None,
    26
)

# --------------------------------------------------
# WELCOME SCREEN
# --------------------------------------------------

show_welcome = True

start_tour_button = pygame.Rect(
    WIDTH // 2 - 120,
    HEIGHT // 2 + 220,
    240,
    60
)


INTERACTION_DISTANCE = 40

INTERACTABLE_OFFSET_X = -50
INTERACTABLE_OFFSET_Y = 0


# --------------------------------------------------
# NPC DIALOGUE
# --------------------------------------------------

show_dialogue = False

dialogue_text = ""

dialogue_name = ""


dialogue_box = pygame.Rect(
    150,
    HEIGHT - 180,
    WIDTH - 300,
    120
)


close_button = pygame.Rect(
    dialogue_box.right - 100,
    dialogue_box.y + 15,
    75,
    35
)


# --------------------------------------------------
# BIOLOGY QUESTION
# --------------------------------------------------

show_biology_question = False

biology_result = ""


biology_question = (
    "Which organelle carries out photosynthesis?"
)


biology_answers = [

    "A. Nucleus",

    "B. Chloroplast",

    "C. Ribosome",

    "D. Mitochondrion"

]

#--------------------------------------------------
# PHYSICS QUESTION
#--------------------------------------------------
show_physics_question = False
physics_result = ""

physics_question = "What is the unit of force?"

physics_answers = [
    "A. Joule",
    "B. Newton",
    "C. Watt",
    "D. Volt"
]

correct_physics_answer = 1


correct_biology_answer = 1


biology_buttons = []


for i in range(4):

    button = pygame.Rect(

        WIDTH // 2 - 250,

        350 + i * 65,

        500,

        50

    )

    biology_buttons.append(
        button
    )

physics_buttons = []

for i in range(4):

    button = pygame.Rect(
        WIDTH // 2 - 250,
        350 + i * 65,
        500,
        50
    )

    physics_buttons.append(button)


biology_close_button = pygame.Rect(

    WIDTH // 2 + 210,

    200,

    70,

    35

)

physics_close_button = pygame.Rect(

    WIDTH // 2 + 210,

    200,

    70,

    35
)

# --------------------------------------------------
# BIOLOGY TREE MINIGAME
# --------------------------------------------------

#USed AI for first mini-game to give me an idea on how to do it
show_biology_minigame = False

biology_stage = 0
biology_dragging = None

biology_sequence = [
    "Water",
    "Sunlight",
    "Air"
]

biology_message = "Drag WATER to the tree!"

tree_drop_rect = pygame.Rect(
    WIDTH // 2 - 100,
    250,
    200,
    330
)

biology_items = [
    {
        "name": "Water",
        "rect": pygame.Rect(250, 300, 160, 60),
        "start_x": 250,
        "start_y": 300
    },
    {
        "name": "Sunlight",
        "rect": pygame.Rect(250, 400, 160, 60),
        "start_x": 250,
        "start_y": 400
    },
    {
        "name": "Air",
        "rect": pygame.Rect(250, 500, 160, 60),
        "start_x": 250,
        "start_y": 500
    }
]

biology_used_items = []

biology_minigame_close = pygame.Rect(
    WIDTH - 250,
    170,
    90,
    40
)

# --------------------------------------------------
# CHEMISTRY COLOUR MIXING MINIGAME
# --------------------------------------------------

show_chemistry_minigame = False

chemistry_dragging = None
chemistry_selected = []

chemistry_targets = [
    "Green",
    "Purple",
    "Orange"
]

chemistry_round = 0
chemistry_message = "Make GREEN (drag colours into the beaker!)"

chemistry_colours = [
    {
        "name": "Red",
        "colour": (220, 60, 60),
        "rect": pygame.Rect(220, 320, 150, 60),
        "start_x": 220,
        "start_y": 320
    },
    {
        "name": "Blue",
        "colour": (70, 110, 220),
        "rect": pygame.Rect(220, 420, 150, 60),
        "start_x": 220,
        "start_y": 420
    },
    {
        "name": "Yellow",
        "colour": (240, 220, 60),
        "rect": pygame.Rect(220, 520, 150, 60),
        "start_x": 220,
        "start_y": 520
    }
]

chemistry_beaker_rect = pygame.Rect(
    WIDTH // 2 - 100,
    300,
    200,
    250
)

chemistry_close_button = pygame.Rect(
    WIDTH - 250,
    170,
    90,
    40
)

chemistry_mix_colour = (240, 240, 240)

# --------------------------------------------------
# PHYSICS FORCE MINIGAME
# --------------------------------------------------

show_physics_minigame = False

physics_dragging = None
physics_result = ""         

physics_box_rect = pygame.Rect(
    WIDTH // 2 - 100,
    300,
    200,
    180
)

physics_items = [
    {
        "name": "Left",
        "rect": pygame.Rect(WIDTH // 2 - 265, 500, 150, 60),
        "start_x": WIDTH // 2 - 265,
        "start_y": 500
    },
    {
        "name": "Right",
        "rect": pygame.Rect(WIDTH // 2 - 75, 500, 150, 60),
        "start_x": WIDTH // 2 - 75,
        "start_y": 500
    },
    {
        "name": "Up",
        "rect": pygame.Rect(WIDTH // 2 + 115, 500, 150, 60),
        "start_x": WIDTH // 2 + 115,
        "start_y": 500
    }
]

physics_minigame_close = pygame.Rect(
    WIDTH - 290,
    170,
    90,
    40
)

# --------------------------------------------------
# TOILET SEARCH MINIGAME
# --------------------------------------------------

show_toilet_minigame = False

toilet_result = ""
golden_pencil_found = False

toilet_buttons = [
    pygame.Rect(WIDTH // 2 - 260, 350, 160, 180),
    pygame.Rect(WIDTH // 2 - 80, 350, 160, 180),
    pygame.Rect(WIDTH // 2 + 100, 350, 160, 180)
]

# Toilet number 2 contains the special item
special_toilet = 1

toilet_close_button = pygame.Rect(
    WIDTH // 2 + 240,
    200,
    90,
    40
)


# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

running = True


while running:


    # --------------------------------------------------
    # EVENTS
    # --------------------------------------------------

    for event in pygame.event.get():
        # Process window, keyboard, mouse, and minigame events once per frame.


        if event.type == pygame.QUIT:
            running = False


        # ----------------------------------------------
        # KEYBOARD
        # ----------------------------------------------

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if show_biology_question:
                    show_biology_question = False

                elif show_physics_question:
                    show_physics_question = False

                elif show_dialogue:
                    show_dialogue = False

                else:
                    running = False

            # ------------------------------------------
            # PRESS E
            # ------------------------------------------

            if event.key == pygame.K_e:
                # E interacts with the nearest valid object before checking NPCs.


                interaction_found = False


                # --------------------------------------
                # CHECK WHITEBOARD / INTERACTABLES FIRST
                # --------------------------------------

                for interactable in interactables:


                    interactable_rect = pygame.Rect(

                        interactable["x"] + INTERACTABLE_OFFSET_X,

                        interactable["y"] + INTERACTABLE_OFFSET_Y,

                        32,

                        32
                    )


                    distance_x = abs(

                        player_rect.centerx
                        -
                        interactable_rect.centerx

                    )


                    distance_y = abs(

                        player_rect.centery
                        -
                        interactable_rect.centery

                    )


                    if (
                        distance_x < INTERACTION_DISTANCE
                        and
                        distance_y < INTERACTION_DISTANCE
                    ):

                        interaction_found = True

                        if interactable["id"] == "biology_question":
                            # Open the biology quiz and close other activities.
                            show_biology_question = True
                            show_physics_question = False
                            show_biology_minigame = False
                            biology_result = ""

                        elif interactable["id"] == "physics_question":
                            show_physics_question = True
                            show_biology_question = False
                            show_physics_minigame = False
                            physics_result = ""

                        elif interactable["id"] == "biology_experiment":
                            # Reset the biology experiment whenever it is opened.
                            show_biology_question = False
                            show_physics_question = False
                            show_biology_minigame = True

                            biology_stage = 0
                            biology_used_items = []
                            biology_dragging = None
                            biology_message = "Drag WATER to the tree!"

                            for item in biology_items:
                                item["rect"].x = item["start_x"]
                                item["rect"].y = item["start_y"]

                        elif interactable["id"] == "chemistry_experiment":
                            # Reset the colour mixing experiment to its first target.

                            show_biology_question = False
                            show_physics_question = False
                            show_biology_minigame = False
                            show_chemistry_minigame = True

                            chemistry_round = 0
                            chemistry_selected = []
                            chemistry_dragging = None
                            chemistry_message = "Make GREEN (drag colours into the beaker!)"
                            chemistry_mix_colour = (240, 240, 240)

                            for item in chemistry_colours:
                                item["rect"].x = item["start_x"]
                                item["rect"].y = item["start_y"]

                        elif interactable["id"] == "Physics_experiment":
                            # Reset the force experiment and return the box to its start.

                            show_biology_question = False
                            show_physics_question = False
                            show_biology_minigame = False
                            show_chemistry_minigame = False

                            show_physics_minigame = True

                            physics_dragging = None
                            physics_result = ""

                            for item in physics_items:
                                item["rect"].x = item["start_x"]
                                item["rect"].y = item["start_y"]

                            physics_box_rect.x = WIDTH // 2 - 100
                            physics_box_rect.y = 300

                        elif interactable["id"] == "Golden_pencil":
                            # Open the toilet search activity.

                            show_biology_question = False
                            show_physics_question = False
                            show_biology_minigame = False
                            show_chemistry_minigame = False
                            show_physics_minigame = False

                            show_toilet_minigame = True
                            toilet_result = ""

                        break


                # --------------------------------------
                # CHECK NPCS
                # --------------------------------------

                if not interaction_found:


                    for npc in npcs:


                        npc_rect = pygame.Rect(

                            npc["x"] + NPC_OFFSET_X,

                            npc["y"] + NPC_OFFSET_Y,

                            40,

                            40

                        )


                        distance_x = abs(

                            player_rect.centerx
                            -
                            npc_rect.centerx

                        )


                        distance_y = abs(

                            player_rect.centery
                            -
                            npc_rect.centery

                        )


                        if (
                            distance_x < INTERACTION_DISTANCE
                            and
                            distance_y < INTERACTION_DISTANCE
                        ):


                            dialogue_name = npc["name"]

                            if (
                                npc["id"] == "Student"
                                and golden_pencil_found
                            ):
                                dialogue_text = "You found the Golden Pencil! Nice work."

                            else:
                                dialogue_text = npc["dialogue"]

                            show_dialogue = True

                            show_biology_question = False

                            break


        # ----------------------------------------------
        # MOUSE movement and clicks
        # ----------------------------------------------

    #USED AI FOR FIRST MOUSE MOTION AND W3SCHOOLS TO UNDERSTAND HOW DRAG AND DROP WORKS AND HOW TO IMPLEMENT IT INTO THE MINIGAMES.

        if event.type == pygame.MOUSEMOTION:
            # Keep a selected draggable item underneath the mouse cursor.

            if (
                show_biology_minigame
                and biology_dragging is not None
            ):

                biology_items[biology_dragging]["rect"].center = event.pos

            if (
                show_chemistry_minigame
                and chemistry_dragging is not None
            ):

                chemistry_colours[chemistry_dragging]["rect"].center = event.pos

            if (
                show_physics_minigame
                and physics_dragging is not None
            ):
                physics_items[physics_dragging]["rect"].center = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            # Resolve a biology, chemistry, or physics drag when the mouse is released.
            if (
                event.button == 1
                and show_biology_minigame
                and biology_dragging is not None
            ):
                item = biology_items[biology_dragging]

                if item["rect"].colliderect(tree_drop_rect):
                    correct_item = biology_sequence[biology_stage]

                    if item["name"] == correct_item:
                        biology_used_items.append(item["name"])
                        biology_stage += 1

                        if biology_stage == 1:
                            biology_message = "Great! Now drag SUNLIGHT!"
                        elif biology_stage == 2:
                            biology_message = "Great! Now drag AIR!"
                        elif biology_stage == 3:
                            biology_message = "You grew the tree!"
                    else:
                        biology_message = "Try another one!"

                item["rect"].x = item["start_x"]
                item["rect"].y = item["start_y"]
                biology_dragging = None

            if (
                event.button == 1
                and show_chemistry_minigame
                and chemistry_dragging is not None
            ):

                item = chemistry_colours[chemistry_dragging]

                if item["rect"].colliderect(chemistry_beaker_rect):

                    if item["name"] not in chemistry_selected:
                        chemistry_selected.append(item["name"])

                    # SHOW FIRST COLOUR IN THE BEAKER

                    if len(chemistry_selected) == 1:
                        chemistry_mix_colour = item["colour"]

                    if len(chemistry_selected) == 2:
                        # Two selected colours are compared with the current target mix.

                        mix = set(chemistry_selected)
                        result_name = ""

                        if mix == {"Blue", "Yellow"}:
                            result_name = "Green"
                            chemistry_mix_colour = (80, 180, 80)

                        elif mix == {"Red", "Blue"}:
                            result_name = "Purple"
                            chemistry_mix_colour = (150, 80, 180)

                        elif mix == {"Red", "Yellow"}:
                            result_name = "Orange"
                            chemistry_mix_colour = (240, 150, 50)

                        target = chemistry_targets[chemistry_round]

                        if result_name == target:

                            chemistry_selected = []
                            chemistry_round += 1

                            if chemistry_round < len(chemistry_targets):
                                next_target = chemistry_targets[chemistry_round]

                                chemistry_message = (
                                    "Correct! Now make "
                                    + next_target.upper()
                                )

                            else:
                                chemistry_message = "Experiment complete!"

                        else:

                            chemistry_message = (
                                "Wrong mix! Try "
                                + target.upper()
                                + " again."
                            )

                            chemistry_selected = []
                            chemistry_mix_colour = (240, 240, 240)

                item["rect"].x = item["start_x"]
                item["rect"].y = item["start_y"]

                chemistry_dragging = None

            # PHYSICS FORCE DROP

            if (
                event.button == 1
                and show_physics_minigame
                and physics_dragging is not None
            ):

                item = physics_items[physics_dragging]

                if item["rect"].colliderect(physics_box_rect):

                    if item["name"] == "Right":
                        physics_result = "Correct! The box moves right."
                        physics_box_rect.x += 120

                    else:
                        physics_result = "Try again!"

                item["rect"].x = item["start_x"]
                item["rect"].y = item["start_y"]

                physics_dragging = None

        if event.type == pygame.MOUSEBUTTONDOWN:



            if event.button == 1:

                if (
                    show_welcome
                    and start_tour_button.collidepoint(event.pos)
                ):
                    show_welcome = False

                # TELEPORT YES / NO BUTTONS

                if show_teleport_prompt:

                    if teleport_yes_button.collidepoint(event.pos):
                        show_teleport_prompt = False
                        show_next_area = True

                    elif teleport_no_button.collidepoint(event.pos):
                        show_teleport_prompt = False

                elif (
                    show_next_area
                    and finish_tour_button.collidepoint(event.pos) # type: ignore
                ):
                    running = False

                # BIOLOGY MINIGAME CLOSE

                if (
                    show_biology_minigame
                    and biology_minigame_close.collidepoint(event.pos)
                ):
                    show_biology_minigame = False


                # PICK UP BIOLOGY ITEM

                if show_biology_minigame:

                    for i, item in enumerate(biology_items):

                        if (
                            item["name"] not in biology_used_items
                            and item["rect"].collidepoint(event.pos)
                        ):
                            biology_dragging = i
                            break

                # CHEMISTRY MINIGAME CLOSE

                if (
                    show_chemistry_minigame
                    and chemistry_close_button.collidepoint(event.pos)
                ):
                    show_chemistry_minigame = False

                # PHYSICS MINIGAME CLOSE

                if (
                    show_physics_minigame
                    and physics_minigame_close.collidepoint(event.pos)
                ):
                    show_physics_minigame = False

                # TOILET MINIGAME CLOSE

                if (
                    show_toilet_minigame
                    and toilet_close_button.collidepoint(event.pos)
                ):
                    show_toilet_minigame = False

                # SEARCH TOILETS

                if show_toilet_minigame:

                    for i, button in enumerate(toilet_buttons):

                        if button.collidepoint(event.pos):

                            if i == special_toilet:

                                if not golden_pencil_found:
                                    toilet_result = "You found the Golden Pencil! Congratulations!"
                                    golden_pencil_found = True

                                else:
                                    toilet_result = "You already found it!"

                            else:

                                toilet_result = "Nothing here..."


                # PICK UP CHEMISTRY COLOUR

                if (
                    show_chemistry_minigame
                    and chemistry_round < len(chemistry_targets)
                ):

                    for i, item in enumerate(chemistry_colours):

                        if item["rect"].collidepoint(event.pos):

                            chemistry_dragging = i
                            break

                # PICK UP PHYSICS FORCE

                if show_physics_minigame:

                    for i, item in enumerate(physics_items):

                        if item["rect"].collidepoint(event.pos):

                            physics_dragging = i
                            break
        


                # --------------------------------------
                # CLOSE NPC DIALOGUE
                # --------------------------------------

                if (
                    show_dialogue
                    and
                    close_button.collidepoint(
                        event.pos
                    )
                ):

                    show_dialogue = False


                # --------------------------------------
                # BIOLOGY AND PHYSICS QUESTION CLOSE BUTTON
                # --------------------------------------

                if (
                    show_biology_question
                    and
                    biology_close_button.collidepoint(
                        event.pos
                    )
                ):

                    show_biology_question = False
                    show_physics_question = False

                if (
                    show_physics_question
                    and
                    physics_close_button.collidepoint(
                        event.pos
                    )
                ):

                    show_physics_question = False


                # --------------------------------------
                # BIOLOGY ANSWERS
                # --------------------------------------

                if show_biology_question:


                    for i, button in enumerate(
                        biology_buttons
                    ):


                        if button.collidepoint(
                            event.pos
                        ):


                            if i == correct_biology_answer:

                                biology_result = "Correct!"


                            else:

                                biology_result = "Try again!"


                # PHYSICS ANSWERS
                # --------------------------------------

                if show_physics_question:

                    for i, button in enumerate(
                        physics_buttons
                    ):

                        if button.collidepoint(
                            event.pos
                        ):

                            if i == correct_physics_answer:

                                physics_result = "Correct!"

                            else:

                                physics_result = "Try again!"


    # --------------------------------------------------
    # PLAYER MOVEMENT
    # --------------------------------------------------

    keys = pygame.key.get_pressed()
    # Read held movement keys and convert them into a frame-by-frame displacement.


    move_x = 0
    move_y = 0


    if keys[pygame.K_w]:
        move_y -= PLAYER_SPEED
        player_direction = "back"

    if keys[pygame.K_s]:
        move_y += PLAYER_SPEED
        player_direction = "front"

    if keys[pygame.K_a]:
        move_x -= PLAYER_SPEED
        player_direction = "left"

    if keys[pygame.K_d]:
        move_x += PLAYER_SPEED
        player_direction = "right"

    if move_x != 0 or move_y != 0:
        # Advance the walking animation only while the player is moving.

        player_animation_timer += 1

        if player_animation_timer >= player_animation_speed:
            player_frame += 1
            player_animation_timer = 0

            if player_frame >= 8:
                player_frame = 0

    else:
        player_frame = 0
        player_animation_timer = 0

    move_player_x(
        move_x
    )

    move_player_y(
        move_y
    )

    in_teleport = player_rect.colliderect(teleport_rect)

    if (
        in_teleport
        and not was_in_teleport
        and not show_next_area
    ):
        show_teleport_prompt = True

    was_in_teleport = in_teleport
    


    # NPC dialogue disappears when walking

    if move_x != 0 or move_y != 0:

        show_dialogue = False


    # --------------------------------------------------
    # CHECK NEARBY NPC
    # --------------------------------------------------

    nearby_npc = None


    for npc in npcs:


        npc_rect = pygame.Rect(

            npc["x"] + NPC_OFFSET_X,

            npc["y"] + NPC_OFFSET_Y,

            40,

            40

        )


        distance_x = abs(

            player_rect.centerx
            -
            npc_rect.centerx

        )


        distance_y = abs(

            player_rect.centery
            -
            npc_rect.centery

        )


        if (
            distance_x < INTERACTION_DISTANCE
            and
            distance_y < INTERACTION_DISTANCE
        ):

            nearby_npc = npc

            break


    # --------------------------------------------------
    # CHECK NEARBY INTERACTABLE
    # --------------------------------------------------

    nearby_interactable = None


    for interactable in interactables:


        interactable_rect = pygame.Rect(

            interactable["x"] + INTERACTABLE_OFFSET_X,

            interactable["y"] + INTERACTABLE_OFFSET_Y,

            32,

            32
        )

        distance_x = abs(

            player_rect.centerx
            -
            interactable_rect.centerx

        )


        distance_y = abs(

            player_rect.centery
            -
            interactable_rect.centery

        )


        if (
            distance_x < INTERACTION_DISTANCE
            and
            distance_y < INTERACTION_DISTANCE
        ):

            nearby_interactable = interactable

            break


    # --------------------------------------------------
    # KEEP PLAYER ON MAP
    # --------------------------------------------------

    if player_rect.left < 0:

        player_rect.left = 0


    if player_rect.right > MAP_WIDTH:

        player_rect.right = MAP_WIDTH


    if player_rect.top < 0:

        player_rect.top = 0


    if player_rect.bottom > MAP_HEIGHT:

        player_rect.bottom = MAP_HEIGHT


    # --------------------------------------------------
    # CAMERA
    # --------------------------------------------------

    # Keep the camera centred on the player while preventing it from leaving the map.

    camera_x = (
        player_rect.centerx
        -
        WIDTH // 2
    )


    camera_y = (
        player_rect.centery
        -
        HEIGHT // 2
    )


    camera_x = max(

        0,

        min(

            camera_x,

            max(
                0,
                MAP_WIDTH - WIDTH
            )

        )

    )


    camera_y = max(

        0,

        min(

            camera_y,

            max(
                0,
                MAP_HEIGHT - HEIGHT
            )

        )

    )


    # --------------------------------------------------
    # DRAW MAP
    # --------------------------------------------------

    # Draw the world first so player and interface elements appear on top of it.
    #USED AI TO HELP ME UNDERSTAND HOW TO DRAW THE MAP AND HOW TO IMPLEMENT IT INTO THE GAME. WAS ABLE TO UNDERSTAND AND USE FOR A WHOLE LOT OF OTHER THINGS.

    screen.fill(
        (30, 30, 30)
    )


    screen.blit(

        map_image,

        (
            -camera_x,
            -camera_y
        )

    )


    # --------------------------------------------------
    # DRAW PLAYER
    # --------------------------------------------------

    # Select the animation frames for the current facing direction.

    if player_direction == "front":
        current_player_image = player_front_frames[player_frame]

    elif player_direction == "back":
        current_player_image = player_back_frames[player_frame]

    elif player_direction == "left":
        current_player_image = player_left_frames[player_frame]

    elif player_direction == "right":
        current_player_image = player_right_frames[player_frame]

    screen.blit(
    current_player_image,
    (
        player_rect.centerx
        - current_player_image.get_width() // 2
        - camera_x,

        player_rect.bottom
        - current_player_image.get_height()
        - camera_y
    )
)


    # --------------------------------------------------
    # DRAW NPCS
    # --------------------------------------------------

    for npc in npcs:


        if npc["id"] == "Biology_teacher":

            image = biology_image


        elif npc["id"] == "Chemistry_teacher":

            image = chemistry_image


        elif npc["id"] == "Physics_teacher":

            image = physics_image


        elif npc["id"] == "Student":

            image = student_image


        else:

            continue


        screen.blit(

            image,

            (
                npc["x"] + NPC_OFFSET_X - camera_x,

                npc["y"] + NPC_OFFSET_Y - camera_y
            )

        )

    # DRAW ACTIVITY MARKERS
    # --------------------------------------------------

    for interactable in interactables:

        marker = None
        marker_colour = (255, 255, 255)

        if interactable["id"] in [
            "biology_question",
            "physics_question"
        ]:
            marker = "?"
            marker_colour = (120, 200, 255)

        elif interactable["id"] in [
            "biology_experiment",
            "chemistry_experiment",
            "Physics_experiment"
        ]:
            marker = "!"
            marker_colour = (255, 210, 90)

        if marker is not None:

            marker_x = (
                interactable["x"]
                + INTERACTABLE_OFFSET_X
                - camera_x
            )

            marker_y = (
                interactable["y"]
                + INTERACTABLE_OFFSET_Y
                - camera_y
                - 0
            )

            marker_box = pygame.Rect(
                marker_x - 16,
                marker_y - 16,
                32,
                32
            )

            pygame.draw.rect(
                screen,
                (30, 30, 30),
                marker_box,
                border_radius=8
            )

            pygame.draw.rect(
                screen,
                marker_colour,
                marker_box,
                2,
                border_radius=8
            )

            marker_surface = font.render(
                marker,
                True,
                marker_colour
            )

            screen.blit(
                marker_surface,
                (
                    marker_box.centerx
                    - marker_surface.get_width() // 2,

                    marker_box.centery
                    - marker_surface.get_height() // 2
                )
            )


    # --------------------------------------------------
    # INTERACTION PROMPT
    # --------------------------------------------------

    # Show the action available at the nearest NPC or interactable.

    if (
        (
            nearby_npc is not None
            or
            nearby_interactable is not None
        )
        and not show_dialogue
        and not show_biology_question
        and not show_physics_question
        and not show_biology_minigame
        and not show_chemistry_minigame
        and not show_physics_minigame
        and not show_toilet_minigame
        and not show_teleport_prompt
        and not show_next_area
        and not show_welcome
    ):

        if nearby_interactable is not None:

            if nearby_interactable["id"] == "biology_question":
                prompt_text = " E to answer Biology question"

            elif nearby_interactable["id"] == "physics_question":
                prompt_text = " E to answer Physics question"

            elif nearby_interactable["id"] == "biology_experiment":
                prompt_text = " E to start Biology experiment"

            elif nearby_interactable["id"] == "chemistry_experiment":
                prompt_text = " E to start Chemistry experiment"

            elif nearby_interactable["id"] == "Physics_experiment":
                prompt_text = " E to start Physics experiment"

            elif nearby_interactable["id"] == "Golden_pencil":
                prompt_text = " E to search the toilets"

            else:
                prompt_text = "Press E to interact"

        elif nearby_npc is not None:
            prompt_text = "Press E to talk"


        prompt_surface = small_font.render(

            prompt_text,

            True,

            (255, 255, 255)

        )


        prompt_box = pygame.Rect(

            WIDTH // 2 - 140,

            HEIGHT - 80,

            280,

            45

        )


        pygame.draw.rect(

            screen,

            (20, 20, 20),

            prompt_box

        )


        pygame.draw.rect(

            screen,

            (255, 255, 255),

            prompt_box,

            2

        )


        screen.blit(

            prompt_surface,

            (

                prompt_box.centerx
                -
                prompt_surface.get_width() // 2,

                prompt_box.centery
                -
                prompt_surface.get_height() // 2

            )

        )


    # --------------------------------------------------
    # DRAW BIOLOGY QUESTION
    # --------------------------------------------------

    if show_biology_question:


        question_box = pygame.Rect(

            WIDTH // 2 - 300,

            180,

            600,

            470

        )


        # WHITEBOARD

        pygame.draw.rect(

            screen,

            (245, 245, 235),

            question_box

        )


        pygame.draw.rect(

            screen,

            (30, 30, 30),

            question_box,

            4

        )


        # TITLE

        title_surface = font.render(

            "Biology Question",

            True,

            (20, 20, 20)

        )


        screen.blit(

            title_surface,

            (

                question_box.x + 20,

                question_box.y + 20

            )

        )

    


        # QUESTION

        question_surface = small_font.render(

            biology_question,

            True,

            (20, 20, 20)

        )


        screen.blit(

            question_surface,

            (

                question_box.x + 20,

                question_box.y + 75

            )

        )


        # ANSWER BUTTONS

        for i, button in enumerate(
            biology_buttons
        ):


            pygame.draw.rect(

                screen,

                (220, 220, 210),

                button

            )


            pygame.draw.rect(

                screen,

                (30, 30, 30),

                button,

                2

            )


            answer_surface = small_font.render(

                biology_answers[i],

                True,

                (20, 20, 20)

            )


            screen.blit(

                answer_surface,

                (

                    button.x + 15,

                    button.y + 13

                )

            )


        # RESULT

        if biology_result != "":


            result_surface = font.render(

                biology_result,

                True,

                (20, 20, 20)

            )


            screen.blit(

                result_surface,

                (

                    question_box.x + 20,

                    question_box.bottom - 55

                )

            )


        # CLOSE BUTTON

        pygame.draw.rect(

            screen,

            (210, 210, 200),

            biology_close_button

        )


        pygame.draw.rect(

            screen,

            (20, 20, 20),

            biology_close_button,

            2

        )


        close_question_text = small_font.render(

            "Close",

            True,

            (20, 20, 20)

        )


        screen.blit(

            close_question_text,

            (

                biology_close_button.centerx
                -
                close_question_text.get_width() // 2,

                biology_close_button.centery
                -
                close_question_text.get_height() // 2

            )

        )


    # --------------------------------------------------
    # DRAW PHYSICS QUESTION
    # --------------------------------------------------

    if show_physics_question:

        question_box = pygame.Rect(
            WIDTH // 2 - 300,
            180,
            600,
            470
        )

        pygame.draw.rect(
            screen,
            (245, 245, 235),
            question_box
        )

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            question_box,
            4
        )

        title_surface = font.render(
            "Physics Question",
            True,
            (20, 20, 20)
        )

        screen.blit(
            title_surface,
            (
                question_box.x + 20,
                question_box.y + 20
            )
        )

        question_surface = small_font.render(
            physics_question,
            True,
            (20, 20, 20)
        )

        screen.blit(
            question_surface,
            (
                question_box.x + 20,
                question_box.y + 75
            )
        )

        for i, button in enumerate(physics_buttons):

            pygame.draw.rect(
                screen,
                (220, 220, 210),
                button
            )

            pygame.draw.rect(
                screen,
                (30, 30, 30),
                button,
                2
            )

            answer_surface = small_font.render(
                physics_answers[i],
                True,
                (20, 20, 20)
            )

            screen.blit(
                answer_surface,
                (
                    button.x + 15,
                    button.y + 13
                )
            )

        if physics_result != "":

            result_surface = font.render(
                physics_result,
                True,
                (20, 20, 20)
            )

            screen.blit(
                result_surface,
                (
                    question_box.x + 20,
                    question_box.bottom - 55
                )
            )

        # CLOSE BUTTON

        pygame.draw.rect(
            screen,
            (210, 210, 200),
            physics_close_button
        )

        pygame.draw.rect(
            screen,
            (20, 20, 20),
            physics_close_button,
            2
        )

        close_question_text = small_font.render(
            "Close",
            True,
            (20, 20, 20)
        )

        screen.blit(
            close_question_text,
            (
                physics_close_button.centerx
                - close_question_text.get_width() // 2,

                physics_close_button.centery
                - close_question_text.get_height() // 2
            )
        )



    # --------------------------------------------------
    # DRAW BIOLOGY TREE MINIGAME
    # ------------------------------------------------




    if show_biology_minigame:

        minigame_box = pygame.Rect(
            120,
            130,
            WIDTH - 240,
            HEIGHT - 220
        )

        pygame.draw.rect(
            screen,
            (235, 245, 225),
            minigame_box
        )

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            minigame_box,
            4
        )

        title_surface = font.render(
            "Help the Tree Grow!",
            True,
            (20, 20, 20)
        )

        screen.blit(
            title_surface,
            (
                minigame_box.x + 30,
                minigame_box.y + 25
            )
        )

        message_surface = small_font.render(
            biology_message,
            True,
            (20, 20, 20)
        )

        screen.blit(
            message_surface,
            (
                minigame_box.x + 30,
                minigame_box.y + 70
           )
        )


        # TREE AREA

        pygame.draw.rect(
            screen,
            (210, 230, 200),
            tree_drop_rect,
            2
        )


        # SEED

        if biology_stage == 0:

            pygame.draw.circle(
                screen,
                (100, 70, 40),
                tree_drop_rect.center,
                15
            )


        # SMALL SPROUT

        elif biology_stage == 1:

            pygame.draw.rect(
                screen,
                (100, 70, 40),
                (
                    tree_drop_rect.centerx - 5,
                    tree_drop_rect.centery,
                    10,
                    80
                )
            )

            pygame.draw.circle(
                screen,
                (80, 160, 70),
                (
                    tree_drop_rect.centerx,
                    tree_drop_rect.centery
                ),
                35
            )


        # SMALL TREE

        elif biology_stage == 2:

            pygame.draw.rect(
                screen,
                (100, 70, 40),
                (
                    tree_drop_rect.centerx - 10,
                    tree_drop_rect.centery - 20,
                    20,
                    140
                )
            )

            pygame.draw.circle(
                screen,
                (70, 150, 60),
                (
                    tree_drop_rect.centerx,
                    tree_drop_rect.centery - 40
                ),
                65
            )


        # FULL TREE

        elif biology_stage >= 3:

            pygame.draw.rect(
                screen,
                (100, 70, 40),
                (
                    tree_drop_rect.centerx - 15,
                    tree_drop_rect.centery - 30,
                    30,
                    180
                )
            )

            pygame.draw.circle(
                screen,
                (60, 150, 60),
                (
                    tree_drop_rect.centerx,
                    tree_drop_rect.centery - 70
                ),
                90
            )


        # DRAGGABLE ITEMS

        for item in biology_items:

            if item["name"] not in biology_used_items:

                pygame.draw.rect(
                    screen,
                    (255, 255, 255),
                    item["rect"]
                )

                pygame.draw.rect(
                    screen,
                    (30, 30, 30),
                    item["rect"],
                    2
                )

                item_text = small_font.render(
                    item["name"],
                    True,
                    (20, 20, 20)
                )

                screen.blit(
                    item_text,
                    (
                        item["rect"].centerx
                        - item_text.get_width() // 2,

                        item["rect"].centery
                        - item_text.get_height() // 2
                    )
                )


        # CLOSE BUTTON

        pygame.draw.rect(
            screen,
            (210, 210, 200),
            biology_minigame_close
        )

        pygame.draw.rect(
            screen,
            (20, 20, 20),
            biology_minigame_close,
            2
        )

        close_text = small_font.render(
            "Close",
            True,
            (20, 20, 20)
        )

        screen.blit(
            close_text,
            (
                biology_minigame_close.centerx
                - close_text.get_width() // 2,

                biology_minigame_close.centery
                - close_text.get_height() // 2
            )
        )


    # --------------------------------------------------
    # DRAW CHEMISTRY COLOUR MIXING MINIGAME
    # --------------------------------------------------

    if show_chemistry_minigame:

        chemistry_box = pygame.Rect(
            120,
            130,
            WIDTH - 240,
            HEIGHT - 220
        )

        pygame.draw.rect(
            screen,
            (245, 245, 235),
            chemistry_box
        )

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            chemistry_box,
            4
        )


        # TITLE

        title_surface = font.render(
            "Chemistry Colour Mixing",
            True,
            (20, 20, 20)
        )

        screen.blit(
            title_surface,
            (
                chemistry_box.x + 30,
                chemistry_box.y + 25
            )
        )


        # TARGET MESSAGE

        message_surface = small_font.render(
            chemistry_message,
            True,
            (20, 20, 20)
        )

        screen.blit(
            message_surface,
            (
                chemistry_box.x + 30,
                chemistry_box.y + 70
            )
        )


        # BEAKER

        pygame.draw.rect(
            screen,
            chemistry_mix_colour,
            chemistry_beaker_rect
        )

        pygame.draw.rect(
            screen,
            (30, 30, 30),
            chemistry_beaker_rect,
            4
        )

        beaker_text = small_font.render(
            "BEAKER",
            True,
            (20, 20, 20)
        )

        screen.blit(
            beaker_text,
            (
                chemistry_beaker_rect.centerx
                - beaker_text.get_width() // 2,

                chemistry_beaker_rect.centery
                - beaker_text.get_height() // 2
            )
        )


        # COLOUR BLOCKS

        for item in chemistry_colours:

            pygame.draw.rect(
                screen,
                item["colour"],
                item["rect"]
            )

            pygame.draw.rect(
                screen,
                (30, 30, 30),
                item["rect"],
                2
            )

            colour_text = small_font.render(
                item["name"],
                True,
                (20, 20, 20)
            )

            screen.blit(
                colour_text,
                (
                    item["rect"].centerx
                    - colour_text.get_width() // 2,

                    item["rect"].centery
                    - colour_text.get_height() // 2
                )
            )


        # CLOSE BUTTON

        pygame.draw.rect(
            screen,
            (210, 210, 200),
            chemistry_close_button
        )

        pygame.draw.rect(
            screen,
            (20, 20, 20),
            chemistry_close_button,
            2
        )

        close_text = small_font.render(
            "Close",
            True,
            (20, 20, 20)
        )

        screen.blit(
            close_text,
            (
                chemistry_close_button.centerx
                - close_text.get_width() // 2,

                chemistry_close_button.centery
                - close_text.get_height() // 2
            )
        )




    # --------------------------------------------------
    # DRAW NPC DIALOGUE
    # --------------------------------------------------

    if show_dialogue:


        pygame.draw.rect(

            screen,

            (20, 20, 20),

            dialogue_box

        )


        pygame.draw.rect(

            screen,

            (255, 255, 255),

            dialogue_box,

            3

        )


        name_surface = font.render(

            dialogue_name,

            True,

            (255, 255, 255)

        )


        text_surface = small_font.render(

            dialogue_text,

            True,

            (255, 255, 255)

        )


        screen.blit(

            name_surface,

            (
                dialogue_box.x + 20,
                dialogue_box.y + 20
            )

        )


        screen.blit(

            text_surface,

            (
                dialogue_box.x + 20,
                dialogue_box.y + 65
            )

        )


        # DIALOGUE CLOSE BUTTON

        pygame.draw.rect(

            screen,

            (70, 70, 70),

            close_button

        )


        pygame.draw.rect(

            screen,

            (255, 255, 255),

            close_button,

            2

        )


        close_text = small_font.render(

            "Close",

            True,

            (255, 255, 255)

        )


        screen.blit(

            close_text,

            (

                close_button.centerx
                -
                close_text.get_width() // 2,

                close_button.centery
                -
                close_text.get_height() // 2

            )

        )

    # --------------------------------------------------
    # DRAW PHYSICS FORCE MINIGAME
    # --------------------------------------------------

    if show_physics_minigame:

        physics_panel = pygame.Rect(
            180,
            150,
            WIDTH - 360,
            HEIGHT - 280
        )

        # MAIN PANEL
        pygame.draw.rect(
            screen,
            (240, 236, 220),
            physics_panel,
            border_radius=18
        )

        pygame.draw.rect(
            screen,
            (57, 65, 26),
            physics_panel,
            5,
            border_radius=18
        )

        # TITLE
        title_surface = font.render(
            "Physics Minigame",
            True,
            (30, 30, 30)
        )

        screen.blit(
            title_surface,
            (
                physics_panel.centerx - title_surface.get_width() // 2,
                physics_panel.y + 25
            )
        )

        # QUESTION
        question_surface = small_font.render(
            "Which force would move the box to the right?",
            True,
            (30, 30, 30)
        )

        screen.blit(
            question_surface,
            (
                physics_panel.centerx - question_surface.get_width() // 2,
                physics_panel.y + 80
            )
        )

        # INSTRUCTION
        instruction_surface = small_font.render(
            "Drag the correct arrow onto the box",
            True,
            (80, 80, 80)
        )

        screen.blit(
            instruction_surface,
            (
                physics_panel.centerx - instruction_surface.get_width() // 2,
                physics_panel.y + 115
            )
        )

        # --------------------------------------------------
        # CRATE / BOX
        # --------------------------------------------------

        pygame.draw.rect(
            screen,
            (155, 105, 60),
            physics_box_rect,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (70, 45, 25),
            physics_box_rect,
            4,
            border_radius=8
        )

        pygame.draw.line(
            screen,
            (95, 60, 30),
            physics_box_rect.topleft,
            physics_box_rect.bottomright,
            7
        )

        pygame.draw.line(
            screen,
            (95, 60, 30),
            physics_box_rect.topright,
            physics_box_rect.bottomleft,
            7
        )

        box_text = small_font.render(
            "BOX",
            True,
            (255, 255, 255)
        )

        screen.blit(
            box_text,
            (
                physics_box_rect.centerx - box_text.get_width() // 2,
                physics_box_rect.centery - box_text.get_height() // 2
            )
        )

        # --------------------------------------------------
        # FORCE CHOICES
        # --------------------------------------------------

        for item in physics_items:

            pygame.draw.rect(
                screen,
                (225, 222, 205),
                item["rect"],
                border_radius=10
            )

            pygame.draw.rect(
                screen,
                (50, 50, 50),
                item["rect"],
                3,
                border_radius=10
            )

            center_x = item["rect"].centerx
            center_y = item["rect"].centery - 5

            # LEFT ARROW
            if item["name"] == "Left":

                pygame.draw.line(
                    screen,
                    (190, 60, 60),
                    (center_x + 25, center_y),
                    (center_x - 20, center_y),
                    8
                )

                pygame.draw.polygon(
                    screen,
                    (190, 60, 60),
                    [
                        (center_x - 30, center_y),
                        (center_x - 10, center_y - 15),
                        (center_x - 10, center_y + 15)
                    ]
                )

            # RIGHT ARROW
            elif item["name"] == "Right":

                pygame.draw.line(
                    screen,
                    (60, 100, 200),
                    (center_x - 25, center_y),
                    (center_x + 20, center_y),
                    8
                )

                pygame.draw.polygon(
                    screen,
                    (60, 100, 200),
                    [
                        (center_x + 30, center_y),
                        (center_x + 10, center_y - 15),
                        (center_x + 10, center_y + 15)
                    ]
                )

            # UP ARROW
            elif item["name"] == "Up":

                pygame.draw.line(
                    screen,
                    (70, 160, 80),
                    (center_x, center_y + 20),
                    (center_x, center_y - 20),
                    8
                )

                pygame.draw.polygon(
                    screen,
                    (70, 160, 80),
                    [
                        (center_x, center_y - 30),
                        (center_x - 15, center_y - 10),
                        (center_x + 15, center_y - 10)
                    ]
                )

            # LABEL
            item_text = small_font.render(
                item["name"],
                True,
                (25, 25, 25)
            )

            screen.blit(
                item_text,
                (
                    item["rect"].centerx - item_text.get_width() // 2,
                    item["rect"].bottom - 25
                )
            )

        # --------------------------------------------------
        # RESULT MESSAGE
        # --------------------------------------------------

        if physics_result != "":

            result_surface = small_font.render(
                physics_result,
                True,
                (25, 25, 25)
            )

            screen.blit(
                result_surface,
                (
                    physics_panel.centerx - result_surface.get_width() // 2,
                    physics_panel.bottom - 70
                )
            )

        # --------------------------------------------------
        # CLOSE BUTTON
        # --------------------------------------------------

        pygame.draw.rect(
            screen,
            (210, 210, 195),
            physics_minigame_close,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (40, 40, 40),
            physics_minigame_close,
            2,
            border_radius=8
        )

        close_text = small_font.render(
            "Close",
            True,
            (20, 20, 20)
        )

        screen.blit(
            close_text,
            (
                physics_minigame_close.centerx - close_text.get_width() // 2,
                physics_minigame_close.centery - close_text.get_height() // 2
            )
        )


    # --------------------------------------------------
    # DRAW TOILET SEARCH MINIGAME
    # --------------------------------------------------

    if show_toilet_minigame:

        toilet_panel = pygame.Rect(
            220,
            170,
            WIDTH - 440,
            HEIGHT - 340
        )

        # PANEL
        pygame.draw.rect(
            screen,
            (240, 236, 220),
            toilet_panel,
            border_radius=18
        )

        pygame.draw.rect(
            screen,
            (50, 50, 50),
            toilet_panel,
            4,
            border_radius=18
        )

        # TITLE
        title_surface = font.render(
            "Search the Toilets",
            True,
            (25, 25, 25)
        )

        screen.blit(
            title_surface,
            (
                toilet_panel.centerx - title_surface.get_width() // 2,
                toilet_panel.y + 30
            )
        )

        # INSTRUCTION
        instruction_surface = small_font.render(
            "One toilet contains a special item...",
            True,
            (70, 70, 70)
        )

        screen.blit(
            instruction_surface,
            (
                toilet_panel.centerx - instruction_surface.get_width() // 2,
                toilet_panel.y + 80
            )
        )

        # TOILET BUTTONS
        for i, button in enumerate(toilet_buttons):

            pygame.draw.rect(
                screen,
                (215, 215, 205),
                button,
                border_radius=12
            )

            pygame.draw.rect(
                screen,
                (40, 40, 40),
                button,
                3,
                border_radius=12
            )

            toilet_text = small_font.render(
                "Toilet " + str(i + 1),
                True,
                (25, 25, 25)
            )

            screen.blit(
                toilet_text,
                (
                    button.centerx - toilet_text.get_width() // 2,
                    button.centery - toilet_text.get_height() // 2
                )
            )

        # RESULT MESSAGE
        if toilet_result != "":

            result_surface = small_font.render(
                toilet_result,
                True,
                (25, 25, 25)
            )

            screen.blit(
                result_surface,
                (
                    toilet_panel.centerx - result_surface.get_width() // 2,
                    toilet_panel.bottom - 80
                )
            )

        # CLOSE BUTTON
        pygame.draw.rect(
            screen,
            (210, 210, 195),
            toilet_close_button,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (40, 40, 40),
            toilet_close_button,
            2,
            border_radius=8
        )

        close_text = small_font.render(
            "Close",
            True,
            (20, 20, 20)
        )

        screen.blit(
            close_text,
            (
                toilet_close_button.centerx - close_text.get_width() // 2,
                toilet_close_button.centery - close_text.get_height() // 2
            )
        )


    # --------------------------------------------------
    # DRAW TELEPORT PROMPT
    # --------------------------------------------------

    if show_teleport_prompt:

        prompt_box = pygame.Rect(
            WIDTH // 2 - 260,
            HEIGHT // 2 - 120,
            520,
            240
        )

        pygame.draw.rect(
            screen,
            (240, 236, 220),
            prompt_box,
            border_radius=15
        )

        pygame.draw.rect(
            screen,
            (40, 40, 40),
            prompt_box,
            4,
            border_radius=15
        )

        prompt_title = font.render(
            "Travel to DTC & Art Block? No turning back!",
            True,
            (25, 25, 25)
        )

        screen.blit(
            prompt_title,
            (
                prompt_box.centerx - prompt_title.get_width() // 2,
                prompt_box.y + 40
            )
        )

        pygame.draw.rect(
            screen,
            (210, 230, 210),
            teleport_yes_button,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (230, 210, 210),
            teleport_no_button,
            border_radius=8
        )

        yes_text = small_font.render(
            "Yes",
            True,
            (20, 20, 20)
        )

        no_text = small_font.render(
            "No",
            True,
            (20, 20, 20)
        )

        screen.blit(
            yes_text,
            (
                teleport_yes_button.centerx - yes_text.get_width() // 2,
                teleport_yes_button.centery - yes_text.get_height() // 2
            )
        )

        screen.blit(
            no_text,
            (
                teleport_no_button.centerx - no_text.get_width() // 2,
                teleport_no_button.centery - no_text.get_height() // 2
            )
        )

    # --------------------------------------------------
    # DRAW NEXT AREA SCREEN
    # --------------------------------------------------

    if show_next_area:

        screen.fill((35, 45, 40))

        title = font.render(
            "DTC & ART BLOCK",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                HEIGHT // 2 - 120
            )
        )

        message = small_font.render(
            "This area is still under construction, I hope you enjoyed the Science Block!",
            True,
            (230, 230, 230)
        )

        screen.blit(
            message,
            (
                WIDTH // 2 - message.get_width() // 2,
                HEIGHT // 2 - 50
            )
        )

        pygame.draw.rect(
            screen,
            (220, 220, 200),
            finish_tour_button,
            border_radius=10
        )

        finish_text = small_font.render(
            "Finish Tour",
            True,
            (30, 30, 30)
        )

        screen.blit(
            finish_text,
            (
                finish_tour_button.centerx - finish_text.get_width() // 2,
                finish_tour_button.centery - finish_text.get_height() // 2
            )
        )


    # --------------------------------------------------
    # DRAW WELCOME SCREEN
    # --------------------------------------------------

    if show_welcome:

        screen.fill((35, 45, 40))

        title = font.render(
            "WELCOME TO THE SBHS SCIENCE BLOCK TOUR",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (
                WIDTH // 2 - title.get_width() // 2,
                120
            )
        )

        how_to_play = font.render(
            "How to Play",
            True,
            (255, 255, 255)
        )

        screen.blit(
            how_to_play,
            (
                WIDTH // 2 - how_to_play.get_width() // 2,
                200
            )
        )

        instructions = [
            "WASD - Move",
            "E - Interact with teachers and objects",
            "Mouse - Click buttons and minigame options",
            "Walk away from an NPC to close their dialogue",
            "",
            "Explore the Science Block, complete the activities,",
            "and make your way to the end of the tour."
        ]

        for i, line in enumerate(instructions):

            instruction_text = small_font.render(
                line,
                True,
                (230, 230, 230)
            )

            screen.blit(
                instruction_text,
                (
                    WIDTH // 2 - instruction_text.get_width() // 2,
                    270 + i * 45
                )
            )

        pygame.draw.rect(
            screen,
            (220, 220, 200),
            start_tour_button,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            (40, 40, 40),
            start_tour_button,
            3,
            border_radius=10
        )

        start_text = small_font.render(
            "START TOUR",
            True,
            (30, 30, 30)
        )

        screen.blit(
            start_text,
            (
                start_tour_button.centerx - start_text.get_width() // 2,
                start_tour_button.centery - start_text.get_height() // 2
            )
        )

    # --------------------------------------------------
    # UPDATE DISPLAY
    # --------------------------------------------------

    # Present the completed frame and limit the game loop to 60 frames per second.

    pygame.display.flip()

    clock.tick(60)


pygame.quit()