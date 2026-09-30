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
        public string interview_type;
        public string prompt;
    }

    [Serializable]
    public class FeedbackData
    {
        public int score;
        public string[] strengths;
        public string[] improvements;
        public string[] missing_information;
        public string follow_up_question;
    }

    [Serializable]
    public class InterviewReportData
    {
        public string role;
        public string interview_type;
        public int total_questions;
        public float average_score;
        public string summary;
        public string[] recommendations;
    }

    [Serializable]
    public class InterviewState
    {
        public string role;
        public string interview_type;
        public int currentQuestionIndex;
        public List<QuestionData> questions = new List<QuestionData>();
        public string transcript;
        public FeedbackData lastFeedback;
    }
}
