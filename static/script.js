document.addEventListener("DOMContentLoaded", () => {
  console.log("FairLens frontend loaded.");
});
function sendQuestion() {
  const question = document.getElementById("question").value;

  if (!question) return;

  document.getElementById("chatResponse").innerText = "Thinking...";

  fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ question })
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("chatResponse").innerText = data.reply;
    })
    .catch(() => {
      document.getElementById("chatResponse").innerText = "Error contacting server";
    });
}