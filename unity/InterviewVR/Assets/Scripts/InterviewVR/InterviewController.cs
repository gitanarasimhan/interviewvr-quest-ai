using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

namespace InterviewVR
{
    /// <summary>
    /// Drives the dynamic AI interview conversation flow:
    ///   1. Start a session (POST /api/interview/start)
    ///   2. Submit candidate answers and receive AI feedback + follow-up
    ///      questions (POST /api/interview/chat), repeating until complete
    ///   3. End the session and display the final report (POST /api/interview/end)
    /// </summary>
    public class InterviewController : MonoBehaviour
    {
        [Header("Interview Configuration")]
        [SerializeField] private string apiBaseUrl = "http://localhost:8000";
        [SerializeField] private string role = "software_engineer";
        [SerializeField] private string interview_type = "behavioral";

        [Header("Security")]
        [Tooltip("Shared secret used to HMAC-sign requests. Must match the backend's QUEST_APP_SECRET.")]
        [SerializeField] private string appSecret = "";
        [Tooltip("When true, requests are signed with X-Signature/X-Timestamp headers.")]
        [SerializeField] private bool useSignedRequests = false;

        [Header("Runtime State")]
        [SerializeField] private string sessionId;
        [SerializeField] private string currentQuestion;
        [SerializeField] private float progress;
        [SerializeField] private List<int> scores = new List<int>();

        public bool IsReady { get; private set; }
        public bool IsProcessing { get; private set; }
        public string SessionId => sessionId;
        public string CurrentQuestion => currentQuestion;
        public float Progress => progress;

        public event Action<string> OnQuestionChanged;
        public event Action<string> OnAnswerSubmitted;
        public event Action<ChatResponse> OnFeedbackReady;
        public event Action<EndInterviewResponse> OnInterviewCompleted;
        public event Action<string> OnError;

        private Network.SecureAPIClient secureClient;

        private void Awake()
        {
            secureClient = new Network.SecureAPIClient(apiBaseUrl, appSecret);
        }

        private void Start()
        {
            StartCoroutine(StartInterview());
        }

        public void SubmitAnswer(string answer)
        {
            if (!IsReady || IsProcessing)
            {
                Debug.LogWarning("Controller is not ready or is currently processing.");
                return;
            }

            if (string.IsNullOrWhiteSpace(answer))
            {
                OnError?.Invoke("Cannot submit a blank answer.");
                return;
            }

            if (string.IsNullOrEmpty(sessionId))
            {
                OnError?.Invoke("No active interview session.");
                return;
            }

            OnAnswerSubmitted?.Invoke(answer);
            StartCoroutine(SendAnswer(answer));
        }

        public void ResetInterview()
        {
            sessionId = null;
            currentQuestion = null;
            progress = 0f;
            scores.Clear();
            IsReady = false;
            IsProcessing = false;
            StartCoroutine(StartInterview());
        }

        private IEnumerator StartInterview()
        {
            IsReady = false;
            IsProcessing = true;

            var payload = new StartInterviewRequest { role = role, interview_type = interview_type };
            string json = JsonUtility.ToJson(payload);

            yield return SendRequest<StartInterviewResponse>(
                "/api/interview/start",
                json,
                onSuccess: response =>
                {
                    sessionId = response.session_id;
                    currentQuestion = response.question;
                    progress = response.progress;
                    IsReady = true;
                    IsProcessing = false;
                    Debug.Log($"Interview started. Session: {sessionId}");
                    OnQuestionChanged?.Invoke(currentQuestion);
                },
                onError: error =>
                {
                    IsReady = false;
                    IsProcessing = false;
                    OnError?.Invoke($"Failed to start interview: {error}");
                });
        }

        private IEnumerator SendAnswer(string answer)
        {
            IsProcessing = true;

            var payload = new ChatRequest { session_id = sessionId, answer = answer };
            string json = JsonUtility.ToJson(payload);

            yield return SendRequest<ChatResponse>(
                "/api/interview/chat",
                json,
                onSuccess: response =>
                {
                    scores.Add(response.score);
                    OnFeedbackReady?.Invoke(response);
                    progress = response.progress;

                    Debug.Log($"Score: {response.score}");

                    if (response.is_complete || string.IsNullOrEmpty(response.next_question))
                    {
                        StartCoroutine(EndInterview());
                        return;
                    }

                    currentQuestion = response.next_question;
                    IsProcessing = false;
                    OnQuestionChanged?.Invoke(currentQuestion);
                },
                onError: error =>
                {
                    IsProcessing = false;
                    OnError?.Invoke($"Chat request failed: {error}");
                });
        }

        private IEnumerator EndInterview()
        {
            var payload = new EndInterviewRequest { session_id = sessionId };
            string json = JsonUtility.ToJson(payload);

            yield return SendRequest<EndInterviewResponse>(
                "/api/interview/end",
                json,
                onSuccess: report =>
                {
                    IsReady = false;
                    IsProcessing = false;
                    OnInterviewCompleted?.Invoke(report);
                    Debug.Log($"Interview report average: {report.average_score}");
                    Debug.Log(report.summary);
                },
                onError: error =>
                {
                    IsProcessing = false;
                    OnError?.Invoke($"Failed to generate report: {error}");
                });
        }

        /// <summary>
        /// Sends a JSON POST request, optionally HMAC-signed, and parses the
        /// JSON response into <typeparamref name="T"/>.
        /// </summary>
        private IEnumerator SendRequest<T>(string endpoint, string json, Action<T> onSuccess, Action<string> onError)
        {
            if (useSignedRequests && !string.IsNullOrEmpty(appSecret))
            {
                bool completed = false;
                string resultText = null;
                string errorText = null;

                secureClient.SendSignedRequest(
                    endpoint,
                    "POST",
                    json,
                    success =>
                    {
                        resultText = success;
                        completed = true;
                    },
                    error =>
                    {
                        errorText = error;
                        completed = true;
                    });

                yield return new WaitUntil(() => completed);

                if (errorText != null)
                {
                    onError?.Invoke(errorText);
                    yield break;
                }

                T parsed = JsonUtility.FromJson<T>(resultText);
                onSuccess?.Invoke(parsed);
                yield break;
            }

            using (UnityWebRequest request = new UnityWebRequest($"{apiBaseUrl}{endpoint}", "POST"))
            {
                byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");

                yield return request.SendWebRequest();

                if (request.result != UnityWebRequest.Result.Success)
                {
                    onError?.Invoke($"{request.error} ({request.responseCode})");
                    yield break;
                }

                T parsed = JsonUtility.FromJson<T>(request.downloadHandler.text);
                onSuccess?.Invoke(parsed);
            }
        }
    }
}
