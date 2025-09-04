import pygame
import subprocess
import sys
import os

pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Skyjo - Startmenü")
font = pygame.font.SysFont(None, 36)

WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BLUE = (70, 130, 180)
BLACK = (0, 0, 0)

def draw_button(text, rect, color):
    pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def start_process(script_name):
    if sys.platform.startswith('win'):
        python_exe = "python"
    else:
        python_exe = "python3"
    subprocess.Popen([python_exe, script_name])

def main():
    clock = pygame.time.Clock()

    host_button = pygame.Rect(150, 120, 300, 60)
    join_button = pygame.Rect(150, 220, 300, 60)

    running = True
    while running:
        screen.fill(GREEN)
        draw_button("Spiel erstellen (Host)", host_button, BLUE)
        draw_button("Spiel beitreten (Client)", join_button, BLUE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if host_button.collidepoint(event.pos):
                    start_process("net/server.py")
                    running = False
                elif join_button.collidepoint(event.pos):
                    start_process("net/client.py")
                    running = False

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
