let sendRequest = () => {
    let api_url = 'https://short.veljkoloncarevic.in.rs/';

    let request_result = document.getElementById('request_result');
    let operation = document.getElementById('operation').value;
    let http_method = '';

    switch (operation) {
        case 'insert':
            http_method = 'POST';
            break;
        case 'update':
            http_method = 'PUT';
            break;
        case 'delete':
            http_method = 'DELETE';
            break;
    }

    let token = document.getElementById('auth_token').value;
    let short_url = document.getElementById('short_url').value;
    let url = document.getElementById('url').value;

    fetch(api_url, {
        method: http_method,
        headers: {
            "Content-Type": "application/json",
            "Authorization": token
        },
        body: JSON.stringify({
            "short_url": short_url,
            "url": url
        })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }

        return response.json().then(response => {throw new Error(response.message)});
    })
    .then(body => {
        op = (operation == 'insert') ? "inserted" : (operation == 'delete') ? "deleted" : "updated";
        request_result.textContent = 'Short URL https://short.veljkoloncarevic.in.rs/' + short_url +  ' successfully ' + op;
        request_result.style.display = 'block';
        request_result.style.backgroundColor = "var(--green)";
    })
    .catch(error => {
        request_result.textContent = error.message;
        request_result.style.opacity = 1;
        request_result.style.backgroundColor = "var(--red)";
    });
}