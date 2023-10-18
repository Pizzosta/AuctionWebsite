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
