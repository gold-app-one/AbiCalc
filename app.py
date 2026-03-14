from __future__ import annotations
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static

from classes import Calculator, Course, CreditedCombination, FinalExams, SaveState
from subjects import *

saveState = SaveState() # TODO: dynamic loading

def getGrades() -> list[CreditedCombination]:
    courses: list[Course] = saveState.getQ(1) + saveState.getQ(2) + saveState.getQ(3) + saveState.getQ(4)
    finals: FinalExams = saveState.getFinals()
    calculator = Calculator(courses, finals)

    bestCombinations: list[CreditedCombination] = calculator.returnBestCombinations(1)

    return bestCombinations

class SettingsScreen(Screen[None]):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Einstellungen", classes="menu-title")
        yield Static("Hier könnten wunderschöne Einstellungen sein\n"
                     "An/Aus?",
                     id="settings_content")
        yield Button("Zurück", id="settings_back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "settings_back":
            self.app.pop_screen() # type: ignore

class GradesScreen(Screen[None]):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Noten", classes="menu-title")
        yield Static("Hier tragen wir unsere Noten ein\n"
                     "Note 1\nNote2\nNote3",
                     id="grades_content")
        yield Button("Back to Main", id="grades_back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "grades_back":
            self.app.pop_screen() # type: ignore

class SubjectsScreen(Screen[None]):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Noten", classes="menu-title")
        yield Static("Hier tragen wir unsere Fächer ein\n"
                     "Deutsch\nMathe\nEnglisch",
                     id="subjects_content")
        yield Button("Back to Main", id="subjects_back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "subjects_back":
            self.app.pop_screen() # type: ignore

class ResultsScreen(Screen[None]):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Noten", classes="menu-title")
        for i, comb in enumerate(getGrades()):
            for j, line in enumerate(str(comb).splitlines()):
                yield Static(content=line, id=f"resultsLine_{i}_{j}", markup=False)
        yield Button("Back to Main", id="results_back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "results_back":
            self.app.pop_screen() # type: ignore

# === MAIN APP

class MainApp(App[None]):
    CSS = """
    .menu-title {
        text-align: center;
        margin: 2;
        background: darkblue;
        color: white;
    }
    Button {
        margin: 1;
    }
    #content1, #content2 {
        margin: 2 1;
        height: 10;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Hauptmenü", classes="menu-title")
        yield Button("Noten bearbeiten", id="grades")
        yield Button("Fächer bearbeiten", id="subjects")
        yield Button("Ergebnisse berechnen", id="results")
        yield Button("Einstellungen", id="settings")
        yield Button("Beenden", id="quit")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "settings":
            self.push_screen(SettingsScreen())
        elif event.button.id == "grades":
            self.push_screen(GradesScreen())
        elif event.button.id == "subjects":
            self.push_screen(SubjectsScreen())
        elif event.button.id == "results":
            self.push_screen(ResultsScreen())
        elif event.button.id == "quit":
            self.exit()


if __name__ == "__main__":
    MainApp().run()