from datetime import datetime, timedelta
from random import betavariate


class CockController:

    def __init__(self):
        self.value = dict()

    def get(self, username):
        if username in self.value:
            if CockController.need_update(self.value[username][0]):
                self.value[username][1] = CockController.generate_value()
                self.value[username][0] = datetime.now()
        else:
            row = (datetime.now(), CockController.generate_value())
            self.value[username] = row

        return self.value[username][1]

    @staticmethod
    def need_update(date):
        dt = datetime.now()
        last_update_delta = dt - date
        return last_update_delta >= timedelta(days=1)

    @staticmethod
    def generate_value():
        return int(betavariate(alpha=2, beta=5) * 50)
