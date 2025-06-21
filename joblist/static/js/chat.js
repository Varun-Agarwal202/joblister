document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form")
    const chatMessages = document.getElementById("chat-messages")
    const userInput = document.getElementById("user-input")
    const sendButton = document.getElementById("send-button")
    const typingIndicator = document.getElementById("typing-indicator")
  
    // chatbotUrl is defined in the template
  
    function scrollToBottom() {
      chatMessages.scrollTop = chatMessages.scrollHeight
    }
  
    function showTypingIndicator() {
      typingIndicator.style.display = "block"
      scrollToBottom()
    }
  
    function hideTypingIndicator() {
      typingIndicator.style.display = "none"
    }
  
    function addMessage(content, isUser) {
      const messageDiv = document.createElement("div")
      messageDiv.classList.add("message")
      messageDiv.classList.add(isUser ? "user-message" : "ai-message")
  
      if (!isUser) {
        messageDiv.classList.add("typing")
      }
  
      messageDiv.innerHTML = content
      chatMessages.appendChild(messageDiv)
      scrollToBottom()
  
      if (!isUser) {
        simulateTyping(messageDiv)
      }
    }
  
    function simulateTyping(element) {
      const text = element.innerHTML
      element.innerHTML = ""
      let i = 0
      const interval = setInterval(() => {
        if (i < text.length) {
          element.innerHTML += text.charAt(i)
          i++
          scrollToBottom()
        } else {
          clearInterval(interval)
          element.classList.remove("typing")
        }
      }, 50)
    }
  
    // Check if chatbotUrl is defined, if not, define it with a default value
    if (typeof chatbotUrl === "undefined") {
      chatbotUrl = "/chatbot" // Or any other default URL you want to use
    }
  
    form.addEventListener("submit", (e) => {
      e.preventDefault()
      const message = userInput.value.trim()
      if (message) {
        addMessage(message, true)
        sendButton.disabled = true
        userInput.value = ""
        showTypingIndicator()
  
        fetch(chatbotUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            "X-Requested-With": "XMLHttpRequest",
          },
          body: new URLSearchParams({
            user_input: message,
          }),
        })
          .then((response) => response.json())
          .then((data) => {
            hideTypingIndicator()
            addMessage(data.response, false)
            sendButton.disabled = false
          })
          .catch((error) => {
            console.error("Error:", error)
            hideTypingIndicator()
            sendButton.disabled = false
            addMessage("Sorry, there was an error processing your request.", false)
          })
      }
    })
  
    // Initial scroll to bottom
    scrollToBottom()
  })
  
  