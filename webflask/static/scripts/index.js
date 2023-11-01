// Tooltip
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

// Top page
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}


// Image Thumbnail
var imageInput = document.getElementById('image');
var preview = document.getElementById('image-preview');
var clearButton = document.getElementById('clear-thumbnails');

imageInput.addEventListener('change', function () {
  preview.innerHTML = ''; // Clear previous previews
  var files = this.files;

  for (var i = 0; i < files.length; i++) {
    var file = files[i];
    if (file.type.startsWith('image/')) {
      var reader = new FileReader();
      reader.onload = function (e) {
        var img = document.createElement('img');
        img.src = e.target.result;
        img.classList.add('preview-thumbnail');
        preview.appendChild(img);
      };
      reader.readAsDataURL(file);
    }
  }
});

clearButton.addEventListener('click', function () {
  imageInput.value = null; // Clear the file input
  preview.innerHTML = ''; // Clear the previews
});


// Delete Auction
function deleteAuction(auctionId) {
  fetch(`/delete-auction/${auctionId}`, {
    method: 'POST',
    credentials: 'same-origin',
  })
    .then(response => {
      if (response.status === 204) {
        // Successful deletion, remove the row from the table
        const row = document.getElementById(`auction-row-${auctionId}`);
        if (row) {
          row.parentNode.removeChild(row);
        }
        // Display success flash message (you can adjust this part to fit your HTML structure)
        document.getElementById('flash-message').innerHTML = '<div class="alert alert-success">Auction deleted successfully! \
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>';
      } else if (response.status === 401) {
        // Unauthorized, show an error message (optional)
        document.getElementById('flash-message').innerHTML = '<div class="alert alert-danger">Unauthorized to delete this auction. \
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>';
      } else {
        // Other error, show an error message (optional)
        document.getElementById('flash-message').innerHTML = '<div class="alert alert-danger">An error occurred while deleting the auction. \
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>';
      }
    })
    .catch(error => {
      // Fetch error, show an error message (optional)
      document.getElementById('flash-message').innerHTML = '<div class="alert alert-danger">Error occurred while deleting the auction. \
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>';
    })
}

//Check password client side validation
function checkPasswordsMatch() {
  const password = document.getElementById("password").value;
  const confirm_password = document.getElementById("confirm_password").value;

  if (password !== confirm_password) {
    document.getElementById("flash-message").innerHTML = '<div class="alert alert-danger alert-dismissible fade show">Passwords dont match. \
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>';
    return false;
  } else {
    document.getElementById("flash-message").style.display = "none";
    return true;
  }
}

function validateForm() {
  // Additional client-side validation checks can be added here.
  return checkPasswordsMatch();
}


/**(function () {
  // Convert the end time from your database format to a JavaScript Date object
  var endTime = new Date("{{ auction.end_time }}");

  var x = setInterval(function () {
      var now = new Date().getTime();
      var distance = endTime - now;

      // Calculate days, hours, minutes, and seconds
      var days = Math.floor(distance / (1000 * 60 * 60 * 24));
      var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      var seconds = Math.floor((distance % (1000 * 60)) / 1000);

      // Display the countdown
      var countdownElem = document.getElementById("countdown-{{ auction.id }}");
      countdownElem.innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s ";

      // If the countdown is over, display a message
      if (distance < 0) {
          clearInterval(x);
          countdownElem.innerHTML = "EXPIRED";
          var bidButton = document.querySelector("#bid-button-{{ auction.id }}");
          var bidInput = document.querySelector("#amount-{{ auction.id }}");
          bidButton.disabled = true;
          bidInput.disabled = true;
      }
  }, 1000);

})();
*/

// Wrap your code in a function to ensure it runs after the DOM is fully loaded.
document.addEventListener("DOMContentLoaded", function () {
  // Find all elements needed for the countdown and bid button handling.
  const auctionId = "{{ auction.id }}";
  const countdownElem = document.getElementById("countdown-" + auctionId);
  const bidButton = document.getElementById("bid-button-" + auctionId);
  const bidInput = document.getElementById("amount-" + auctionId);

  // Function to update the countdown timer.
  function updateCountdown(endTime) {
    const now = new Date().getTime();
    const distance = endTime - now;

    // Calculate days, hours, minutes, and seconds
    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

    // Display the countdown
    countdownElem.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;

    // If the countdown is over, display a message
    if (distance < 0) {
      clearInterval(countdownInterval);
      countdownElem.innerHTML = "EXPIRED";
      bidButton.disabled = true;
      bidInput.disabled = true;
    }
  }

  // Function to start the countdown.
  function startCountdown() {
    const endTime = new Date("{{ auction.end_time }}").getTime();
    updateCountdown(endTime);
    // Update the countdown every second.
    const countdownInterval = setInterval(function () {
      updateCountdown(endTime);
    }, 1000);
  }

  // Call the startCountdown function to begin the countdown.
  startCountdown();
});
