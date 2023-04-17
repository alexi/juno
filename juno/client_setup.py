from IPython.display import Javascript, display
from .juno import hack

HANDLE_USER_AUTH = """
// Helper function to get the value of a cookie by name
function getCookieValue(name) {
  const cookies = document.cookie.split("; ");
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i];
    const [cookieName, cookieValue] = cookie.split("=");
    if (cookieName === name) {
      return cookieValue;
    }
  }
  return null;
}

// Helper function to generate a unique visitor ID
function generateUniqueVisitorId() {
  // Use a cryptographically secure random number generator to generate a random 128-bit hash value
  const array = new Uint8Array(16);
  window.crypto.getRandomValues(array);
  const hash = Array.from(array).map(b => b.toString(16).padStart(2, '0')).join('');

  // Append the current timestamp to the hash value to make it even more unique
  return hash + Date.now().toString();
}

const existingVisitorId = localStorage.getItem("visitor_id");

if (!existingVisitorId) {
  // Generate a unique visitor ID
  const visitorId = generateUniqueVisitorId();

  // Store the visitorId in localStorage
  localStorage.setItem("visitor_id", visitorId);
}
"""

def setup():
    display(Javascript(HANDLE_USER_AUTH))
    hack()