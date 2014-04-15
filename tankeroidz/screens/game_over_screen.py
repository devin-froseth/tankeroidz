import pygame
import screen
import title_screen
import console
from pygame.locals import *

class GameOverScreen(screen.Screen):
    def create(self, *args, **kwargs):
        try:
            self.score = kwargs['score']
        except KeyError:
            console.error('Score not sent to GameOverScreen. No stats recorded.')

        self.log_score()

    def log_score(self):
        scores_file = open("config/scores.txt", 'r+')

        scores_list = []
        for line in scores_file:
            scores_list.append(int(line.strip()))
        scores_list.append(int(self.score))

        scores_file.seek(0)
        scores_file.write('\n'.join([str(s) for s in scores_list]))
        scores_file.truncate()
        scores_file.close()

        scores_avg = sum(scores_list) / float(len(scores_list))
        scores_max = max(scores_list)
        scores_min = min(scores_list)

    def handle_input(self, event):
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                self.game.set_screen(title_screen.TitleScreen(self.game))

    def render(self):
        self.game.frame.fill((128, 128, 0))
