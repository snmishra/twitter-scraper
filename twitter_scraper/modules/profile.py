from requests_html import HTMLSession, HTML
from lxml.etree import ParserError
import mechanicalsoup

session = HTMLSession()

browser = mechanicalsoup.StatefulBrowser()
browser.addheaders = [('User-agent', 'Firefox')]

class Profile:
    """
        Parse twitter profile and split informations into class as attribute.
        
        Attributes:
            - name
            - username
            - birthday
            - biography
            - website
            - profile_photo
            - likes_count
            - tweets_count
            - followers_count
            - following_count
    """
    def __init__(self, username):
        browser.open("https://twitter.com/"+username)
        page = browser.get_current_page()
        self.username = username
        self.__parse_profile(page)

    def __parse_profile(self, page):
        # parse location, also check is username valid 
        try:
            self.location = page.find(attrs={"class":"ProfileHeaderCard-locationText u-dir"}).text.strip()
        except AttributeError:
            raise ValueError(
                    f'Oops! Either "@{self.username}" does not exist or is private.')
        except IndexError:
            self.location = None

        # parse birthday
        try:
            self.birthday = page.find(attrs={"class":"ProfileHeaderCard-birthdateText u-dir"}).find().text.strip().replace("Born ", "")
        except:
            self.birthday = None

        # parse URL of profile photo
        try:
            self.profile_photo = page.find(attrs={"class":"ProfileAvatar-image"}).attrs['src']
        except:
            self.profile_photo = None
        try:
            self.profile_photo_mini = page.find(attrs={"class":"ProfileCardMini-avatarImage"}).attrs['src']
        except:
            self.profile_photo_mini = None

        # parse full name
        name_text = page.find("title").contents[0]
        self.name = name_text[:name_text.find('(')].strip()

        # parse biography
        self.biography = self._process_paragraph(page.find(attrs={"class":"ProfileHeaderCard-bio u-dir"}))

        # parse user's website adress
        try:
            self.website = page.find(attrs={'class': 'ProfileHeaderCard-urlText u-dir'}).find().text.strip()
        except:
            self.website = None
        
        # parse count of followers
        self.followers_count = self._get_count(page, 'followers')

        # parse count of likes
        self.likes_count = self._get_count(page, 'favorites')

        # parse count of following
        self.following_count = self._get_count(page, 'following')

        # parse count of tweets
        self.tweets_count = self._get_count(page, 'tweets')

    def _get_count(self, page, attr):
        try:
            page.find(attrs={"data-nav":attr}).find(attrs={"class":"ProfileNav-value"})
            return int(q.attrs["data-count"])
        except:
            return 0

    def _process_paragraph(self, contents):
        output = contents.text
        links = [elt.attrs['href'] for elt in contents.find_all('a')]
        return output, links

    def __dir__(self):
        return [
            'name',
            'username',
            'birthday',
            'biography',
            'website',
            'profile_photo',
            'profile_photo_mini',
            'likes_count',
            'tweets_count',
            'followers_count',
            'following_count'
        ]

    def __repr__(self):
        return f'<profile {self.username}@twitter>'
