var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Set the target date and time (5 minutes from now)
var targetDate = new Date();
targetDate.setMinutes(targetDate.getMinutes() + 5);

function updateTimer() {
  var now = new Date();
  var timeLeft = targetDate - now;

  if (timeLeft <= 0) {
    document.getElementById('countdown').innerHTML = "Auction Ended";
  } else {
    var minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
    document.getElementById('countdown').innerHTML = ("0" + minutes).slice(-2) + ":" + ("0" + seconds).slice(-2);
  }
}

setInterval(updateTimer, 1000);