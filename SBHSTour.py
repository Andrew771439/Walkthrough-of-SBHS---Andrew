import pygame
import pytmx

WIDTH, HEIGHT, FPS = 800, 600, 60
NAVY = (9, 24, 43)

def run_game():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SBHS Tour")
    clock = pygame.time.Clock()

    tmx_data = pytmx.load_pygame(
        "/Users/andcam_2010/Library/CloudStorage/OneDrive-SouthlandBoys'HighSchool/Level 2 DTC/AS91893/Walkthrough-of-SBHS---Andrew/Science_Block map.tmx"
    )

    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(NAVY)

        for layer in tmx_data.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = tmx_data.get_tile_image_by_gid(gid)

                    if tile:
                        screen.blit(
                            tile,
                            (
                                x * tmx_data.tilewidth,
                                y * tmx_data.tileheight
                            )
                        )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_game()
