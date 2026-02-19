console.log("script.js loaded successfully");

// ---------- TEXT TO SPEECH ----------
function speakText(text) {
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = "en-US";
    speech.rate = 1;
    speech.pitch = 1;
    window.speechSynthesis.speak(speech);
}

document.getElementById("hearBtn")?.addEventListener("click", function () {
    speakText(chapterText);
});

// ---------- SPEECH TO TEXT ----------
let recognition;
try {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
} catch {
    recognition = null;
    console.log("Speech recognition not supported.");
}

if (recognition) {
    recognition.lang = "en-US";
    recognition.interimResults = false;

    recognition.onresult = function (event) {
        const userSpeech = event.results[0][0].transcript.toLowerCase();
        console.log("You said:", userSpeech);

        const chapterLower = chapterText.toLowerCase();

        // accuracy calculation
        let matchCount = 0;
        userSpeech.split(" ").forEach(word => {
            if (chapterLower.includes(word)) {
                matchCount++;
            }
        });

        const accuracy = Math.round((matchCount / userSpeech.split(" ").length) * 100);
        document.getElementById("accuracyBox").innerText = 
            `Your speaking accuracy: ${accuracy}%`;
    };

    recognition.onerror = function (e) {
        console.log("Error:", e.error);
    };
}

document.getElementById("speakBtn")?.addEventListener("click", function () {
    if (recognition) {
        recognition.start();
    } else {
        alert("Speech Recognition is not supported on this browser.");
    }
});
