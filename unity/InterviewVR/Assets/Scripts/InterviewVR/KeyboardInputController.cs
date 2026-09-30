using UnityEngine;

namespace InterviewVR
{
    public class KeyboardInputController : MonoBehaviour
    {
        [SerializeField] private InterviewController interviewController;
        [SerializeField] private KeyCode recordKey = KeyCode.Space;

        private string _buffer = string.Empty;

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.A))
            {
                _buffer = "I led a project where we improved reliability by diagnosing the root cause and asking the team to reduce deployment risk. We shipped a gradual rollout and measured failures over the next week.";
            }

            if (Input.GetKeyDown(recordKey))
            {
                if (interviewController != null && !string.IsNullOrWhiteSpace(_buffer))
                {
                    interviewController.SimulateAnswer(_buffer);
                    _buffer = string.Empty;
                }
            }
        }
    }
}
