$(document).ready(function() {
    const form = document.querySelector("div#form > form");
    const button = document.querySelector(
        "div#form > form button[type='submit']");
    button.disabled = true;

    var webpush_service = null;
    (async () => {
        webpush_service = await initialize_webpush_service();
        button.disabled = false;
    })();

    form.addEventListener("submit", function(e) {
        var result = false;
        const webpush_selected = document.querySelector(
            "div#form > form input[value='webpush']");
        console.log(webpush_selected.checked);
        if (webpush_selected.checked) {
            const result = webpush_service.subscribe();
            if (result === false) {
                webpush_selected.checked = false;
            }
        } else {
            const result = webpush_service.unsubscribe();
        }
        if (result === false) {
            e.preventDefault();
        }
    });

});
