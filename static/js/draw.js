const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

ctx.fillStyle = "white";
ctx.fillRect(0, 0, canvas.width, canvas.height);

let drawing = false;

canvas.addEventListener("mousedown", () => drawing = true);
canvas.addEventListener("mouseup", () => drawing = false);
canvas.addEventListener("mouseleave", () => drawing = false);

canvas.addEventListener("mousemove", draw);

function draw(e) {
    if (!drawing) return;

    ctx.fillStyle = "black";
    ctx.beginPath();
    ctx.arc(e.offsetX, e.offsetY, 4, 0, Math.PI * 2);
    ctx.fill();
}

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function sendCanvas() {
    const dataURL = canvas.toDataURL("image/png");

    fetch("/predict-canvas", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataURL })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("expression").innerText = data.expression;
        document.getElementById("result").innerText = data.result;
    });
}

/* 🔴 THIS FUNCTION WAS MISSING */
function uploadImage() {
    const input = document.getElementById("uploadInput");
    const file = input.files[0];

    if (!file) {
        alert("Please choose an image first");
        return;
    }

    const formData = new FormData();
    formData.append("image", file);

    fetch("/predict-upload", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("expression").innerText = data.expression;
        document.getElementById("result").innerText = data.result;
    });
}
