using System;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace InterviewVR.Network
{
    /// <summary>
    /// Secure API client for Quest app that signs requests with HMAC.
    /// This prevents unauthorized access to the backend from spoofed clients.
    /// </summary>
    public class SecureAPIClient
    {
        private readonly string apiBaseUrl;
        private readonly string appSecret;

        public SecureAPIClient(string baseUrl, string secret)
        {
            apiBaseUrl = baseUrl;
            appSecret = secret;
        }

        /// <summary>
        /// Generate HMAC-SHA256 signature over "{timestamp}.{body}".
        /// Including the timestamp in the signed message prevents replay
        /// attacks and must match the backend's `RequestSigner` implementation
        /// (see `backend/app/auth.py`).
        /// </summary>
        private string GenerateSignature(string body, string timestamp)
        {
            string message = $"{timestamp}.{body}";
            using (var hmac = new HMACSHA256(Encoding.UTF8.GetBytes(appSecret)))
            {
                byte[] hash = hmac.ComputeHash(Encoding.UTF8.GetBytes(message));
                // Convert to hex string (must match Python's hexdigest())
                StringBuilder sb = new StringBuilder();
                foreach (byte b in hash)
                {
                    sb.Append(b.ToString("x2"));
                }
                return sb.ToString();
            }
        }

        public void SendSignedRequest(
            string endpoint,
            string method,
            string jsonBody,
            System.Action<string> onSuccess,
            System.Action<string> onError)
        {
            string timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds().ToString();
            string signature = GenerateSignature(jsonBody, timestamp);
            Debug.Log($"[SecureAPIClient] Generated signature: {signature.Substring(0, 8)}...");

            string url = $"{apiBaseUrl}{endpoint}";
            byte[] bodyRaw = Encoding.UTF8.GetBytes(jsonBody);

            using (UnityWebRequest request = new UnityWebRequest(url, method))
            {
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                request.SetRequestHeader("X-Signature", signature);
                request.SetRequestHeader("X-Timestamp", timestamp);

                // Send asynchronously
                var asyncOp = request.SendWebRequest();
                asyncOp.completed += (op) =>
                {
                    if (request.result != UnityWebRequest.Result.Success)
                    {
                        string error = $"{request.error} ({request.responseCode})";
                        Debug.LogError($"[SecureAPIClient] Request failed: {error}");
                        onError?.Invoke(error);
                    }
                    else
                    {
                        Debug.Log($"[SecureAPIClient] Request succeeded");
                        onSuccess?.Invoke(request.downloadHandler.text);
                    }
                    request.Dispose();
                };
            }
        }
    }
}
