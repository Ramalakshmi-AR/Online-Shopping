// Function to get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

document.getElementById('rzp-button').onclick = function(e) {
    e.preventDefault();

    fetch(CREATE_ORDER_URL, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ amount: TOTAL_AMOUNT })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        const options = {
            "key": RAZORPAY_KEY,
            "amount": data.amount,
            "currency": data.currency,
            "name": "OnlineShopping",
            "description": "Order Payment",
            "order_id": data.id,
            "handler": function(response) {
                window.location.href = "/payment_success/";
            },
            "theme": { "color": "#3399cc" }
        };

        const rzp1 = new Razorpay(options);
        rzp1.open();
    })
    .catch(err => console.error("Error:", err));
};
