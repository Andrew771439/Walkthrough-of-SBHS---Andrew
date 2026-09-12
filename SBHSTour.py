import pygame
import json
import os

pygame.init()

# -------------------------
# WINDOW
# -------------------------

WIDTH = 1580
HEIGHT = 920

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SBHS Tour")

clock = pygame.time.Clock()


# -------------------------
# FILE PATHS
# -------------------------

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


# -------------------------
# LOAD LDTK
# -------------------------

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


# -------------------------
# LOAD IMAGES
# -------------------------

map_image = pygame.image.load(
    map_image_path
).convert_alpha()

player_image = pygame.image.load(
    player_image_path
).convert_alpha()


# Make player a sensible size
player_image = pygame.transform.scale(
    player_image,
    (40, 40)
)

MAP_WIDTH = map_image.get_width()
MAP_HEIGHT = map_image.get_height()


# -------------------------
# FIND PLAYER SPAWN
# -------------------------

player_x = 144
player_y = 528

for layer in science_level["layerInstances"]:

    if layer["__identifier"] == "Spawn_and_teleport":

        for entity in layer["entityInstances"]:

            if entity["__identifier"] == "Science_block_spawn":

                for field in entity["fieldInstances"]:

                    if (
                        field["__identifier"] == "SpawnID"
                        and field["__value"] == "Science_Block_Initial"
                    ):

                        player_x = entity["px"][0]
                        player_y = entity["px"][1]

                        print(
                            "Player spawn:",
                            player_x,
                            player_y
                        )


# -------------------------
# PLAYER SETTINGS
# -------------------------

PLAYER_SPEED = 4

player_rect = pygame.Rect(
    player_x,
    player_y,
    40,
    40
)


# -------------------------
# CAMERA
# -------------------------

camera_x = 0
camera_y = 0


# -------------------------
# MAIN LOOP
# -------------------------

running = True

while running:

    # -------------------------
    # EVENTS
    # -------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False


    # -------------------------
    # PLAYER MOVEMENT
    # -------------------------

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


    player_rect.x += move_x
    player_rect.y += move_y


    # -------------------------
    # KEEP PLAYER ON MAP
    # -------------------------

    if player_rect.left < 0:
        player_rect.left = 0

    if player_rect.right > MAP_WIDTH:
        player_rect.right = MAP_WIDTH

    if player_rect.top < 0:
        player_rect.top = 0

    if player_rect.bottom > MAP_HEIGHT:
        player_rect.bottom = MAP_HEIGHT


    # -------------------------
    # CAMERA FOLLOWS PLAYER
    # -------------------------

    camera_x = (
        player_rect.centerx
        - WIDTH // 2
    )

    camera_y = (
        player_rect.centery
        - HEIGHT // 2
    )


    # Stop camera going outside map

    camera_x = max(
        0,
        min(
            camera_x,
            MAP_WIDTH - WIDTH
        )
    )

    camera_y = max(
        0,
        min(
            camera_y,
            MAP_HEIGHT - HEIGHT
        )
    )


    # -------------------------
    # DRAW MAP
    # -------------------------

    screen.fill((30, 30, 30))

    screen.blit(
        map_image,
        (-camera_x, -camera_y)
    )


    # -------------------------
    # DRAW PLAYER
    # -------------------------

    screen.blit(
        player_image,
        (
            player_rect.x - camera_x,
            player_rect.y - camera_y
        )
    )



    # -------------------------
    # UPDATE DISPLAY
    # -------------------------

    pygame.display.flip()

    clock.tick(60)



pygame.quit()