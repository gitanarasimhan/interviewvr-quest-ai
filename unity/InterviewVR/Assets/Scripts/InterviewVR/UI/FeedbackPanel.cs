using System;
using UnityEngine;
using UnityEngine.UI;

namespace InterviewVR.UI
{
    /// <summary>
    /// Displays feedback for a single answer.
    /// </summary>
    public class FeedbackPanel : MonoBehaviour
    {
        [SerializeField] private Text scoreText;
        [SerializeField] private Text strengthsText;
        [SerializeField] private Text improvementsText;
        [SerializeField] private Text missingInfoText;
        [SerializeField] private Text followUpText;
        [SerializeField] private Button nextButton;

        public event Action OnNextClicked;

        private void Start()
        {
            if (nextButton != null)
            {
                nextButton.onClick.AddListener(() => OnNextClicked?.Invoke());
            }
        }

        public void DisplayFeedback(ChatResponse feedback)
        {
            if (feedback == null) return;

            scoreText.text = $"Score: {feedback.score}/100";
            strengthsText.text = $"Strengths:\n{string.Join("\n• ", feedback.strengths)}";
            improvementsText.text = $"Areas to Improve:\n{string.Join("\n• ", feedback.improvements)}";
            missingInfoText.text = $"Missing Information:\n{string.Join("\n• ", feedback.missing_information)}";
            followUpText.text = string.IsNullOrEmpty(feedback.next_question)
                ? "Follow-up Question:\n(Interview complete)"
                : $"Follow-up Question:\n{feedback.next_question}";
        }
    }
}
