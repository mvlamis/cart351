Query 3:
This query selects all documents from the collection where the after_mood field matches any value within the positive_moods list. It uses the $in operator for filtering.

Query 4: 
This query retrieves all documents in the collection. It then sorts the results in ascending order alphabetically based on the event_name field using .sort("event_name", 1).

Query 5:
This query filters for documents where the day field is either "Monday" or "Tuesday" using the $in operator. The resulting documents are then sorted in ascending order based on the event_affect_strength field.

Query 6:
This query filters for documents that satisfy two conditions simultaneously: the start_mood must be in the negative_moods list AND the after_mood must also be in the negative_moods list. The results are then sorted alphabetically by the weather field.

My favourite part of the visualization I did for project 2 was the use of sine waves, so I wanted to play with them a bit more in this exercise. I created four different modes for displaying the data points as sine waves: vertical, horizontal, split, and helix. The hardest part was figuring out things like phases and offsets to get the waves to look right in each mode, but I think it turned out pretty well.