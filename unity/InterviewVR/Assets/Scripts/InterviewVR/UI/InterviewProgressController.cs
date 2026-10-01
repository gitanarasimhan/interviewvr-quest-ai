using UnityEngine;
using UnityEngine.UI;

namespace InterviewVR.UI
{
    /// <summary>
    /// Drives a progress bar showing how far along the interview conversation is
    /// (0 = just started, 1 = interview complete).
    /// </summary>
    public class InterviewProgressController : MonoBehaviour
    {
        [SerializeField] private Image fillImage;
        [SerializeField] private Text progressLabel;
        [SerializeField] private float animationSpeed = 4f;

        private float targetProgress;

        private void Update()
        {
            if (fillImage == null) return;

            fillImage.fillAmount = Mathf.MoveTowards(
                fillImage.fillAmount,
                targetProgress,
                animationSpeed * Time.deltaTime);
        }

        /// <summary>Sets the target progress in the [0, 1] range.</summary>
        public void SetProgress(float progress)
        {
            targetProgress = Mathf.Clamp01(progress);

            if (progressLabel != null)
            {
                progressLabel.text = $"{Mathf.RoundToInt(targetProgress * 100f)}%";
            }
        }
    }
}
