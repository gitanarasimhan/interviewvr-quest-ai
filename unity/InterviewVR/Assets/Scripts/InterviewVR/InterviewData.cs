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

    // --- Dynamic AI conversation data contracts ---
    // These mirror backend/app/schemas.py: StartInterviewRequest/Response,
    // ChatRequest/Response, EndInterviewRequest/Response.

    [Serializable]
    public class StartInterviewRequest
    {
        public string role;
        public string interview_type;
    }

    [Serializable]
    public class StartInterviewResponse
    {
        public string session_id;
        public string role;
        public string interview_type;
        public string question;
        public float progress;
    }

    [Serializable]
    public class ChatRequest
    {
        public string session_id;
        public string answer;
    }

    [Serializable]
    public class ChatResponse
    {
        public string session_id;
        public int score;
        public string[] strengths;
        public string[] improvements;
        public string[] missing_information;
        public string next_question;
        public bool is_complete;
        public float progress;
    }

    [Serializable]
    public class EndInterviewRequest
    {
        public string session_id;
    }

    [Serializable]
    public class EndInterviewResponse
    {
        public string session_id;
        public string role;
        public string interview_type;
        public int total_questions;
        public float average_score;
        public string summary;
        public string[] recommendations;
    }

    /// <summary>
    /// A single exchange in the chat UI: candidate's answer and the AI's
    /// resulting feedback/next question, used to populate chat bubbles.
    /// </summary>
    [Serializable]
    public class ChatExchange
    {
        public string question;
        public string answer;
        public ChatResponse feedback;
    }
}

