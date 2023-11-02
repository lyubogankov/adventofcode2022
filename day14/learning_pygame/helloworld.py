import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode(size=(1300, 700))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() // 2, screen.get_height() // 2)

screen.fill('purple')
while running:
    # poll for events
    for event in pygame.event.get():
        # user clicked topbar X to close the window
        if event.type == pygame.QUIT:
            running = False

    # fill screen to wipe away anything from last frame
    # screen.fill('purple')

    pygame.draw.circle(surface=screen, color='red', center=player_pos, radius=40)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt

    pygame.display.flip()  # "put our work on the screen"

    # limit FPS to 60, dt allows for framerate-independent physics
    dt = clock.tick(60) / 1000

pygame.quit()