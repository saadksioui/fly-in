import pygame

if __name__ == "__main__":
    nodes = {"A": (100, 100), "B": (400, 200), "C": (200, 500)}
    edges = [("A", "B"), ("B", "C")]
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    font = pygame.font.Font(None, 74)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill("purple")
        
        for start, end in edges:
            pygame.draw.line(screen, (0, 0, 255), nodes[start], nodes[end])

        for node, value in nodes.items():
            pygame.draw.circle(screen, (255, 0, 0), value, 50)
            screen.blit(font.render(node, True, (255, 255, 255)), value)
        
        

        pygame.display.flip()

