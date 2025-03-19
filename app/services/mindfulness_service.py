class MindfulnessService:
    break_activities = [
        "Take a deep breath and stretch your arms.",
        "Close your eyes and focus on your breathing for one minute.",
        "Take a quick walk or stand up to stretch.",
        "Grab a glass of water and hydrate.",
        "Write down one thing you're grateful for today.",
    ]

    def get_suggestion(self) -> str:
        return random.choice(self.break_activities)

    def get_personalized_suggestion(self, stress_level: int) -> str:
        if stress_level > 7:
            return "Take a deep breath and go for a short walk."
        elif stress_level > 4:
            return "Pause and write down something you're grateful for."
        else:
            return "Stay hydrated and take a moment to stretch."

    def get_dynamic_suggestion(self, stress_level: int):
        """
        Provide a dynamic suggestion based on the user's stress level.
        """
        if stress_level > 7:
            return "Take a deep breath and go for a 5-minute walk."
        elif stress_level > 4:
            return "Pause and write down one positive thought."
        else:
            return "Hydrate and take a moment to stretch."
