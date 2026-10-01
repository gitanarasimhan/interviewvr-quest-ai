# InterviewVR AI architecture plan

## Phase 1: MVP foundation

- Create a small Python API that serves interview questions and evaluation responses.
- Build a Unity client with a simple interview scene and a simulated input controller.
- Keep the business logic shared across both client types.

## Phase 2: Interview flow

- Add question selection based on job role and interview type.
- Add transcript capture workflow using a speech-to-text abstraction.
- Add AI evaluation service with a structured response model.

## Phase 3: UX improvements

- Add final report screen with score summary.
- Add question-by-question feedback cards.
- Add keyboard/mouse simulation support for editor testing.

## Phase 4: Quest integration

- Add a Quest-specific input adapter.
- Keep the same interview logic and AI evaluation pipeline.
- Ensure the Unity editor still works with simulated input.

## Phase 5: Dynamic AI conversation

- Replace the static question bank with a GPT-generated, stateful
  conversation: `app/conversation_service.py` owns session state
  (questions asked, answers, feedback, running scores) and prompts GPT for
  both the opening question and each dynamic follow-up.
- Expose the conversation over `/api/interview/start`, `/api/interview/chat`,
  and `/api/interview/end`, replacing the old `/api/interview/questions`
  endpoint.
- Add HMAC-SHA256 request signing (`app/auth.py`) with a timestamp in the
  signed payload to prevent replay attacks; enforced only when
  `REQUIRE_SIGNATURE=true`.
- Add `lambda_handler.py` so the same FastAPI app can run on AWS Lambda
  behind API Gateway via Mangum, in addition to local `uvicorn`.
- Update the Unity client to a chat-bubble conversation UI
  (`ChatUIController`, `FeedbackDisplayController`,
  `InterviewProgressController`) instead of a single-question-at-a-time view.

## Guiding constraints

- No multiplayer or social features.
- No authentication or payments.
- No unnecessary platform complexity.
- Keep the first version reliable and window-friendly.
