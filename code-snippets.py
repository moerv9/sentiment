'''
PANDAS
to delete a dataframe column pandas
del df['Column Name]

Number of Rows
df.shape[0]


Twint scrape by city (inspo):
def scrape_by_city(keywords, since, outfile):
    unique_cities=set(all_cities) #To get unique cities of country
    cities = sorted(unique_cities) #Sort & convert datatype to list
    for city in cities:
        print(city)
        c = twint.Config()
        c.Search = keywords #search keyword
        c.Since = since
        c.Store_csv = True
        c.Output = "./" + outfile
        c.Near = city
        c.Hide_output = True
        c.Count = True
        c.Stats = True
        c.Resume = 'resume.txt'
        twint.run.Search(c)



'''