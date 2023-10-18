// Tooltip
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

// Top page
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

//Check password client side validation
function checkPasswordsMatch() {
  const password = document.getElementById("password").value;
  const confirm_password = document.getElementById("confirm_password").value;

  if (password !== confirm_password) {
    document.getElementById("flash-message").style.display = "block";
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

function placeBid() {
  // Capture the bid amount from the input field
  const bidAmount = document.getElementById('amount').value;
  const auctionId = document.getElementById('auction_id').value;

  // Send an AJAX request to place the bid
  fetch('/place_bid', {
      method: 'POST',
      body: new URLSearchParams({ auction_id: auctionId, bid_amount: bidAmount }),
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  .then(response => {
      if (response.ok) {
          if (response.status === 204) {
              // Successful bid placement without a response body
              // You can display a success message if needed
              document.getElementById('flash-message').innerHTML = '<div class="alert alert-success">Bid placed successfully.</div>';
              alert('Bid placed successfully.');
          } else {
              // Successful response with a response body
              return response.json();
          }
      } else if (response.status === 401) {
          // Unauthorized
          document.getElementById('flash-message').innerHTML = '<div class="alert alert-danger">Unauthorized to place this bid.</div>';
          throw new Error('Unauthorized');
      } else {
          // Other errors
          throw new Error('Network error');
      }
  })
  .then(data => {
      if (data.success) {
          // Update the displayed bid amount with the new bid amount
          const currentBidElement = document.getElementById('current_bid');
          currentBidElement.innerText = `$${data.new_bid_amount}`;
      } else {
          // Handle other success cases if needed
          document.getElementById('flash-message').innerHTML = '<div class="alert alert-success">Bid amount must be equal to or greater than the starting bid.</div>';
          alert('Bid not placed: ' + data.error);
      }
  })
  .catch(error => {
      // Handle other errors
      console.error('Error:', error);
  });
}
