// Here is where the different operations for gathering data from Spotify will be organized

// Selections is organized as `key, value`
// The first index used below is the key, the second is the value. Value always will be 1.
// Both data types are strings
// Refactor in the future. Should find a way to iterate through this but pressed for time

function process_selections(selections) {  // circle back, might not need keys
    if (selections[0][1] === "true") { // fav_song
        get_top_song();
    }

    if (selections[1][1] === "true") {  // likes_count
        get_likes_count();
    }

    if (selections[2][1] === "true") {  // fav_artist
        get_top_artist();
    }

    if (selections[3][1] === "true") {  // recent_tracks
        recent_tracks();
    }
}

function get_top_song() {
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=1&offset=0", false);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Authorization', 'Bearer ' + localStorage.getItem('access_token'));

    xhr.onload = function () { // https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/responseText
        if (xhr.readyState === xhr.DONE) {
            if (xhr.status === 200) {
                let json = JSON.parse(xhr.responseText);
                let artist = json.items[0].artists[0].name;
                let album = json.items[0].album.name;
                let track = json.items[0].name;
                document.getElementById("output").innerHTML += (
                    "\n" + "Favorite Song: " + track + "\n" +
                    "By: " + artist + "\n" +
                    "On Album: " + album + "\n"
                );
            }
        }
    };

    xhr.send();
}

function get_likes_count() {
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "https://api.spotify.com/v1/me/tracks", false);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Authorization', 'Bearer ' + localStorage.getItem('access_token'));

    xhr.onload = function () { // https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/responseText
        if (xhr.readyState === xhr.DONE) {
            if (xhr.status === 200) {
                let json = JSON.parse(xhr.responseText);
                let likes_count = json.total;
                document.getElementById("output").innerHTML += (
                     "\n" + "Amount of Liked Songs: " + likes_count + "\n"
                );
            }
        }
    };

    xhr.send();
}

function get_top_artist() {
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "https://api.spotify.com/v1/me/top/artists?limit=1&offset=0", false);
    //xhr.setRequestHeader('Accept', 'application/json');
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Authorization', 'Bearer ' + localStorage.getItem('access_token'));

    xhr.onload = function () { // https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/responseText
        if (xhr.readyState === xhr.DONE) {
            if (xhr.status === 200) {
                let json = JSON.parse(xhr.responseText);
                let fav_artist = json.items[0].name;
                document.getElementById("output").innerHTML += (
                    "\n" + "Favorite Artist: " + fav_artist + "\n"
                );
            }
        }
    };

    xhr.send();
}

function recent_tracks() {
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "https://api.spotify.com/v1/me/player/recently-played?limit=5", false);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Authorization', 'Bearer ' + localStorage.getItem('access_token'));

    xhr.onload = function () { // https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/responseText
        if (xhr.readyState === xhr.DONE) {
            if (xhr.status === 200) {
                document.getElementById("output").innerHTML += (
                    "\n" + "Last five songs played: " + "\n"
                );

                let json = JSON.parse(xhr.responseText);
                for (let itr = 0; itr < json.items.length; itr++) {
                    let track = (json.items[itr].track.name);
                    let album = (json.items[itr].track.album.name);
                    let artist = (json.items[itr].track.album.artists[0].name);

                    document.getElementById("output").innerHTML += (
                        "Song: " + track + "\n" +
                        "By: " + artist + "\n" +
                        "On Album: " + album + "\n" + "\n"
                    );
                }
            }
        }
    };

    xhr.send();
}

