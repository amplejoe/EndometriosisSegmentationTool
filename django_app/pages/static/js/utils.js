function getCsrf(parentID) {
    var inputElems = document.querySelectorAll(`#${parentID} input`);
    var csrfToken = '';
    for (i = 0; i < inputElems.length; ++i) {
        if (inputElems[i].name === 'csrfmiddlewaretoken') {
            csrfToken = inputElems[i].value;
            break;
        }
    }
    return csrfToken;
};