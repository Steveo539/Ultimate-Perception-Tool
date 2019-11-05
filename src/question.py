class Question:
    def __init__(self, type, text):
        self.type = type
        self.text = text
        # TODO: link with database to create unique question id
        self.id = 0

    def set_title(self, title):
        self.text = title

    def get_title(self):
        return self.text

    def get_type(self):
        return self.type

    def get_id(self):
        return self.id


class MultipleChoice(Question):
    def __init__(self, text, choices):
        super().__init__("Multiple Choice", text)
        self.option = choices

    def set_choice(self, choices):
        self.option = choices

    def add_choice(self, choice):
        self.option.append(choice)


class ShortAnswer(Question):
    def __init__(self, title):
        super().__init__("SHort Answer", title)


class Scale(Question):
    def __init__(self, title):
        super().__init__("Scale", title)
        self.choice = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
