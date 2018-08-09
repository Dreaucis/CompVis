window.onclick = function(event) {
    if(event.target == document.getElementById('photoButton')) {
        document.getElementById('videoFeed').src = '/photo_feed';
        document.getElementById('photoButton').disabled = true;
        document.getElementById('lotteryButton').disabled = false;
        document.getElementById('redoButton').disabled = false;
        document.getElementById('audioFeed').src = 'about:blank';
    }
    if(event.target == document.getElementById('lotteryButton')) {
        document.getElementById('videoFeed').src = '/lottery_feed';
        document.getElementById('audioFeed').src = '/audio_feed';
    }
    if(event.target == document.getElementById('redoButton')) {
        document.getElementById('videoFeed').src = '/video_feed'
        document.getElementById('photoButton').disabled = false;
        document.getElementById('lotteryButton').disabled = true;
        document.getElementById('redoButton').disabled = true;
        document.getElementById('audioFeed').src = 'about:blank';
    }
}