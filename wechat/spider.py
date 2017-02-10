import requests
from bs4 import BeautifulSoup

from app import create_app
from app.extensions import db
from app.models import Sentence


app = create_app('development')
app_context = app.app_context()
app_context.push()


list_page = requests.get("https://bigbangtrans.wordpress.com/")

list_page_data = list_page.text

list_page_soup = BeautifulSoup(list_page_data)

all_links = list_page_soup.find_all(name="a")


def get_all_episode_links():
    episode_links = []
    for item in all_links:
        link = item.get("href")
        if "episode" in link:
            episode_links.append(link)
    return episode_links


def parse_episode(episode_link):
    episode_page = requests.get(episode_link)
    episode_page_data = episode_page.text
    episode_page_soup = BeautifulSoup(episode_page_data)
    sentences = parse_sentence(episode_page_soup)
    season = int(episode_page_soup.title.string.split(" ")[1])
    episode = int(episode_page_soup.title.string.split(" ")[3])
    return season, episode, sentences


def parse_sentence(episode_page_soup):
    sentences = episode_page_soup.find_all("p")
    return sentences


def insert_into_db():
    for episode_link in get_all_episode_links():
        season, episode, sentences = parse_episode(episode_link)
        for sentence in sentences:
            if sentence.text:
                sen = Sentence(
                    season=season,
                    episode=episode,
                    sentence=sentence.text.strip()
                )
                db.session.add(sen)
        db.session.commit()

insert_into_db()


