from collections import deque

from wordclock_plugins.snake.plugin import plugin as Snake
from wordclock_plugins.snake.Snakeobject import Snakeobject
import wordclock_tools.wordclock_colors as colors


class plugin(Snake):
    def __init__(self, config):
        super().__init__(config)
        self.name = 'snake_auto'
        self.pretty_name = 'Snake Auto'
        self.description = 'Snake plays automatically and restarts.'

    def run(self, wcd, wci):
        exit_events = (wci.EVENT_BUTTON_RETURN, wci.EVENT_EXIT_PLUGIN,
                       wci.EVENT_NEXT_PLUGIN_REQUESTED)
        while True:
            snake = Snakeobject(11, 10)
            self.init(snake, wcd)
            while not snake.data['isGameOver']:
                direction = self.choose_direction(snake)
                if direction is None:
                    break
                row, col = snake.data['headRow'], snake.data['headCol']
                board = snake.data['snakeBoard']
                if board[row + direction[0]][col + direction[1]] < 0 and all(
                        cell != 0 for line in board for cell in line):
                    break
                self.moveSnake(snake, *direction)
                self.redrawAll(snake, wcd)
                if wci.waitForEvent(0.2) in exit_events:
                    return
            if wci.waitForEvent(1) in exit_events:
                return

    def updatePoints(self, snake, wcd):
        points = snake.data['points'] // 12
        for i in range(4):
            color = colors.PINK if points >= i + 5 else colors.YELLOW if points >= i + 1 else colors.BLACK
            wcd.setColorByMinute(i, color)

    def choose_direction(self, snake):
        board = snake.data['snakeBoard']
        rows, cols = len(board), len(board[0])
        head = (snake.data['headRow'], snake.data['headCol'])
        moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        queue = deque([(head, None)])
        visited = {head}
        choices = []
        while queue:
            (row, col), first = queue.popleft()
            for dr, dc in moves:
                nxt = (row + dr, col + dc)
                if not (0 <= nxt[0] < rows and 0 <= nxt[1] < cols) or nxt in visited:
                    continue
                cell = board[nxt[0]][nxt[1]]
                if cell > 1:
                    continue
                direction = first or (dr, dc)
                if first is None:
                    choices.append(direction)
                if cell < 0:
                    return direction
                visited.add(nxt)
                queue.append((nxt, direction))
        return choices[0] if choices else None
