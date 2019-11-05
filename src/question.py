class Question:
    def __init__(self, type, title):
        self.type = type
        self.title = title
        # TODO: link with database to create unique question id
        self.question_id = 0

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def get_type(self):
        return self.type

    def get_id(self):
        return self.question_id


class MultipleChoice(Question):
    def __init__(self, title, choices):
        super().__init__("Multiple Choice", title)
        self.choices = choices

    def set_choice(self, choices):
        self.choices = choices

    def add_choice(self, choice):
        self.choices.append(choice)


class ShortAnswer(Question):
    def __init__(self, title):
        super().__init__("SHort Answer", title)


class Scale(Question):
    def __init__(self, title):
        super().__init__("Scale", title)
        self.choice = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
