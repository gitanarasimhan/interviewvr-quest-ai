# InterviewVR AI MVP

This folder contains the Unity client for the InterviewVR AI MVP. It is designed to run on a Windows PC and uses simulated keyboard input in the Unity Editor so Quest hardware is not required in the first phase.

## Included scripts

- `InterviewData.cs` — shared data model for questions, feedback, and reports
- `InterviewController.cs` — loads questions, submits answers, evaluates them, and ends with a final report
- `KeyboardInputController.cs` — simulates verbal responses using keyboard input for editor testing

## Running the app

1. Open `unity/InterviewVR` as a Unity project.
2. Create a scene with an empty GameObject called `InterviewManager`.
3. Attach `InterviewController` and `KeyboardInputController` to it.
4. Start the Python API from `backend`.
5. Press Play in Unity and use the Space key to simulate an answer.
6. Use R to reset the interview.

## Backend startup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

This keeps the product small and reliable while matching the requested Windows-first architecture.
