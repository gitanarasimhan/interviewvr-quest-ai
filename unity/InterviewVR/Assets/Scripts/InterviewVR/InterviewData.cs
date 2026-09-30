using System;
using System.Collections.Generic;
using UnityEngine;

namespace InterviewVR
{
    [Serializable]
    public class QuestionData
    {
        public string id;
        public string role;
        public string interviewType;
        public string prompt;
    }

    [Serializable]
    public class FeedbackData
    {
        public int score;
        public List<string> strengths = new List<string>();
        public List<string> improvements = new List<string>();
        public List<string> missingInformation = new List<string>();
        public string followUpQuestion;
    }

    [Serializable]
    public class InterviewState
    {
        public string role;
        public string interviewType;
        public int currentQuestionIndex;
        public List<QuestionData> questions = new List<QuestionData>();
        public string transcript;
        public FeedbackData lastFeedback;
    }
}
