import requests
from urllib import request, response, error, parse
from urllib.request import urlopen
from bs4 import BeautifulSoup


def first_names(tag):
    '''finds the id=show_signups element on a profile page'''
    try:
        return tag['id'] == 'show_signups'
    except:
        return False


def get_names(challenge):
    ''' returns names of all participants signed up to a challenge '''
    participants = []

    page = urlopen(f'https://archiveofourown.org/collections/{challenge}/profile')
    soup = BeautifulSoup(page, 'lxml')

    parent = soup.find(first_names).parent

    for child in parent.descendants:
        if child.name == 'li':
            user = child.string.strip(",")
            if "(" in user:
                user = user.split("(")[1].strip(")")
            participants.append(user)
            
    return participants


def get_gifts(user, challenge):
    ''' returns gifts belonging to a specific challenge for user '''
    gifts = 0
    page = urlopen(f"https://archiveofourown.org/users/{user}/gifts")
    soup = BeautifulSoup(page, 'lxml')

    headings = soup.find_all('h5')
    for heading in headings:
        if 'fandoms' not in heading['class']:
            # check the collection
            if heading.a['href'] == f"/collections/{challenge}":
                gifts += 1
    return gifts