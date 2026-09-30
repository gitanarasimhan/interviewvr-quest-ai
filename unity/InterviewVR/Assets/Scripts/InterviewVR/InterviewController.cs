using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

namespace InterviewVR
{
    public class InterviewController : MonoBehaviour
    {
        [SerializeField] private string apiBaseUrl = "http://localhost:8000";
        [SerializeField] private string role = "software_engineer";
        [SerializeField] private string interviewType = "behavioral";

        private readonly List<QuestionData> _questions = new List<QuestionData>();
        private int _currentQuestionIndex;

        private void Start()
        {
            StartCoroutine(FetchQuestions());
        }

        public void SimulateAnswer(string answer)
        {
            if (_currentQuestionIndex >= _questions.Count)
            {
                return;
            }

            var question = _questions[_currentQuestionIndex];
            StartCoroutine(EvaluateAnswer(question, answer));
        }

        private IEnumerator FetchQuestions()
        {
            string url = $"{apiBaseUrl}/api/interview/questions?role={role}&interview_type={interviewType}";
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                yield return request.SendWebRequest();

                if (request.result != UnityWebRequest.Result.Success)
                {
                    Debug.LogError($"Failed to fetch questions: {request.error}");
                    yield break;
                }

                var response = JsonUtility.FromJson<QuestionsResponse>($"{{\"items\":{request.downloadHandler.text}}}");
                _questions.Clear();
                _questions.AddRange(response.items);

                if (_questions.Count > 0)
                {
                    Debug.Log($"Question: {_questions[0].prompt}");
                }
            }
        }

        private IEnumerator EvaluateAnswer(QuestionData question, string transcript)
        {
            var payload = new EvaluateRequest
            {
                role = role,
                interviewType = interviewType,
                questionId = question.id,
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
                    Debug.LogError($"Evaluation failed: {request.error}");
                    yield break;
                }

                var feedback = JsonUtility.FromJson<FeedbackData>(request.downloadHandler.text);
                Debug.Log($"Score: {feedback.score}");
                Debug.Log($"Follow-up: {feedback.followUpQuestion}");

                _currentQuestionIndex++;
                if (_currentQuestionIndex < _questions.Count)
                {
                    Debug.Log($"Next question: {_questions[_currentQuestionIndex].prompt}");
                }
            }
        }

        [System.Serializable]
        private class QuestionsResponse
        {
            public QuestionData[] items;
        }

        [System.Serializable]
        private class EvaluateRequest
        {
            public string role;
            public string interviewType;
            public string questionId;
            public string transcript;
        }
    }
}
