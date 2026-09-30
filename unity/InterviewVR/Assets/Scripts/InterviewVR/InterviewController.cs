using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

namespace InterviewVR
{
    public class InterviewController : MonoBehaviour
    {
        [Header("Interview Configuration")]
        [SerializeField] private string apiBaseUrl = "http://localhost:8000";
        [SerializeField] private string role = "software_engineer";
        [SerializeField] private string interview_type = "behavioral";
        [SerializeField] private int maxQuestions = 5;

        [Header("Runtime State")]
        [SerializeField] private List<QuestionData> questions = new List<QuestionData>();
        [SerializeField] private int currentQuestionIndex;
        [SerializeField] private List<int> scores = new List<int>();

        public bool IsReady { get; private set; }
        public bool IsProcessing { get; private set; }
        public QuestionData CurrentQuestion => currentQuestionIndex < questions.Count ? questions[currentQuestionIndex] : null;
        public float Progress => questions.Count > 0 ? (float)currentQuestionIndex / Mathf.Min(questions.Count, maxQuestions) : 0f;

        public event Action<QuestionData> OnQuestionChanged;
        public event Action<FeedbackData> OnFeedbackReady;
        public event Action<InterviewReportData> OnInterviewCompleted;
        public event Action<string> OnError;

        private void Start()
        {
            StartCoroutine(LoadQuestions());
        }

        public void SubmitAnswer(string transcript)
        {
            if (!IsReady || IsProcessing)
            {
                Debug.LogWarning("Controller is not ready or is currently processing.");
                return;
            }

            if (string.IsNullOrWhiteSpace(transcript))
            {
                OnError?.Invoke("Cannot submit a blank transcript.");
                return;
            }

            if (CurrentQuestion == null)
            {
                OnError?.Invoke("No current question is available.");
                return;
            }

            StartCoroutine(EvaluateCurrentAnswer(transcript));
        }

        public void ResetInterview()
        {
            currentQuestionIndex = 0;
            scores.Clear();
            IsProcessing = false;
            StartCoroutine(LoadQuestions());
        }

        private IEnumerator LoadQuestions()
        {
            IsProcessing = true;
            string url = $"{apiBaseUrl}/api/interview/questions?role={role}&interview_type={interview_type}";
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                yield return request.SendWebRequest();

                if (request.result != UnityWebRequest.Result.Success)
                {
                    string error = $"Failed to load questions: {request.error}";
                    OnError?.Invoke(error);
                    Debug.LogError(error);
                    IsReady = false;
                    IsProcessing = false;
                    yield break;
                }

                var response = JsonUtility.FromJson<QuestionsResponse>($"{{\"items\":{request.downloadHandler.text}}}");
                questions.Clear();

                if (response == null || response.items == null || response.items.Length == 0)
                {
                    string error = "No questions returned from backend.";
                    OnError?.Invoke(error);
                    Debug.LogError(error);
                    IsReady = false;
                    IsProcessing = false;
                    yield break;
                }

                foreach (var item in response.items)
                {
                    questions.Add(item);
                }

                currentQuestionIndex = 0;
                IsReady = true;
                IsProcessing = false;
                Debug.Log($"Loaded {questions.Count} questions.");
                OnQuestionChanged?.Invoke(CurrentQuestion);
            }
        }

        private IEnumerator EvaluateCurrentAnswer(string transcript)
        {
            IsProcessing = true;
            var question = CurrentQuestion;
            var payload = new EvaluateRequest
            {
                role = role,
                interview_type = interview_type,
                question_id = question.id,
                transcript = transcript
            };

            string json = JsonUtility.ToJson(payload);
            using (UnityWebRequest request = new UnityWebRequest($"{apiBaseUrl}/api/interview/evaluate", "POST"))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");

                yield return request.SendWebRequest();

                if (request.result != UnityWebRequest.Result.Success)
                {
                    string error = $"Evaluation failed: {request.error}";
                    OnError?.Invoke(error);
                    Debug.LogError(error);
                    IsProcessing = false;
                    yield break;
                }

                var feedback = JsonUtility.FromJson<FeedbackData>(request.downloadHandler.text);
                scores.Add(feedback.score);
                OnFeedbackReady?.Invoke(feedback);

                Debug.Log($"Score: {feedback.score}");
                Debug.Log($"Follow-up: {feedback.follow_up_question}");

                currentQuestionIndex++;

                if (currentQuestionIndex >= Mathf.Min(questions.Count, maxQuestions))
                {
                    StartCoroutine(GenerateFinalReport());
                    yield break;
                }

                IsProcessing = false;
                OnQuestionChanged?.Invoke(CurrentQuestion);
            }
        }

        private IEnumerator GenerateFinalReport()
        {
            var reportPayload = new ReportRequest
            {
                role = role,
                interview_type = interview_type,
                scores = scores.ToArray()
            };

            string payloadJson = JsonUtility.ToJson(reportPayload);
            using (UnityWebRequest request = new UnityWebRequest($"{apiBaseUrl}/api/interview/report", "POST"))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(payloadJson);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");

                yield return request.SendWebRequest();

                if (request.result != UnityWebRequest.Result.Success)
                {
                    string error = $"Report generation failed: {request.error}";
                    OnError?.Invoke(error);
                    Debug.LogError(error);
                    IsProcessing = false;
                    yield break;
                }

                var report = JsonUtility.FromJson<InterviewReportData>(request.downloadHandler.text);
                OnInterviewCompleted?.Invoke(report);
                Debug.Log($"Interview report average: {report.average_score}");
                Debug.Log(report.summary);
                IsProcessing = false;
            }
        }

        [Serializable]
        private class QuestionsResponse
        {
            public QuestionData[] items;
        }

        [Serializable]
        private class EvaluateRequest
        {
            public string role;
            public string interview_type;
            public string question_id;
            public string transcript;
        }

        [Serializable]
        private class ReportRequest
        {
            public string role;
            public string interview_type;
            public int[] scores;
        }
    }
}
