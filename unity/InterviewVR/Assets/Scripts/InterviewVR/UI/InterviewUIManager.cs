using System;
using UnityEngine;
using UnityEngine.UI;

namespace InterviewVR.UI
{
    /// <summary>
    /// Manages the main interview flow UI: wires the <see cref="InterviewController"/>
    /// conversation events to the chat, feedback, progress, report and error
    /// sub-controllers.
    /// </summary>
    public class InterviewUIManager : MonoBehaviour
    {
        [SerializeField] private InterviewController interviewController;
        [SerializeField] private Text questionText;
        [SerializeField] private Button submitButton;
        [SerializeField] private Button resetButton;
        [SerializeField] private CanvasGroup loadingPanel;
        [SerializeField] private CanvasGroup reportPanel;
        [SerializeField] private Text errorText;

        [Header("Sub-controllers")]
        [SerializeField] private ChatUIController chatUIController;
        [SerializeField] private FeedbackDisplayController feedbackDisplayController;
        [SerializeField] private InterviewProgressController progressController;
        [SerializeField] private ReportPanel reportPanelController;

        private void Start()
        {
            if (interviewController == null)
            {
                Debug.LogError("InterviewUIManager: No InterviewController assigned.");
                return;
            }

            interviewController.OnQuestionChanged += DisplayQuestion;
            interviewController.OnAnswerSubmitted += DisplayAnswer;
            interviewController.OnFeedbackReady += DisplayFeedback;
            interviewController.OnInterviewCompleted += DisplayReport;
            interviewController.OnError += DisplayError;

            if (submitButton != null)
            {
                submitButton.onClick.AddListener(OnSubmitButtonClicked);
            }
            if (resetButton != null)
            {
                resetButton.onClick.AddListener(OnResetButtonClicked);
            }

            HideAllPanels();
            ShowLoadingPanel();
        }

        private void DisplayQuestion(string question)
        {
            if (string.IsNullOrEmpty(question))
            {
                Debug.LogWarning("DisplayQuestion: question is empty.");
                return;
            }

            HideAllPanels();

            if (questionText != null)
            {
                questionText.text = question;
            }

            chatUIController?.AddQuestionBubble(question);
            progressController?.SetProgress(interviewController.Progress);

            if (submitButton != null)
            {
                submitButton.interactable = true;
            }
        }

        private void DisplayAnswer(string answer)
        {
            chatUIController?.AddAnswerBubble(answer);
        }

        private void DisplayFeedback(ChatResponse feedback)
        {
            HideAllPanels();

            chatUIController?.AddFeedbackBubble(feedback);
            feedbackDisplayController?.DisplayFeedback(feedback);
            progressController?.SetProgress(feedback.progress);

            Debug.Log($"Feedback: Score={feedback.score}, Next question={feedback.next_question}");
        }

        private void DisplayReport(EndInterviewResponse report)
        {
            HideAllPanels();

            if (reportPanel != null)
            {
                reportPanel.alpha = 1;
                reportPanel.interactable = true;
            }

            reportPanelController?.DisplayReport(report);
            progressController?.SetProgress(1f);

            Debug.Log($"Report: Average Score={report.average_score}, Summary={report.summary}");
        }

        private void DisplayError(string message)
        {
            HideAllPanels();
            if (errorText != null)
            {
                errorText.text = $"Error: {message}";
                errorText.gameObject.SetActive(true);
            }
            Debug.LogError($"InterviewUIManager error: {message}");
        }

        private void OnSubmitButtonClicked()
        {
            if (submitButton != null)
            {
                submitButton.interactable = false;
            }
            // In a real app, this would capture microphone input.
            // For now, simulated input via KeyboardInputController.
        }

        private void OnResetButtonClicked()
        {
            chatUIController?.Clear();
            interviewController.ResetInterview();
        }

        private void HideAllPanels()
        {
            if (reportPanel != null)
            {
                reportPanel.alpha = 0;
                reportPanel.interactable = false;
            }
            if (loadingPanel != null)
            {
                loadingPanel.alpha = 0;
                loadingPanel.interactable = false;
            }
            if (errorText != null)
            {
                errorText.gameObject.SetActive(false);
            }
        }

        private void ShowLoadingPanel()
        {
            if (loadingPanel != null)
            {
                loadingPanel.alpha = 1;
                loadingPanel.interactable = true;
            }
        }

        private void OnDestroy()
        {
            if (interviewController != null)
            {
                interviewController.OnQuestionChanged -= DisplayQuestion;
                interviewController.OnAnswerSubmitted -= DisplayAnswer;
                interviewController.OnFeedbackReady -= DisplayFeedback;
                interviewController.OnInterviewCompleted -= DisplayReport;
                interviewController.OnError -= DisplayError;
            }
        }
    }
}
