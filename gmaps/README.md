# Business Data Scraper
The Business Data Scraper is a powerful application designed to help you find the best businesses in a specific area based on **Google Maps** data. By inputting a search term (e.g., restaurant, gym) and defining an area, the app scrapes relevant business data using *Selenium*, sorts it by a score based on the number of reviews and star ratings, and presents you with the top businesses in that area in *csv* format.

## Requirements
- Python 3
- Selenium
- WebDriver for your preferred browser (e.g., ChromeDriver for Google Chrome)

## Usage
Help:
```bash
python business_data.py -h
```

### Run the application:
```bash
python business_data.py -s <search_term> -a <area>
```

- `search_term` is the term you want to search for (e.g., restaurant, gym).
- `area` is the bunch of coordinates that define the area you want to search in given by Google Maps url.
In order to get the area, you need to focus an area in google maps where you want to search and copy the url.  
For example:
![Google Maps screenshot showing the captured url of the area](url_area_sample.png)
**Note**: Only the coordinates part is important to have (between `@` and `z`, including them).

### Open links
Later on, you can use `open_links.py` to open a bunch of links in your browser at once:
```bash
python open_links.py -n amount_of_links_to_open name_of_csv_file
```

### Customize sorting score
It is possible to change the `weight_reviews` and `weight_stars` parameters in the `BusinessData` class to change the sorting function. The weight of reviews can be interpreted as **popularity of the business**, while the weight of stars can be interpreted as **quality of the business**. This is important if you are prioritizing the popularity or quality of a business.  
For example, `weight_reviews=0.2` and `weight_stars=0.8` will display businesses with more stars first, over those with more reviews. This could result in some stores with a large number of stars and a small number of reviews.  
By default, its values are equal to `0.5` and should sum to `1`. Feel free to adjust these values to your use case interest.
