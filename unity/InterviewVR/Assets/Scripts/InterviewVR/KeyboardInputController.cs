using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace InterviewVR
{
    /// <summary>
    /// Simulates candidate speech-to-text input via keyboard, for editor
    /// testing of the dynamic AI conversation flow without a microphone.
    /// Space submits the next sample answer to the current AI-generated
    /// question; R restarts the interview session from scratch.
    /// </summary>
    public class KeyboardInputController : MonoBehaviour
    {
        [SerializeField] private InterviewController interviewController;
        [SerializeField] private KeyCode answerKey = KeyCode.Space;
        [SerializeField] private KeyCode resetKey = KeyCode.R;
        [SerializeField] private string[] sampleAnswers =
        {
            "I approached the issue by first isolating the failure mode, reviewing logs, and identifying the most likely root cause. I then created a small rollout plan so we could reduce risk while validating the fix.",
            "I started by aligning stakeholders on the goal and constraints, then I gathered user feedback and mapped it to the highest-value use cases. I worked with engineering and design to prioritize the roadmap.",
            "I focused on the root problem instead of the surface symptom. I broke the work into measurable steps, assigned owners, and used regular checkpoints to keep the team aligned. That process helped us ship faster.",
        };

        private int answerIndex;

        private void Update()
        {
            #if ENABLE_INPUT_SYSTEM
            // Using new Input System
            HandleInputSystemInput();
            #else
            // Fallback to old Input Manager
            HandleLegacyInput();
            #endif
        }

        #if ENABLE_INPUT_SYSTEM
        private void HandleInputSystemInput()
        {
            var keyboard = Keyboard.current;
            if (keyboard == null)
                return;

            if (keyboard.spaceKey.wasPressedThisFrame)
            {
                if (interviewController == null)
                {
                    Debug.LogWarning("No interview controller assigned.");
                    return;
                }

                interviewController.SubmitAnswer(sampleAnswers[answerIndex % sampleAnswers.Length]);
                answerIndex++;
            }

            if (keyboard.rKey.wasPressedThisFrame)
            {
                interviewController?.ResetInterview();
                answerIndex = 0;
            }
        }
        #endif

        private void HandleLegacyInput()
        {
            if (Input.GetKeyDown(answerKey))
            {
                if (interviewController == null)
                {
                    Debug.LogWarning("No interview controller assigned.");
                    return;
                }

                interviewController.SubmitAnswer(sampleAnswers[answerIndex % sampleAnswers.Length]);
                answerIndex++;
            }

            if (Input.GetKeyDown(resetKey))
            {
                interviewController?.ResetInterview();
                answerIndex = 0;
            }
        }
    }
}
