# InterviewVR AI MVP

This folder contains the Unity client for the InterviewVR AI MVP. It is designed to run on a Windows PC and uses simulated keyboard input in the Unity Editor so Quest hardware is not required in the first phase.

## Included scripts

- `InterviewData.cs` — shared data model for the conversation request/response contracts
- `InterviewController.cs` — starts a dynamic AI interview session, submits answers via `/api/interview/chat`, and ends with a final report via `/api/interview/end`
- `KeyboardInputController.cs` — simulates verbal responses using keyboard input for editor testing
- `Network/SecureAPIClient.cs` — HMAC-SHA256 request signer for when `REQUIRE_SIGNATURE=true` on the backend
- `UI/ChatUIController.cs` — chat bubble conversation view (candidate answers left, AI questions/feedback right)
- `UI/FeedbackDisplayController.cs` — shows score/feedback immediately after each answer
- `UI/InterviewProgressController.cs` — progress bar showing interview completion
- `UI/InterviewUIManager.cs` — wires the controller's conversation events into the UI sub-controllers
- `UI/FeedbackPanel.cs` / `UI/ReportPanel.cs` — panel-level renderers for feedback and the final report

## Running the app

1. Open `unity/InterviewVR` as a Unity project.
2. Create a scene with an empty GameObject called `InterviewManager`.
3. Attach `InterviewController` and `KeyboardInputController` to it.
4. Start the Python API from `backend`.
5. Press Play in Unity and use the Space key to simulate an answer to the current AI-generated question.
6. Use R to reset the interview (starts a brand-new session).

## Backend startup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

This keeps the product small and reliable while matching the requested Windows-first architecture.
