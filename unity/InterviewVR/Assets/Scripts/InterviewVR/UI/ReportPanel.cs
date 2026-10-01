using System;
using UnityEngine;
using UnityEngine.UI;

namespace InterviewVR.UI
{
    /// <summary>
    /// Displays the final interview report.
    /// </summary>
    public class ReportPanel : MonoBehaviour
    {
        [SerializeField] private Text averageScoreText;
        [SerializeField] private Text summaryText;
        [SerializeField] private Text recommendationsText;
        [SerializeField] private Button newInterviewButton;

        public event Action OnNewInterviewClicked;

        private void Start()
        {
            if (newInterviewButton != null)
            {
                newInterviewButton.onClick.AddListener(() => OnNewInterviewClicked?.Invoke());
            }
        }

        public void DisplayReport(EndInterviewResponse report)
        {
            if (report == null) return;

            averageScoreText.text = $"Average Score: {report.average_score}/100";
            summaryText.text = report.summary;
            recommendationsText.text = $"Recommendations:\n{string.Join("\n• ", report.recommendations)}";
        }
    }
}
