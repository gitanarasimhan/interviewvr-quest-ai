# InterviewVR Unity project

This folder is the start of the Unity client for InterviewVR AI.

## Included scripts

- `InterviewController.cs` — loads questions from the Python backend and evaluates answers
- `KeyboardInputController.cs` — simulates a spoken answer in the editor using keyboard input
- `InterviewData.cs` — shared interview data model

## Open in Unity

Open this folder as a Unity project and create a scene containing:

- an empty GameObject called `InterviewManager`
- `InterviewController` attached to it
- `KeyboardInputController` attached to the same object

This gives a fast Windows-first workflow without requiring Meta Quest hardware.
