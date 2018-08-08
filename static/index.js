
function openAddGame() {
    document.getElementById('addGameModal').style.display = "block";
};

function openRules() {
    document.getElementById('rulesModal').style.display = "block";
};

function openAdmin() {
    document.getElementById('adminModal').style.display = "block";
};

window.onclick = function(event) {
    if(event.target == document.getElementById('rulesModal')) {
        document.getElementById('rulesModal').style.display = "none";
    }

    if(event.target == document.getElementById('adminModal')) {
        document.getElementById('adminModal').style.display = "none";
    }

    if(event.target == document.getElementById('addGameModal')) {
        document.getElementById('addGameModal').style.display = "none";
    }
};