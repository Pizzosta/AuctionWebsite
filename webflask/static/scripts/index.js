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
        document.getElementById('flash-message').innerHTML = '<div class="alert alert-success">Auction deleted successfully!</div>';
      } else if (response.status === 401) {
        // Unauthorized, show an error message (optional)
        document.getElementById('flash-message').innerHTML = '<div class="alert alert-danger">Unauthorized to delete this auction.</div>';
      } else {
        // Other error, show an error message (optional)
        document.getElementById('flash-message').innerHTML = '<div class="alert alert-danger">An error occurred while deleting the auction.</div>';      }
    })
    .catch(error => {
      // Fetch error, show an error message (optional)
      document.getElementById('flash-message').innerHTML = '<div class="alert alert-danger">Error occurred while deleting the auction.</div>';    })
}