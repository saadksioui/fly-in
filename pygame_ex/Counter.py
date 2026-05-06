import pygame

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    font = pygame.font.Font(None, 74)
    clock = pygame.time.Clock()
    current_count = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_count += 1
        screen.fill((30, 30, 30))
        pygame.draw.circle(screen, (0, 0, 255), (640, 360), 50)
        screen.blit(font.render(str(current_count), True, (255, 255, 255)), (640, 360))        

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

