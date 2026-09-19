import pygame
import json
import os

pygame.init()


# WINDOW


WIDTH = 1580
HEIGHT = 920

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SBHS Tour")

clock = pygame.time.Clock()



# FILE PATHS


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



# LOAD LDTK


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



# LOAD IMAGES

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

biology_image = pygame.image.load(biology_image_path).convert_alpha()
chemistry_image = pygame.image.load(chemistry_image_path).convert_alpha()
physics_image = pygame.image.load(physics_image_path).convert_alpha()
student_image = pygame.image.load(student_image_path).convert_alpha()

biology_image = pygame.transform.scale(biology_image, (40, 40))
chemistry_image = pygame.transform.scale(chemistry_image, (40, 40))
physics_image = pygame.transform.scale(physics_image, (40, 40))
student_image = pygame.transform.scale(student_image, (40, 40))




# LOAD COLLISIONS


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

print("Collision cells loaded:", len(collision_rects))



# FIND PLAYER SPAWN


player_x = 0
player_y = -5

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



# PLAYER SETTINGS


PLAYER_SPEED = 4

player_rect = pygame.Rect(
    player_x,
    player_y,
    40,
    40
)



# COLLISION FUNCTIONS


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

# LOAD NPC POSITIONS

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



# CAMERA


camera_x = 0
camera_y = 0

# INTERACTION

font = pygame.font.Font(None, 32)

show_dialogue = False
dialogue_text = ""
dialogue_name = ""

INTERACTION_DISTANCE = 500


# MAIN LOOP


running = True

while running:

    
    # EVENTS
    

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_e:

                show_dialogue = False

                for npc in npcs:

                    npc_rect = pygame.Rect(
                        npc["x"] + NPC_OFFSET_X,
                        npc["y"] + NPC_OFFSET_Y,
                        40,
                        40
                    )

                    distance_x = abs(
                        player_rect.centerx - npc_rect.centerx
                    )

                    distance_y = abs(
                        player_rect.centery - npc_rect.centery
                    )

                    if (
                        distance_x < INTERACTION_DISTANCE
                        and distance_y < INTERACTION_DISTANCE
                    ):

                        dialogue_name = npc["name"]
                        dialogue_text = npc["dialogue"]
                        show_dialogue = True
                        break


   
    # PLAYER MOVEMENT
   

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


    move_player_x(move_x)
    move_player_y(move_y)


   
    # KEEP PLAYER ON MAP
   

    if player_rect.left < 0:
        player_rect.left = 0

    if player_rect.right > MAP_WIDTH:
        player_rect.right = MAP_WIDTH

    if player_rect.top < 0:
        player_rect.top = 0

    if player_rect.bottom > MAP_HEIGHT:
        player_rect.bottom = MAP_HEIGHT


   
    # CAMERA FOLLOWS PLAYER
   

    camera_x = (
        player_rect.centerx
        - WIDTH // 2
    )

    camera_y = (
        player_rect.centery
        - HEIGHT // 2
    )

    camera_x = max(
        0,
        min(
            camera_x,
            max(0, MAP_WIDTH - WIDTH)
        )
    )

    camera_y = max(
        0,
        min(
            camera_y,
            max(0, MAP_HEIGHT - HEIGHT)
        )
    )


   
    # DRAW MAP
    

    screen.fill((30, 30, 30))

    screen.blit(
        map_image,
        (-camera_x, -camera_y)
    )


    
    # DRAW PLAYER
    

    screen.blit(
        player_image,
        (
            player_rect.x - camera_x,
            player_rect.y - camera_y
        )
    )

        # DRAW NPCS

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

            # DRAW DIALOGUE

    if show_dialogue:

        box = pygame.Rect(
            150,
            HEIGHT - 180,
            WIDTH - 300,
            120
        )

        pygame.draw.rect(
            screen,
            (20, 20, 20),
            box
        )

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            box,
            3
        )

        name_surface = font.render(
            dialogue_name,
            True,
            (255, 255, 255)
        )

        text_surface = font.render(
            dialogue_text,
            True,
            (255, 255, 255)
        )

        screen.blit(
            name_surface,
            (box.x + 20, box.y + 20)
        )

        screen.blit(
            text_surface,
            (box.x + 20, box.y + 60)
        )


    
    # UPDATE DISPLAY
    

    pygame.display.flip()

    clock.tick(60)


pygame.quit()