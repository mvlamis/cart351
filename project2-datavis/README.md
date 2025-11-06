# Music Data Visualization
This project is a visualizer for music listening data from Last.fm and Spotify. It retrieves a user's recent tracks from either platform, fetches audio features from Reccobeats, and generates interactive visualizations using D3.js. 

Spotify recently deprecated the audio features API that I was planning on using, so I found Reccobeats which is used as an alternative source. The Spotify API is still used to get the user's recently played tracks and to cross-reference song IDs, but the audio features (acousticness, dancability, energy, instrumentalness, liveliness, loudness, speechiness, tempo, valence) are pulled from Reccobeats instead. I also added Last.fm support since it has a more straightforward authentication process so people don't have to trust a shady Flask app with their credentials. I'm very familiar with APIs at this point, but I've never had to combine this many in one project before. I would have liked to add Apple Music support but I'd rather not part with the $99/year for the developer program. This app is difficult to run locally since Spotify requires a publicly accessible redirect URI for OAuth, so I'm going to look into hosting options once everything is finished.

This was my first time working with D3, but I've been playing with SVGs for a while so I was happy to be able to apply some of that knowledge. I initially planned on using the HTML canvas element, but I ran into a billion different problems when I was starting and D3 works better with SVGs anyway so I went with that instead. The visualization is made up of several layers, each combining different audio features to create a different image for each song and account. D3 is meant for more traditional data visualizations like bar charts and scatter plots, so I had to stick to SVGs which means I didn't explore quite as many of D3's features as I would have liked. What I like about my visualization is that you can't really extrapolate anything meaningful from looking at it, but it's still going to be unique to each user.

Since I'm using an API with so many different audio feature variables, It was difficult to incorporate every single one. I spent a lot of time struggling with the math, specifically for the waves layer the trigonometry I had to dig up from the back of my brain. It's not interactive, but if I had more time I would have liked to add some motion or interaction to the visualization. I was inspired by the old iTunes visualizer that used the live audio input to create a dynamic image, but I've also been stressing over my upcoming Spotify Wrapped (I can't let my friends see my embarrassing listening habits (I listened to the same song hundreds of times on repeat)) so I decided to use historical track data instead of individually.

Getting the project to this point took a lot longer than I expected, in no small part because of the Reccobeats API. Their documentation is pretty sparse and I had to do a lot of trial and error to figure out how to get the audio features for multiple tracks at once. Overall, I'm happy with how my first Flask app turned out and I learned a lot about server-side web development in the process.



- API Documentation
    - https://www.last.fm/api
    - https://developer.spotify.com/documentation/web-api
    - https://reccobeats.com/docs/documentation/introduction
    - https://d3js.org/getting-started

TODO
- loading screen with per song progress bar
- prompt to refresh if user has data already
- styling
- base template?