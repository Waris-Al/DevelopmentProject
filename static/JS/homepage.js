
    async function getAccessToken() {
        const response = await fetch("https://accounts.spotify.com/api/token", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": "Basic " + btoa(clientId + ":" + clientSecret)
            },
            body: "grant_type=client_credentials"
        });
        const data = await response.json();
        return data.access_token;
    }

    async function editFavouriteAlbum(query) {
        const token = await getAccessToken();
        const response = await fetch(`https://api.spotify.com/v1/search?q=${encodeURIComponent(query)}&type=album`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const searchInfo = await response.json();
        if (searchInfo.albums.items.length > 0) {
            const album = searchInfo.albums.items[0];
            document.getElementById('FavouriteAlbumName').innerText = album.name;
            document.getElementById('FavouriteAlbumImage').src = album.images[0].url;

            await fetch('/changeFavourites', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: 'favouriteAlbum',   
                    name: album.name,  
                    imageURL: album.images[0].url  
                })
            });
            
        }
    }

    async function editFavouriteSong(query) {
        const token = await getAccessToken();
        const response = await fetch(`https://api.spotify.com/v1/search?q=${encodeURIComponent(query)}&type=track`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const searchInfo = await response.json();
        if (searchInfo.tracks.items.length > 0) {
            const song = searchInfo.tracks.items[0];
            document.getElementById('FavouriteSongName').innerText = song.name;
            document.getElementById('FavouriteSongImage').src = song.album.images[0].url;

            await fetch('/changeFavourites', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: 'favouriteSong',      
                    name: song.name,   
                    imageURL: song.album.images[0].url
                })
            });
            
        }
    }

    async function editFavouriteArtist(query) {
        const token = await getAccessToken();
        const response = await fetch(`https://api.spotify.com/v1/search?q=${encodeURIComponent(query)}&type=artist`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const searchInfo = await response.json();
        if (searchInfo.artists.items.length > 0) {
            const artist = searchInfo.artists.items[0];
            document.getElementById('FavouriteArtistName').innerText = artist.name;
            document.getElementById('FavouriteArtistImage').src = artist.images[0].url;

            await fetch('/changeFavourites', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: 'favouriteArtist',     
                    name: artist.name,
                    imageURL: artist.images[0].url
                })
            });
            
        }
    }



    function replaceWithSearch(id, type) {
        const container = document.getElementById(id);
        
        if (!container) {
            console.error(`Container with ID '${id}' not found!`);
            return;
        }
    
        const editButton = container.querySelector("button");
        if (editButton) {
            editButton.style.display = "none"; 
        }
    
        const searchDiv = document.createElement('div');
        searchDiv.innerHTML = `
            <input type="text" id="${id}Query" placeholder="Search for ${type}" />
            <button onclick="searchAndUpdate('${id}', '${type}')">Search</button>
        `;
        container.appendChild(searchDiv);
    }
    
    function searchAndUpdate(id, type) {
        const query = document.getElementById(`${id}Query`).value;
        if (!query) return;
    
        if (type === 'album') {
            editFavouriteAlbum(query);
        } else if (type === 'song') {
            editFavouriteSong(query);
        } else if (type === 'artist') {
            editFavouriteArtist(query);
        }
    
        const editButton = document.getElementById(`${id}Edit`);
        if (editButton) {
            editButton.style.display = "block";
        }
    
        const searchDiv = document.getElementById(id).querySelector("div");
        if (searchDiv) {
            searchDiv.remove();
        }
    }
    

    function addReview() {
        document.getElementById("newReview").style.display = "block";
    }

    

    window.onload = function() {
        document.getElementById('FavouriteAlbumName').textContent = userFavourites.favouriteAlbum.name;
        document.getElementById('FavouriteAlbumImage').src = userFavourites.favouriteAlbum.imageUrl;  
    
        document.getElementById('FavouriteArtistName').textContent = userFavourites.favouriteArtist.name;
        document.getElementById('FavouriteArtistImage').src = userFavourites.favouriteArtist.imageUrl;  
    
        document.getElementById('FavouriteSongName').textContent = userFavourites.favouriteSong.name;
        document.getElementById('FavouriteSongImage').src = userFavourites.favouriteSong.imageUrl;  
    }
    
    
    