// Really basic module for SpotiStats app
// User will enter in their client ID and client secret
// into the index page. What is entered will be used
// as parameters for the API calls

// This video helped inform: https://www.youtube.com/watch?v=1vR3m0HupGI
// Need to find a better way to hold onto client_id and client_secret
// Currently uses localStorage, and I don't like that.

// constants/globals

let client_id = "";
let client_secret = "";
let redirect_uri = "https://safe-anchorage-96905.herokuapp.com/spotistats/";
let base_auth_uri = "https://accounts.spotify.com/authorize";
let token = "https://accounts.spotify.com/api/token";

function process_choices() {
    let keys = [
        'fav_song',
        'likes_count',
        'fav_artist',
        'recent_tracks',
    ];

    let selections = []
    let f_counter = 0;  // amount of false choices (unchecked)

    // build selections
    for (let idx = 0; idx < (keys.length); idx++) {
        let cur_item = document.getElementById(keys[idx]).checked;
        if (cur_item == false) {
            f_counter++;
        }
        let cur_string = keys[idx] + ' ' + cur_item;
        selections[idx] = cur_string.split(" "); // turn each of these into their own array
    }

    // users are not allowed to submit zero choices
    if (f_counter == keys.length) {
        window.alert('No selections made! Please try again.');
    } else {
        // Verify that we have a token, and it is of expected length, currently 200 chars
        // If we do, we don't have to go through the auth process again
        if (localStorage.getItem("access_token")) {
            if (localStorage.getItem("access_token").length === 200) {
                clear_output(); // clean the output box
                process_selections(selections);
            }
        } else {
            window.location.href = "auth"; // allowed to proceed to next steps
        }
    }
}

function on_page_load(){
    if (window.location.search.length > 0) {
        process_redirect();
    }
    else {
        cleanup();
    }
}

function process_redirect(){
    let code = get_code();
    get_auth_token(code);
    window.history.pushState("", "", redirect_uri); // removes the returned code from visible url
}

function get_auth_token(code){
    client_id = localStorage.getItem("client_id");
    client_secret = localStorage.getItem("client_secret");
    let params = "grant_type=authorization_code";
    params += "&code=" + code;
    params += "&redirect_uri=" + encodeURI(redirect_uri);
    params += "&client_id=" + client_id;
    params += "&client_secret=" + client_secret;
    auth_with_api(params);
}

function auth_with_api(params){
    let xhr = new XMLHttpRequest();
    xhr.open("POST", token, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('Authorization', 'Basic ' + btoa(client_id + ":" + client_secret));
    xhr.send(params)
    xhr.onload = process_auth_response;
}

function process_auth_response(){
    if ( this.status == 200 ){
        let data = JSON.parse(this.responseText);
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        on_page_load();
    }
    else {
        console.log(this.responseText);
        window.alert("HTTP Code 500: Server Error. Please refresh the page, and try again.");
    }
}

function get_code(){
    let code = null;
    let query_string = window.location.search;
    if (query_string.length > 0){
        let url_params = new URLSearchParams(query_string);
        code = url_params.get('code');
    }
    return code;
}

function cleanup(){
    localStorage.removeItem("client_id");
    localStorage.removeItem("client_secret");
}

function auth_request(){
    client_id = localStorage.getItem("client_id");
    client_secret = localStorage.getItem("client_secret");

    // what we have to do is build an API request to go out to Spotify
    // this can be done by starting with our base URI and then concatenating
    // parameters onto it

    let base_uri = base_auth_uri;
    base_uri += "?client_id=" + client_id;
    base_uri += "&response_type=code";
    base_uri += "&redirect_uri=" + encodeURI(redirect_uri)
    base_uri += "&show_dialog=true";
    base_uri += "&scope=user-read-private+user-library-read+user-read-email+user-top-read+user-read-recently-played";
    window.location.href = base_uri; // This ultimately should take you to Spotify's auth page
}
