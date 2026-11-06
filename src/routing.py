class UserRouter:
    def __init__(self, user_history_count):
        self.user_history_count = user_history_count

    def get_history_count(self, user_id):
        return int(
            self.user_history_count.get(
                int(user_id),
                0
            )
        )

    def get_segment(self, user_id):
        history_count = self.get_history_count(
            user_id
        )

        if history_count == 0:
            return "new_user"

        if history_count <= 2:
            return "low_history"

        return "established"