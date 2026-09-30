using UnityEngine;

namespace InterviewVR
{
    public class KeyboardInputController : MonoBehaviour
    {
        [SerializeField] private InterviewController interviewController;
        [SerializeField] private KeyCode answerKey = KeyCode.Space;
        [SerializeField] private KeyCode resetKey = KeyCode.R;
        [SerializeField] private string[] sampleAnswers =
        {
            "I approached the issue by first isolating the failure mode, reviewing logs, and identifying the most likely root cause. I then created a small rollout plan so we could reduce risk while still shipping quickly. We tracked error rates and adjusted based on real-world signal.",
            "I started by aligning stakeholders on the goal and constraints, then I gathered user feedback and mapped it to the highest-value use cases. I worked with engineering and design to prioritize the roadmap and used a phased release to measure adoption before expanding further.",
            "I focused on the root problem instead of the surface symptom. I broke the work into measurable steps, assigned owners, and used regular checkpoints to keep the team aligned. That process helped us reduce risk and deliver a higher-quality outcome."
        };

        private int answerIndex;

        private void Update()
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
