import pygame
import screen
import title_screen
import console
import ui
from pygame.locals import *

class GameOverScreen(screen.Screen):
    def create(self, *args, **kwargs):
        try:
            self.score = kwargs['score']
        except KeyError:
            console.error('Score not sent to GameOverScreen. No stats recorded.')

        self.log_score()
        self.create_ui()

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

        self.scores_avg = sum(scores_list) / float(len(scores_list))
        self.scores_max = max(scores_list)
        self.scores_min = min(scores_list)

    def create_ui(self):
       gui = ui.load_ui("resources/ui/game_over_ui.ini",
            (self.game.settings['width'], self.game.settings['height']))
       
#       gui['max_score'].text += " " + str(self.scores_max)
       gui['max_score'].text += " " + str(self.scores_max + 1) + " (Devin Froseth)"
       gui['min_score'].text += " " + str(self.scores_min)
       gui['avg_score'].text += " " + str(int(self.scores_avg))
       
       self.ui = gui
       
    def handle_input(self, event):
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                self.game.set_screen(title_screen.TitleScreen(self.game))

    def render(self):
        self.game.frame.fill((128, 128, 0))
        self.ui.render(self.game.frame)