import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

anime_data = pd.read_csv('anime_data.csv')

# filter out anime where source is unknown
anime_data = anime_data[anime_data['source'] != 'unknown']

# get the number of anime for each source by year
source_counts = anime_data.groupby(['year', 'source']).size().reset_index(name='count')

# create a pivot table to make it easier to plot
source_counts_pivot = source_counts.pivot(index='year', columns='source', values='count')

# plot the percentage of anime that are light novels per year
light_novel_counts = pd.read_csv('light_novel_counts.csv')

# calculate how many visual novel adaptations were made each year
visual_novel_counts = anime_data[anime_data['source'] == 'visual_novel'].groupby('year').size()
visual_novel_percentages = visual_novel_counts / anime_data.groupby('year')['year'].count() * 100

# plot source counts and light/visual novel percentages on subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(30, 20))

ax1.set_title('Anime per Year by Source')
ax1.plot(source_counts_pivot)
ax1.legend(source_counts_pivot.columns)
ax1.set_yscale('log')
# use linear scale for anime counts
# set y axis labels at 10, 100, and 500
ax1.yaxis.set_major_locator(mticker.FixedLocator([10, 100, 500]))
ax1.yaxis.set_major_formatter(mticker.ScalarFormatter())
ax2.set_title('Light Novel Percentage by Year')
ax2.plot(light_novel_counts['year'], light_novel_counts['light_novel_percentage'])
ax3.set_title('Visual Novel Percentage by Year')
ax3.plot(visual_novel_percentages)

# save the plot to a file
fig.savefig('anime_sources_by_year.png')