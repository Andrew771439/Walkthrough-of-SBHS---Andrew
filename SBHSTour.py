import pygame
import json
import os

pygame.init()


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

                        player_x = entity["px"][0]
                        player_y = entity["px"][1]


print(
    "Player spawn:",
    player_x,
    player_y
)


# --------------------------------------------------
# PLAYER
# --------------------------------------------------

PLAYER_SPEED = 4

player_rect = pygame.Rect(
    player_x,
    player_y,
    40,
    40
)


# --------------------------------------------------
# COLLISION FUNCTIONS
# --------------------------------------------------

def move_player_x(amount):

    player_rect.x += amount

    for wall in collision_rects:

        if player_rect.colliderect(wall):

            if amount > 0:
                player_rect.right = wall.left

            elif amount < 0:
                player_rect.left = wall.right


def move_player_y(amount):

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


INTERACTION_DISTANCE = 40


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
# MAIN LOOP
# --------------------------------------------------

running = True


while running:


    # --------------------------------------------------
    # EVENTS
    # --------------------------------------------------

    for event in pygame.event.get():


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


                interaction_found = False


                # --------------------------------------
                # CHECK WHITEBOARD / INTERACTABLES FIRST
                # --------------------------------------

                for interactable in interactables:


                    interactable_rect = pygame.Rect(

                        interactable["x"],

                        interactable["y"],

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


                        if interactable["id"] == "biology_question":
                            show_dialogue = False
                            show_physics_question = False
                            show_biology_question = True
                            biology_result = ""
                            interaction_found = True
                            break

                        elif interactable["id"] == "physics_question":
                            show_dialogue = False
                            show_biology_question = False
                            show_physics_question = True
                            physics_result = ""
                            interaction_found = True
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

                            dialogue_text = npc["dialogue"]

                            show_dialogue = True

                            show_biology_question = False

                            break


        # ----------------------------------------------
        # MOUSE CLICK
        # ----------------------------------------------

        if event.type == pygame.MOUSEBUTTONDOWN:


            if event.button == 1:


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


    move_x = 0
    move_y = 0


    if keys[pygame.K_w]:

        move_y -= PLAYER_SPEED


    if keys[pygame.K_s]:

        move_y += PLAYER_SPEED


    if keys[pygame.K_a]:

        move_x -= PLAYER_SPEED


    if keys[pygame.K_d]:

        move_x += PLAYER_SPEED


    move_player_x(
        move_x
    )

    move_player_y(
        move_y
    )


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

            interactable["x"],

            interactable["y"],

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

    screen.blit(

        player_image,

        (
            player_rect.x - camera_x,
            player_rect.y - camera_y
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


    # --------------------------------------------------
    # INTERACTION PROMPT
    # --------------------------------------------------

    if (
        (
            nearby_npc is not None
            or
            nearby_interactable is not None
        )
        and
        not show_dialogue
        and
        not show_biology_question
        and
        not show_physics_question
    ):


        if (
            nearby_interactable is not None
            and
            nearby_interactable["id"] == "biology_question"
        ):

            prompt_text = "Press E to answer question"

        else:

            prompt_text = "Press E to interact"


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
    # UPDATE DISPLAY
    # --------------------------------------------------

    pygame.display.flip()

    clock.tick(60)


pygame.quit()