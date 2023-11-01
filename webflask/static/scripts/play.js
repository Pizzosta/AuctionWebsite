function setTargetTimes() {
  
  // Get all elements with class 'countdown' and loop through them
  var countdownElements = document.querySelectorAll('[class^="countdown-"]');
  countdownElements.forEach(function (countdownElement) {
    // Extract the auction ID from the class name
    var auctionId = countdownElement.className.split('-')[1];

   // Fetch the target times for this auction
    var targetTimeString = countdownElement.getAttribute('data-target');

    // Parse the target time string to create a JavaScript Date object
    var targetTime = new Date(targetTimeString);

    // Set the 'target' attribute with the target time for this auction
    countdownElement.setAttribute('data-target', targetTime);
  });
}

// Call this function once when the page loads to set the target times
setTargetTimes();

function updateTimers() {
  var now = new Date();

  // Get all elements with class 'countdown' and loop through them
  var countdownElements = document.querySelectorAll('[class^="countdown-"]');
  countdownElements.forEach(function (countdownElement) {
    var targetTime = new Date(countdownElement.getAttribute('data-target'));
    var timeLeft = targetTime - now;

    if (timeLeft <= 0) {
      countdownElement.innerHTML = "Auction Ended";
    } else {
      var minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
      var seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
      countdownElement.innerHTML = ("0" + minutes).slice(-2) + ":" + ("0" + seconds).slice(-2);
    }
  });
}

setInterval(updateTimers, 1000);
