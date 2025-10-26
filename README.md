# AbiCalc

AbiCalc is a calculator designed for students attending German Gymnasiums in Berlin. It helps you estimate your possible Abitur grades based on your chosen courses and the grades you already know, as well as those that are still unknown. The tool takes into account the complex rules and requirements of the Berlin Abitur system, including Leistungskurse (LK), Grundkurse (GK), final exams, and mandatory subject combinations.

## Features

- Input your course selections and grades for each semester.
- Mark grades as unknown if you do not know them yet.
- Specify your chosen subjects for the final exams (Abiturprüfungen).
- The calculator will compute all valid combinations and show your best possible Abitur outcomes.

## How to Use

1. **Edit `main.py`**:
   - Set your chosen Leistungskurse (LK) subjects by changing `YOUR_LK_1` and `YOUR_LK_2`.
   - Update the `finals` section to reflect your selected final exam subjects and types.
   - Fill in your grades for each course in the `Q1`, `Q2`, `Q3`, and `Q4` lists. Use `UNKNOWN` for grades you do not know yet.
   - Add or remove courses as needed to match your actual curriculum.
2. **Run the program**:
   - Execute `main.py` to see your best possible Abitur grade combinations.

## Example

In `main.py`, you will find comments indicating where to change your subjects and grades:

```python
YOUR_LK_1: Subject = GERMAN  # Change to your first LK subject
YOUR_LK_2: Subject = BIOLOGY  # Change to your second LK subject

# Update the finals section with your chosen exam subjects and types
finals: FinalExams = FinalExams(
    FinalExam(YOUR_LK_1, FinalExamType.LK1, UNKNOWN),
    FinalExam(YOUR_LK_2, FinalExamType.LK2, UNKNOWN),
    FinalExam(ENGLISH, FinalExamType.WRITTEN, UNKNOWN),
    FinalExam(HISTORY, FinalExamType.ORALLY, UNKNOWN),
    FinalExam(MATHEMATICS, FinalExamType.PRESENTATION, UNKNOWN),
    FifthPKType.PP
)

# Fill in your grades for each course and semester
Q1: list[Course] = [
    C(YOUR_LK_1, 10, LK, 1),  # Replace 10 with your actual grade, or UNKNOWN
    ...
]
```

## Requirements

- Python 3.10+
- No external dependencies required

## License

MIT

## Authors

[yoshi-qq](https://github.com/yoshi-qq)  
[type-Ignore](https://github.com/type-Ignore)
