const modelSelection = document.getElementById("model-selection-wrapper");


modelSelection.addEventListener("change", event => {
    // console.log(event.target.value);
    let currentURL = window.location.href;
    var csrfToken = getCsrf("model-change-form");
    console.log(`TOKEN: ${csrfToken}`)

    const headers = new Headers({
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8',
        'X-CSRFToken': csrfToken
    });

    let data = {
        type: "model",
        selectID: event.target.value
    };

    fetch(`${currentURL}`, {
      method: "POST",
      headers,
      body: JSON.stringify(data)
    }).then(res => {
      console.log("Request complete! response:", res);
      location.reload();
    });
});