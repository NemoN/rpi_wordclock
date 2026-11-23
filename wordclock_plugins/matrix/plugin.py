# Authored by Markus E.

from wordclock_plugins.time_matrix.plugin import plugin as TimeMatrix


class plugin(TimeMatrix):
    """Display green matrix rain on a black background."""

    def __init__(self, config):
        super().__init__(config)
        self.name = 'matrix'
        self.pretty_name = 'Matrix'
        self.description = 'Why do my eyes hurt?'
        self.show_scroll_text = False

    def update_background(self, background, wcd, width, height, clock_time):
        background[:] = bytes(len(background))
