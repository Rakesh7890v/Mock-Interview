document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('start-recognition');
    const recognizedText = document.getElementById('user');
    const form = document.getElementById('chat-form');
    const messagesDiv = document.getElementById('messages');
    const loadingSpinner = document.getElementById('loading-spinner');

    const scrollToBottom = () => {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    };

    startButton.addEventListener('click', () => {
        const recognition = new webkitSpeechRecognition() || new SpeechRecognition();
        recognition.lang = 'en-IN';
        recognition.start();
        document.getElementById('listen').style.display = 'block';

        recognition.onresult = (event) => {
            const result = event.results[0][0].transcript;
            recognizedText.value = result;
        };

        recognition.onend = () => {
            document.getElementById('listen').style.display = 'none';
            console.log('Speech recognition ended.');
            form.submit(); 
        };
        scrollToBottom();
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        loadingSpinner.style.display = 'block'; 
        fetch(form.action, {
            method: 'POST',
            body: new FormData(form)
        })
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            const newMessages = doc.getElementById('messages').innerHTML;
            messagesDiv.innerHTML = newMessages;
            recognizedText.value = '';
            loadingSpinner.style.display = 'none';
            scrollToBottom();
        })
        .catch(error => {
            console.error('Error:', error);
            loadingSpinner.style.display = 'none';
        });
    });
    scrollToBottom();
});
