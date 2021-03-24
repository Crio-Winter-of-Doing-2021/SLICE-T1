// The Browser API key obtained from the Google API Console.
// Replace with your own Browser API key, or your own key.
var developerKey = 'AIzaSyAYpOSff8PJxjUYLMjnuFkTXhAJPnWzBsw';
// The Client ID obtained from the Google API Console. Replace with your own Client ID.
var clientId = "371503442644-facskhpl8njmi4luslkqb52ketq8kfvq.apps.googleusercontent.com"
var clientSecret = "0C6TCd2sMEu6ctj75IOxL8tw"
// Replace with your own project number from console.developers.google.com.
// See "Project number" under "IAM & Admin" > "Settings"
var appId = "371503442644";
// Scope to use to access user's Drive items.
var scope = ['https://www.googleapis.com/auth/drive.file'];
var pickerApiLoaded = false;
var oauthToken;
var origAuthToken;
var creds_needed;
// Use the Google API Loader script to load the google.picker script.

function loadPicker() {
    gapi.load('auth', {'callback': onAuthApiLoad});
    gapi.load('picker', {'callback': onPickerApiLoad});
}
function onAuthApiLoad() {
    window.gapi.auth.authorize(
        {
        'client_id': clientId,
        'scope': scope,
        'immediate': false,
        'response_type': 'id_token permission code'
        },
        handleAuthResult);
}
function onPickerApiLoad() {
    pickerApiLoaded = true;
    createPicker();
}
function handleAuthResult(authResult) {
    if (authResult && !authResult.error) {
    oauthToken = authResult.access_token;
    origAuthToken = authResult.code;
    console.log(oauthToken);
    console.log(authResult.code);
    console.log(authResult.id_token);
    creds_needed = {
        "token": authResult.access_token,
        "refresh_token": authResult.code,
        "client_id": clientId,
        "client_secret": clientSecret,
        "scopes": scope
    };
    createPicker();
    }
}
// Create and render a Picker object for searching images.
function createPicker() {
    if (pickerApiLoaded && oauthToken) {
    var view = new google.picker.View(google.picker.ViewId.DOCS);
    view.setMimeTypes("image/png,image/jpeg,image/jpg,application/pdf");
    var picker = new google.picker.PickerBuilder()
        .enableFeature(google.picker.Feature.NAV_HIDDEN)
        .enableFeature(google.picker.Feature.MULTISELECT_ENABLED)
        .setAppId(appId)
        .setOAuthToken(oauthToken)
        .addView(view)
        .addView(new google.picker.DocsUploadView())
        .setDeveloperKey(developerKey)
        .setCallback(pickerCallback)
        .build();
        picker.setVisible(true);
    }
}
function csrfcookie(name){
    var cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};
// A simple callback implementation.


function pickerCallback(data) {
    if (data.action == google.picker.Action.PICKED) {
        var array = [];
        for(let i=0;i<data.docs.length;i++){
            var obj={};
            obj['file_id']=(data.docs[i].id);
            obj['name']=(data.docs[i].name);
            obj['size']=(data.docs[i].sizeBytes);
            obj['url']=(data.docs[i].url);
            array.push(obj);
            //console.log(data.docs[i]);
        }
        var csrftoken = csrfcookie('csrftoken');

        fetch("google_api",{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(array),
        }).then(function(response){
          console.log("response successfull");
          location.href="/files_display";
        })
    }
}
