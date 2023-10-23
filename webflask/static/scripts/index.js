// Tooltip
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

// Top page
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function setTargetTimes() {
  // Get the current time
  var now = new Date();

  // Get all elements with class 'countdown' and loop through them
  var countdownElements = document.querySelectorAll('[class^="countdown-"]');
  countdownElements.forEach(function (countdownElement) {
    // Extract the auction ID from the class name
    var auctionId = countdownElement.className.split('-')[1];

    // Calculate the target time for this auction (5 minutes from now)
    var targetTime = new Date(now.getTime() + 5 * 60 * 1000); // 5 minutes in milliseconds

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
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>';      }
    })
    .catch(error => {
      // Fetch error, show an error message (optional)
      document.getElementById('flash-message').innerHTML = '<div class="alert alert-danger">Error occurred while deleting the auction. \
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>';    })
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
