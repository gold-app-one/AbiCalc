from __future__ import annotations


class I18nProvider:
    _LABELS: dict[str, dict[str, str]] = {
        "de": {
            "app.title": "AbiCalc",
            "main.title": "Hauptmenü",
            "main.grades": "Noten bearbeiten",
            "main.subjects": "Fächer und LKs",
            "main.exams": "Prüfungen",
            "main.results": "Ergebnisse berechnen",
            "main.settings": "Einstellungen",
            "main.quit": "Beenden",
            "main.menu_hint": "Drücke 1-6 zur Auswahl.",
            "screen.back": "Zurück",
            "screen.not_implemented": "Dieser Bereich wird gerade aufgebaut.",
            "settings.title": "Einstellungen",
            "settings.theme": "Theme",
            "settings.language": "Sprache",
            "settings.result_limit": "Top-N Ergebnisse",
            "settings.saved": "Konfiguration gespeichert.",
            "subjects.title": "Fächer und Leistungskurse",
            "subjects.current": "Aktülle Leistungskurse",
            "subjects.hint": "Wähle LK1 und LK2. Gleiches Fach für beide LKs ist nicht erlaubt.",
            "subjects.lk1_prev": "LK1 vorheriges Fach",
            "subjects.lk1_next": "LK1 nächstes Fach",
            "subjects.lk2_prev": "LK2 vorheriges Fach",
            "subjects.lk2_next": "LK2 nächstes Fach",
            "subjects.invalid_duplicate": "LK1 und LK2 dürfen nicht identisch sein.",
            "grades.title": "Noten Q1 bis Q4",
            "grades.semester": "Semester",
            "grades.course": "Kurs",
            "grades.prev": "Vorheriger",
            "grades.next": "Nächster",
            "grades.grade_minus": "Note -1",
            "grades.grade_plus": "Note +1",
            "grades.toggle_unknown": "UNKNOWN umschalten",
            "grades.hint": "Hinweis: Noten werden auf 0 bis 15 begrenzt.",
            "exams.title": "Abiturprüfungen",
            "results.title": "Ergebnisse",
            "results.empty": "Keine Kombinationen gefunden.",
            "results.hint": "Hinweis: Die Detailansicht folgt im nächsten Implementierungsschritt.",
        },
        "en": {
            "app.title": "AbiCalc",
            "main.title": "Main Menu",
            "main.grades": "Edit Grades",
            "main.subjects": "Subjects and LKs",
            "main.exams": "Exams",
            "main.results": "Calculate Results",
            "main.settings": "Settings",
            "main.quit": "Quit",
            "main.menu_hint": "Press 1-6 to choose.",
            "screen.back": "Back",
            "screen.not_implemented": "This section is currently under construction.",
            "settings.title": "Settings",
            "settings.theme": "Theme",
            "settings.language": "Language",
            "settings.result_limit": "Top-N results",
            "settings.saved": "Configuration saved.",
            "subjects.title": "Subjects and Leistungskurse",
            "subjects.current": "Current Leistungskurse",
            "subjects.hint": "Choose LK1 and LK2. Same subject for both LKs is not allowed.",
            "subjects.lk1_prev": "LK1 previous subject",
            "subjects.lk1_next": "LK1 next subject",
            "subjects.lk2_prev": "LK2 previous subject",
            "subjects.lk2_next": "LK2 next subject",
            "subjects.invalid_duplicate": "LK1 and LK2 cannot be identical.",
            "grades.title": "Grades Q1 to Q4",
            "grades.semester": "Semester",
            "grades.course": "Course",
            "grades.prev": "Previous",
            "grades.next": "Next",
            "grades.grade_minus": "Grade -1",
            "grades.grade_plus": "Grade +1",
            "grades.toggle_unknown": "Toggle UNKNOWN",
            "grades.hint": "Hint: Grades are clamped to 0 to 15.",
            "exams.title": "Final Exams",
            "results.title": "Results",
            "results.empty": "No combinations found.",
            "results.hint": "Hint: Detail view will be implemented next.",
        },
    }

    def __init__(self, language: str = "de") -> None:
        self._language = language if language in self._LABELS else "de"

    @property
    def language(self) -> str:
        return self._language

    def set_language(self, language: str) -> None:
        if language in self._LABELS:
            self._language = language

    def t(self, key: str) -> str:
        lang_table = self._LABELS.get(self._language, self._LABELS["de"])
        if key in lang_table:
            return lang_table[key]

        # Fallback to German default before exposing raw keys.
        de_valü = self._LABELS["de"].get(key)
        return de_valü if de_valü is not None else key
