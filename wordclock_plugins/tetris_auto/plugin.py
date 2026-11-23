import random

from wordclock_plugins.tetris.plugin import plugin as Tetris


class plugin(Tetris):
    def __init__(self, config):
        super().__init__(config)
        self.name = 'tetris_auto'
        self.pretty_name = 'Tetris Auto'
        self.description = 'Tetris plays automatically and restarts.'

    def run(self, wcd, wci):
        width, height = wcd.get_wca_width(), wcd.get_wca_height()
        exit_events = (wci.EVENT_BUTTON_RETURN, wci.EVENT_EXIT_PLUGIN,
                       wci.EVENT_NEXT_PLUGIN_REQUESTED)
        while True:
            self.field = [[None for _ in range(width)] for _ in range(height)]
            wcd.resetDisplay()
            while True:
                piece = random.choice(self.bricks).clone()
                placement = self.choose_placement(piece, width, height)
                if placement is None:
                    break
                piece, x, target_y = placement
                y = -piece.padTop - piece.innerHeight + 1
                while y < target_y:
                    self.carve(piece, x, y)
                    self.draw(wcd)
                    self.uncarve(piece, x, y)
                    if wci.waitForEvent(0.15) in exit_events:
                        return
                    y += 1
                self.carve(piece, x, target_y)
                self.draw(wcd)
                self.clear_lines(wcd)
                if wci.waitForEvent(0.15) in exit_events:
                    return
            if wci.waitForEvent(1) in exit_events:
                return

    def choose_placement(self, piece, width, height):
        best = None
        for rotation in range(4):
            if rotation:
                piece = piece.rotate_cw()
            for x in range(-piece.padLeft, width - piece.innerWidth - piece.padLeft + 1):
                y = -piece.padTop - piece.innerHeight + 1
                if self.collision(piece, x, y):
                    continue
                bottom = height - piece.padTop - piece.innerHeight
                while y < bottom and not self.collision(piece, x, y + 1):
                    y += 1
                if y + piece.padTop < 0:
                    continue
                self.carve(piece, x, y)
                score = self.score_field(width, height)
                self.uncarve(piece, x, y)
                if best is None or score > best[0]:
                    best = (score, piece, x, y)
        return None if best is None else best[1:]

    def score_field(self, width, height):
        full = sum(all(cell is not None for cell in row) for row in self.field)
        holes = 0
        total_height = 0
        heights = []
        for x in range(width):
            filled = False
            column_height = 0
            for y in range(height):
                if self.field[y][x] is not None:
                    if not filled:
                        column_height = height - y
                        filled = True
                elif filled:
                    holes += 1
            heights.append(column_height)
            total_height += column_height
        roughness = sum(abs(a - b) for a, b in zip(heights, heights[1:]))
        return 10 * full - 8 * holes - total_height - roughness
