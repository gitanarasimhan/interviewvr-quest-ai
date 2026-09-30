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

## Guiding constraints

- No multiplayer or social features.
- No authentication or payments.
- No unnecessary platform complexity.
- Keep the first version reliable and window-friendly.
