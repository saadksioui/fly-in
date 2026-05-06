import pygame

if __name__ == "__main__":
    running = True
    pygame.init()
    
    screen = pygame.display.set_mode((1280, 720))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill("black")
        pygame.display.flip()
    pygame.quit()
