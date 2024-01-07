# import sql database


months = [
    "jan", "feb", "mar", "apr",
    "may", "jun", "jul", "aug",
    "sep", "oct", "nov", "dec"]

# TODO: platform svgs (like vndb.org, but don't just copy theirs)

regions = {
    # "AUS": "\U0001F1E6\U0001F1FA",  # flag: Australia
    "EU": "\U0001F1EA\U0001F1FA",  # flag: European Union Flag
    "JP": "\U0001F1EF\U0001F1F5",  # flag: Japan
    "KOR": "\U0001F1F0\U0001F1F7",  # flag: South Korea
    "NA": "\U0001F1FA\U0001F1F8",  # flag: United States
    "RU": "\U0001F1F7\U0001F1FA",  # flag: Russia
    "WW": "\U0001F310"}  # globe with meridians


# timeline
#  year
#    year-label: 1996-2023
#    columns: 1-4 (grouping relationships [engine, series etc.])
#      months: jan-dec
#        release: game / beta / demo
#          icon: .svg
#          name
#          platform: .svg
#          region: emoji
