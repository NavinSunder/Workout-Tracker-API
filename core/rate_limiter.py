from time import time

class rateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.attempts = {}

    def is_allowed(self, username: str) -> bool:
        current_time = time()

        if username not in self.attempts:
            self.attempts[username] = []

        # remove the attempts outside the window
        self.attempts[username] = [
            attempt
            for attempt in self.attempts[username]
            if current_time - attempt < self.window_seconds
        ]

        if len(self.attempts[username]) >= self.max_attempts:
            return False

        self.attempts[username].append(current_time)

        return True