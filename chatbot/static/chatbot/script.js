document.addEventListener('DOMContentLoaded', function() {
    const userMessageInput = document.getElementById('user-message');
    const sendButton = document.getElementById('send-button');
    const chatbox = document.getElementById('messages');
    const pdfUploadForm = document.getElementById('pdf-upload-form');

    function sendMessage() {
        const userMessage = userMessageInput.value;

        if (userMessage.trim() === '') {
            return; // Don't send empty messages
        }

        // Add user message to chatbox
        const userMessageDiv = document.createElement('div');
        userMessageDiv.className = 'message user-message';
        userMessageDiv.textContent = 'You: ' + userMessage;
        chatbox.appendChild(userMessageDiv);

        // Send user message to server
        fetch('/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ user_message: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            // Add bot response to chatbox
            const botMessageDiv = document.createElement('div');
            botMessageDiv.className = 'message bot-message';
            botMessageDiv.innerHTML = marked.parse('Bot: ' + data.response); // Convert markdown to HTML
            chatbox.appendChild(botMessageDiv);

            // Clear the input
            userMessageInput.value = '';

            // Scroll to the bottom of the chatbox
            chatbox.scrollTop = chatbox.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Send message when the Send button is clicked
    sendButton.addEventListener('click', sendMessage);

    // Send message when Enter key is pressed in the input field
    userMessageInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent the default form submission
            sendMessage();
        }
    });

    // Handle PDF upload
    pdfUploadForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission
        const formData = new FormData(pdfUploadForm);

        fetch('/process_pdf/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // Notify user of upload status
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
