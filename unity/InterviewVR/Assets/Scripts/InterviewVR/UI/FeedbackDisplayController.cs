using UnityEngine;
using UnityEngine.UI;

namespace InterviewVR.UI
{
    /// <summary>
    /// Controls visibility and population of the real-time feedback panel
    /// shown immediately after each candidate answer is evaluated.
    /// </summary>
    public class FeedbackDisplayController : MonoBehaviour
    {
        [SerializeField] private CanvasGroup feedbackCanvasGroup;
        [SerializeField] private FeedbackPanel feedbackPanel;
        [SerializeField] private Image scoreFillBar;
        [SerializeField] private float displaySeconds = 4f;

        private Coroutine hideRoutine;

        public void DisplayFeedback(ChatResponse feedback)
        {
            if (feedback == null) return;

            feedbackPanel?.DisplayFeedback(feedback);

            if (scoreFillBar != null)
            {
                scoreFillBar.fillAmount = Mathf.Clamp01(feedback.score / 100f);
            }

            Show();

            if (hideRoutine != null)
            {
                StopCoroutine(hideRoutine);
            }
            if (displaySeconds > 0f)
            {
                hideRoutine = StartCoroutine(HideAfterDelay());
            }
        }

        public void Show()
        {
            if (feedbackCanvasGroup == null) return;
            feedbackCanvasGroup.alpha = 1f;
            feedbackCanvasGroup.interactable = true;
            feedbackCanvasGroup.blocksRaycasts = true;
        }

        public void Hide()
        {
            if (feedbackCanvasGroup == null) return;
            feedbackCanvasGroup.alpha = 0f;
            feedbackCanvasGroup.interactable = false;
            feedbackCanvasGroup.blocksRaycasts = false;
        }

        private System.Collections.IEnumerator HideAfterDelay()
        {
            yield return new WaitForSeconds(displaySeconds);
            Hide();
        }
    }
}
