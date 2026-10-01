import os
from typing import Optional
from datetime import datetime
import json

from app.config import get_settings

settings = get_settings()


class UsageTracker:
    """Track API usage for cost monitoring and analytics."""
    
    def __init__(self):
        self.log_file = "api_usage.jsonl"
    
    def log_request(
        self,
        endpoint: str,
        role: str,
        interview_type: str,
        transcript_length: int,
        score: Optional[int] = None,
        error: Optional[str] = None,
    ) -> None:
        """Log a single API request for tracking."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "role": role,
            "interview_type": interview_type,
            "transcript_length": transcript_length,
            "score": score,
            "error": error,
            "app_env": settings.app_env,
        }
        
        # Write to log file (for local development)
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"Warning: Could not write usage log: {e}")
        
        # In production, send to CloudWatch or DataDog
        if settings.app_env == "production":
            self._send_to_cloudwatch(event)
    
    def _send_to_cloudwatch(self, event: dict) -> None:
        """Send usage event to AWS CloudWatch (for production)."""
        try:
            import boto3
            client = boto3.client("logs")
            
            log_group = "/aws/lambda/interviewvr-api"
            log_stream = datetime.utcnow().strftime("%Y/%m/%d")
            
            # Create log stream if it doesn't exist
            try:
                client.create_log_stream(logGroupName=log_group, logStreamName=log_stream)
            except client.exceptions.ResourceAlreadyExistsException:
                pass
            
            # Put log event
            client.put_log_events(
                logGroupName=log_group,
                logStreamName=log_stream,
                logEvents=[{
                    "timestamp": int(datetime.utcnow().timestamp() * 1000),
                    "message": json.dumps(event)
                }]
            )
        except ImportError:
            print("boto3 not available, skipping CloudWatch logging")
        except Exception as e:
            print(f"Warning: Could not send to CloudWatch: {e}")


class CostMonitor:
    """Monitor and estimate API costs."""
    
    # OpenAI pricing (as of 2024)
    OPENAI_GPT4O_MINI_PRICE = {
        "input_tokens": 0.00015 / 1000,  # Per token
        "output_tokens": 0.0006 / 1000,
    }
    
    OPENAI_WHISPER_PRICE = 0.02 / 60  # Per minute of audio
    
    @staticmethod
    def estimate_evaluation_cost(transcript_length: int) -> float:
        """Estimate cost of evaluating one answer.
        
        Args:
            transcript_length: Number of words in transcript
        
        Returns:
            Estimated cost in USD
        """
        # Average: 1.3 words per token
        tokens_in = int(transcript_length / 1.3)
        tokens_out = 200  # Feedback is roughly 200 tokens
        
        cost = (
            tokens_in * CostMonitor.OPENAI_GPT4O_MINI_PRICE["input_tokens"] +
            tokens_out * CostMonitor.OPENAI_GPT4O_MINI_PRICE["output_tokens"]
        )
        return cost
    
    @staticmethod
    def estimate_transcription_cost(audio_duration_seconds: int) -> float:
        """Estimate cost of transcribing audio.
        
        Args:
            audio_duration_seconds: Duration of audio in seconds
        
        Returns:
            Estimated cost in USD
        """
        duration_minutes = audio_duration_seconds / 60
        return duration_minutes * CostMonitor.OPENAI_WHISPER_PRICE


class RateLimiter:
    """Simple in-memory rate limiter (use Redis for production)."""
    
    def __init__(self):
        self.requests = {}  # {ip: [timestamps]}
    
    def is_allowed(self, client_ip: str, window_seconds: int = 60) -> bool:
        """Check if client has exceeded rate limit."""
        current_time = datetime.utcnow().timestamp()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old timestamps outside the window
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip]
            if current_time - ts < window_seconds
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= settings.rate_limit_requests:
            return False
        
        # Add current request
        self.requests[client_ip].append(current_time)
        return True


# Global instances
usage_tracker = UsageTracker()
rate_limiter = RateLimiter()
