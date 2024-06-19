def format_url(url):
    folder = url.split('/static/')[1].rsplit('/', 1)[0]
    if len(folder) >= 100:
        folder = "..." + folder[-47:]

    return folder
