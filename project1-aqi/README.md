# AQI TV - Air Quality Television

## Note about API Key

Even though the API key is free, I put it in a separate env file because it feels more correct to not have it directly in the code. You can either set your own API key in a file called `apikey.env` in the same directory as main.py, or you can just swap lines 17 and 18 with your API key directly in main.py as the variable `api_key`.


## Project Description

For this project, I made four TV channels that display different information based on the current air quality index of a specified location. The first one I made was the News channel, where a news anchor reports on the current air quality based on a list of phrases in a JSON file. The JSON file is separated into five categories based on the AQI value, and the program cycles through each line of the appropriate category, filling in templates with names and adjectives from a different file. It also includes a ticker at the bottom that scrolls through various breaking news headlines about air quality. 

The second channel is the Opinions channel, which I originally wanted to include in the News channel, but would have been too complicated to fit into one section. It cycles through a list of opinionated phrases about the air quality, again based on the AQI value. It uses the same names and adjectives as the News channel, as well as a list of bizarre occupations. 

The sports channel was the hardest one to make, as I had to come up with a way to relate sports to air quality, and I know nothing about sports. Although this was the simplest channel, for some reason I decided to make individual ASCII animations for each of the five AQI categories. I used a website that made this easier than typing them by hand, but it was still very time-consuming.

Finally, the Weather channel is the most straightforward one, just displaying the AQI forecast for the next few days. It took some doing to get the bar graphs to work properly, but I think it turned out well.

One of the bigger challenges was managing the timing and animation of different elements. Each channel has its own update cycle, and I had to ensure that the ticker scrolls smoothly while the main content updates at appropriate intervals. I also implemented a channel-switching mechanism that allows users to navigate between channels using number keys, with each channel maintaining its own state when you switch away and return.

The data structure for the content was another important consideration. By storing all the phrases, names, and other text in separate JSON files, I made the project much more maintainable and extensible. If I wanted to add more phrases or create additional categories, I could do so without touching the main code. This separation of content and logic is something I've been trying to practice more in my projects.

I really enjoyed writing the phrases, names, adjectives, and occupations for the different contexts. It's rare that I'm able to employ humour in my coding projects, so I took full advantage of that opportunity.  I took inspiration from the Mii News feature in Tomodachi Life for the News and Opinions channels, and also the news ticker in Cookie Clicker, which I always found super entertaining. This project was a lot of fun to make, and although I'm familiar with much of what I used to make it, I learned a lot about managing terminal output and working with more complicated data.