from telegram.ext import BaseFilter


# TODO: ensure that the filter works with any update, not just message
class FSMFilter(BaseFilter):
    def filter(self, message, needed_state: str):
        pass
