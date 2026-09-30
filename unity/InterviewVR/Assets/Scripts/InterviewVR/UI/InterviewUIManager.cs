using System;
using UnityEngine;
using UnityEngine.UI;

namespace InterviewVR.UI
{
    /// <summary>
    /// Manages the main interview flow UI including question display and feedback.
    /// </summary>
    public class InterviewUIManager : MonoBehaviour
    {
        [SerializeField] private InterviewController interviewController;
        [SerializeField] private Text questionText;
        [SerializeField] private Text questionCounterText;
        [SerializeField] private Button submitButton;
        [SerializeField] private Button resetButton;
        [SerializeField] private CanvasGroup feedbackPanel;
        [SerializeField] private CanvasGroup reportPanel;
        [SerializeField] private CanvasGroup loadingPanel;
        [SerializeField] private Text errorText;

        private void Start()
        {
            if (interviewController == null)
            {
                Debug.LogError("InterviewUIManager: No InterviewController assigned.");
                return;
            }

            interviewController.OnQuestionChanged += DisplayQuestion;
            interviewController.OnFeedbackReady += DisplayFeedback;
            interviewController.OnInterviewCompleted += DisplayReport;
            interviewController.OnError += DisplayError;

            submitButton.onClick.AddListener(() => OnSubmitButtonClicked());
            resetButton.onClick.AddListener(() => OnResetButtonClicked());

            HideAllPanels();
            ShowLoadingPanel();
        }

        private void DisplayQuestion(QuestionData question)
        {
            if (question == null)
            {
                Debug.LogWarning("DisplayQuestion: question is null.");
                return;
            }

            HideAllPanels();
            questionText.text = question.prompt;
            int totalQuestions = Mathf.Min(5, 5); // Simplified for MVP
            int currentQuestion = interviewController.CurrentQuestion != null ? 1 : 0;
            questionCounterText.text = $"Question {currentQuestion} of {totalQuestions}";

            submitButton.interactable = true;
        }

        private void DisplayFeedback(FeedbackData feedback)
        {
            HideAllPanels();
            feedbackPanel.alpha = 1;
            feedbackPanel.interactable = true;
            // Populate feedback UI here (score, strengths, improvements, etc.)
            Debug.Log($"Feedback: Score={feedback.score}, Follow-up={feedback.follow_up_question}");
        }

        private void DisplayReport(InterviewReportData report)
        {
            HideAllPanels();
            reportPanel.alpha = 1;
            reportPanel.interactable = true;
            // Populate report UI here (average score, summary, recommendations)
            Debug.Log($"Report: Average Score={report.average_score}, Summary={report.summary}");
        }

        private void DisplayError(string message)
        {
            HideAllPanels();
            errorText.text = $"Error: {message}";
            errorText.gameObject.SetActive(true);
        }

        private void OnSubmitButtonClicked()
        {
            submitButton.interactable = false;
            // In a real app, this would capture microphone input.
            // For now, simulated input via KeyboardInputController.
        }

        private void OnResetButtonClicked()
        {
            interviewController.ResetInterview();
        }

        private void HideAllPanels()
        {
            feedbackPanel.alpha = 0;
            feedbackPanel.interactable = false;
            reportPanel.alpha = 0;
            reportPanel.interactable = false;
            loadingPanel.alpha = 0;
            loadingPanel.interactable = false;
            errorText.gameObject.SetActive(false);
        }

        private void ShowLoadingPanel()
        {
            loadingPanel.alpha = 1;
            loadingPanel.interactable = true;
        }

        private void OnDestroy()
        {
            if (interviewController != null)
            {
                interviewController.OnQuestionChanged -= DisplayQuestion;
                interviewController.OnFeedbackReady -= DisplayFeedback;
                interviewController.OnInterviewCompleted -= DisplayReport;
                interviewController.OnError -= DisplayError;
            }
        }
    }
}
