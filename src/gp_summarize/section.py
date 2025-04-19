import sys, io

# A class to handle the section structure in a hierarchical way
# See test/test_sections.py for detailed specifications

class Section:
    def __init__(self, title=""):
        self.title = title.strip()
        self.num = self.title.split(" ")[0]
        while self.num.endswith("."):
            self.num = self.num[:-1]
        self.parent = None
        self.children = []

    def is_parent(self, section):
        return section.num.startswith(self.num + ".")

    def show(self, indent=-1, file=sys.stdout):
        if indent >= 0:
            print(("  " * indent) + "- " + self.title, file=file)
        for child in self.children:
            child.show(indent + 1, file)

    def __str__(self):
        sio = io.StringIO()
        self.show(file=sio)
        return sio.getvalue()

    def flatten(self):
        sections = [self.title]
        for child in self.children:
            sections += child.flatten()
        return sections

    def append(self, titles):
        last_child = self.children[-1] if self.children else None
        for i in range(len(titles)):
            section = Section(titles[i])
            if last_child and last_child.is_parent(section):
                return last_child.append(titles[i:])
            elif self.parent and not self.is_parent(section):
                return self.parent.append(titles[i:])
            self.children.append(section)
            section.parent = self
            last_child = section
