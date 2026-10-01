using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace InterviewVR.UI
{
    /// <summary>
    /// Manages the scrolling chat conversation view: candidate answers are
    /// rendered as bubbles on the left, AI questions/feedback on the right.
    /// </summary>
    public class ChatUIController : MonoBehaviour
    {
        [SerializeField] private RectTransform chatContent;
        [SerializeField] private GameObject candidateBubblePrefab;
        [SerializeField] private GameObject aiBubblePrefab;
        [SerializeField] private ScrollRect scrollRect;

        private readonly List<GameObject> spawnedBubbles = new List<GameObject>();

        /// <summary>Adds an AI-authored question bubble (right-aligned).</summary>
        public void AddQuestionBubble(string question)
        {
            AddBubble(aiBubblePrefab, question);
        }

        /// <summary>Adds a candidate answer bubble (left-aligned).</summary>
        public void AddAnswerBubble(string answer)
        {
            AddBubble(candidateBubblePrefab, answer);
        }

        /// <summary>Adds an AI feedback bubble summarizing score and follow-up.</summary>
        public void AddFeedbackBubble(ChatResponse feedback)
        {
            if (feedback == null) return;

            string summary = $"Score: {feedback.score}/100";
            if (feedback.strengths != null && feedback.strengths.Length > 0)
            {
                summary += $"\n+ {feedback.strengths[0]}";
            }
            if (feedback.improvements != null && feedback.improvements.Length > 0)
            {
                summary += $"\n- {feedback.improvements[0]}";
            }

            AddBubble(aiBubblePrefab, summary);
        }

        private void AddBubble(GameObject prefab, string message)
        {
            if (chatContent == null)
            {
                Debug.LogWarning("ChatUIController: chatContent is not assigned.");
                return;
            }

            GameObject bubble;
            if (prefab != null)
            {
                bubble = Instantiate(prefab, chatContent);
                var text = bubble.GetComponentInChildren<Text>();
                if (text != null)
                {
                    text.text = message;
                }
            }
            else
            {
                // Fallback: create a simple text-only bubble if no prefab is assigned.
                bubble = new GameObject("ChatBubble", typeof(RectTransform), typeof(Text));
                bubble.transform.SetParent(chatContent, false);
                var text = bubble.GetComponent<Text>();
                text.text = message;
                text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            }

            spawnedBubbles.Add(bubble);
            ScrollToBottom();
        }

        public void Clear()
        {
            foreach (var bubble in spawnedBubbles)
            {
                if (bubble != null)
                {
                    Destroy(bubble);
                }
            }
            spawnedBubbles.Clear();
        }

        private void ScrollToBottom()
        {
            if (scrollRect == null) return;
            Canvas.ForceUpdateCanvases();
            scrollRect.verticalNormalizedPosition = 0f;
        }
    }
}
