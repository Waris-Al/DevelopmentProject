async function editFavourite(query, type) {
    const response = await fetch('/searchSpotify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: query,
            type: type
        })
    });

    const result = await response.json();

    if (result.error) {
        console.error(result.error);
        return;
    }

    // Update the UI based on the result
    const name = result.name;
    const imageURL = result.imageURL;

    if (type === 'album') {
        document.getElementById('FavouriteAlbumName').innerText = name;
        document.getElementById('FavouriteAlbumImage').src = imageURL;
    } else if (type === 'track') {
        document.getElementById('FavouriteTrackName').innerText = name;
        document.getElementById('FavouriteTrackImage').src = imageURL;
    } else if (type === 'artist') {
        document.getElementById('FavouriteArtistName').innerText = name;
        document.getElementById('FavouriteArtistImage').src = imageURL;
    }

    // Call the /changeFavourites endpoint to save the favorite
    await fetch('/changeFavourites', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            type: `favourite${capitalizeFirstLetter(type)}`,
            name: name,
            imageURL: imageURL
        })
    });
}

function capitalizeFirstLetter(word) {
    return String(word).charAt(0).toUpperCase() + String(word).slice(1);
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
    
        editFavourite(query, type)
    
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

    function editReview(currentReview) {
        document.getElementById("editReview").style.display = "block";
        localStorage.setItem('currentReview', JSON.stringify(currentReview));
    }
    

    window.onload = function() {
        document.getElementById('FavouriteAlbumName').textContent = userFavourites.favouriteAlbum.name;
        document.getElementById('FavouriteAlbumImage').src = userFavourites.favouriteAlbum.imageUrl;  
    
        document.getElementById('FavouriteArtistName').textContent = userFavourites.favouriteArtist.name;
        document.getElementById('FavouriteArtistImage').src = userFavourites.favouriteArtist.imageUrl;  
    
        document.getElementById('FavouriteTrackName').textContent = userFavourites.favouriteTrack.name;
        document.getElementById('FavouriteTrackImage').src = userFavourites.favouriteTrack.imageUrl;  
    }
    
    
    