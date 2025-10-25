from customTypes import SubjectCategory

class Subject:
    idCounter: int = 0
    def __init__(self, name: str, category: SubjectCategory) -> None:
        Subject.idCounter += 1
        self.__id = Subject.idCounter
        self.name = name
        self.category = category

# 1
GERMAN = Subject('Deutsch', SubjectCategory.LangArt)
ENGLISH = Subject('Englisch', SubjectCategory.LangArt)
FRENCH = Subject('Französisch', SubjectCategory.LangArt)
SPANISH = Subject('Spanisch', SubjectCategory.LangArt)
LATIN = Subject('Latein', SubjectCategory.LangArt)
ARTS = Subject('Bildende Kunst', SubjectCategory.LangArt)
MUSIC = Subject('Musik', SubjectCategory.LangArt)
DS = Subject('Darstellendes Spiel', SubjectCategory.LangArt)

# 2
HISTORY = Subject('Geschichte', SubjectCategory.Political)
POLITICS = Subject('Politikwissenschaft', SubjectCategory.Political)
GEOGRAPHY = Subject('Geographie', SubjectCategory.Political)
PHILOSOPHY = Subject('Philosophie', SubjectCategory.Political)

# 3
MATHEMATICS = Subject('Mathematik', SubjectCategory.MathScience)
PHYSICS = Subject('Physik', SubjectCategory.MathScience)
CHEMISTRY = Subject('Chemie', SubjectCategory.MathScience)
BIOLOGY = Subject('Biologie', SubjectCategory.MathScience)
COMPUTER_SCIENCE = Subject('Informatik', SubjectCategory.MathScience)

# 4
PHYSICAL_EDUCATION = Subject('Sport', SubjectCategory.Physical)