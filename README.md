# Scrapping Anime Information
###### Website Scrapped: [Anime List](https://myanimelist.net/anime.php)
## Summary 
The purpose of this project is to extract information on anime from a website to be stored in a PostgreSQL database. SQL queries are then written on the database to identify valuable information trends in data. Quires are then displayed as visuals on a dashboard so that the user can easily identify the trends in correlation with the anime rating.

## Dash App
Created a web application to display the data collected through visuals from the plotly library. Two types of visuals are 
displayed, categorical and continuous data. The user of the web app able to change the x-input in relation to the rating
as the y-input.

## How data extracted
Before scrapping can start there must be a database to store the information. 
###### The structure of the PostgreSQL database is the following
```sql
CREATE TABLE IF NOT EXISTS animeinfo(
    anime_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    rating DECIMAL CHECK ( rating >= 0 AND rating <= 10 ),
    studio TEXT,
    themes TEXT,
    categories TEXT,
    eps INTEGER,
    mins_per_epi INTEGER);
CREATE TABLE IF NOT EXISTS url_scraped(
    web_id SERIAL PRIMARY KEY,
    web_url TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS info_scraping_index(
    web_id INTEGER REFERENCES url_scraped(web_id),
    category TEXT,
    page_index INTEGER,
    div_index INTEGER);
```

Created functions to add rows of data into the database
###### Insert and Update Functions
```python
def update_db(new_row: InfoRow):
    db_cur.execute("SELECT name FROM animeinfo")
    names_in_db = set(map(lambda x: x[0], db_cur.fetchall()))
    if new_row.name in names_in_db:
        db_cur.execute(f"UPDATE animeinfo SET "
                       f"description = '{new_row.description}',"
                       f"rating = {new_row.rating},"
                       f"studio = '{new_row.studio}',"
                       f"themes = '{new_row.themes}',"
                       f"categories = '{new_row.categories}',"
                       f"eps = {new_row.eps},"
                       f"mins_per_epi = {new_row.mins_per_epi} "
                       f"WHERE name = '{new_row.name}'")
    else:
        db_cur.execute("INSERT INTO "
                       "animeinfo(name, description, rating, studio, themes, categories, eps, mins_per_epi) "
                       "VALUES "
                       f"('{new_row.name}', '{new_row.description}', {new_row.rating}, '{new_row.studio}', "
                       f"'{new_row.themes}', '{new_row.categories}', {new_row.eps}, {new_row.mins_per_epi})")
    db_conn.commit()

def insert_url_scraped(url):
    query = "SELECT DISTINCT web_url FROM url_scraped"
    db_cur.execute(query)
    urls_stored = set(map(lambda x: x[0], db_cur.fetchall()))
    if url not in urls_stored:
        db_cur.execute(f"INSERT INTO url_scraped(web_url) VALUES ('{url}')")
        db_conn.commit()

def insert_info_scraping_index(new_row: InforScrapingIndexRow):
    db_cur.execute("SELECT DISTINCT category FROM info_scraping_index")
    categories_stored = set(map(lambda x: x[0], db_cur.fetchall()))
    if new_row.category in categories_stored:
        db_cur.execute("UPDATE info_scraping_index SET "
                       f"web_id = {new_row.web_id}, "
                       f"category = '{new_row.category}', "
                       f"page_index = {new_row.page_index}, "
                       f"div_index = {new_row.div_index} "
                       f"WHERE category = '{new_row.category}'")
    else:
        db_cur.execute("INSERT INTO info_scraping_index(web_id, category, page_index, div_index) VALUES "
                       f"({new_row.web_id}, '{new_row.category}', {new_row.page_index}, {new_row.div_index})")
    db_conn.commit()
```
Now that the database is initialized, using BeautifulSoup I parsed the html structure of the website I was scrapping.
Each anime cell was organized in separate divs of the same class, so I store a list of all the divs and created a function
to extract information from the div.
###### Method for loading pages
```python
def load_page(self):
    response = requests.get(self.url, params={'page': f'{self._next_page}'})
    self.current_url = (f'https://myanimelist.net/anime/genre/{map_categories[self._category]}/{self._category}?'
                        f'page={self._next_page}')
    self._next_page += 1

    soup = BeautifulSoup(response.content, 'html.parser')
    attribute = {
        'class': ['js-anime-category-producer', 'seasonal-anime', 'js-seasonal-anime', 'js-anime-type-all',
                  'js-anime-type-1']
    }
    self.divs_filtered = soup.find_all('div', attrs=attribute)
    return response.status_code
```
###### Method for extracting divs
```python
def extract_div(self):
    current_div = self.divs_filtered[self._next_div]
    self._next_div += 1

    title = current_div.find('a', attrs={'class': ['link-title']}).get_text().replace("'", "''")
    par = current_div.find("p", attrs={'class': ['preline']}).get_text().replace("'", "''")

    rating = current_div.find("div", attrs={'title': 'Score'})
    rating = str(rating).strip()
    index = rating.find('</i>') + 4
    try:
        rating = float(rating[index:index + 4])
    except ValueError:
        rating = 'NULL'

    studio = 'NULL'
    themes = 'NULL'

    for prop in current_div.find_all('div', attrs={'class': ['property']}):
        spans = prop.find_all('span')
        info_caption = spans[0].get_text()
        try:
            if info_caption == 'Studio':
                studio = prop.a.get_text().replace("'", "''")
        except AttributeError:
            pass

        try:
            if info_caption == 'Themes':
                themes = ", ".join([a.get_text() for a in prop.find_all('a')]).replace("'", "''")
        except AttributeError:
            pass

    categories = current_div.find('div', attrs={'class': ['genres-inner', 'js-genre-inner']})
    categories = ", ".join([a.get_text() for a in categories.find_all("a")]).replace("'", "''")

    info = current_div.find_all('span', attrs={'class': ['item']})
    info = info[2].find_all('span')

    eps = ''.join([val for val in info[0].get_text() if val.isdigit()])
    if not eps:
        eps = 'NULL'

    mins = ''.join([val for val in info[1].get_text() if val.isdigit()])
    if not mins:
        mins = 'NULL'

    current_anime = InfoRow(find_info_id(title), title, par, rating, studio, themes, categories, eps, mins)
    return current_anime
```
The class is organized in a way that can be iterated over until all the cells for an anime category is extracted.
###### Code snippets of using the class iteratively
```python
info_conn = ScrapeInfo('Adventure')
all_genres = ['Action', 'Avant_Garde', 'Award_Winning', 'Boys_Love', 'Comedy', 'Drama', 'Fantasy', 'Girls_Love', 
              'Gourmet', 'Mystery', 'Romance', 'Sci-Fi', 'Slice_of_Life', 'Sports', 'Supernatural', 'Suspense']
for genre in all_genres:
    info_conn.set_category(genre)
    for row in info_conn:
        update_db(row)
```

## Data Visualization
Using basic call backs, data graphs are updated in real time in the web application. 
