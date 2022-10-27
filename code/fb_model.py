"""
A data model to work with Facebook data.
"""
from cleantext import clean
from datetime import datetime, timezone


def clean_text(text):
    """
    A convenience function for cleantext.clean because it has an ugly amount
    of parameters.
    """
    return clean(
        text,
        fix_unicode=True,  # fix various unicode errors
        to_ascii=True,  # transliterate to closest ASCII representation
        lower=True,  # lowercase text
        no_line_breaks=True,  # fully strip line breaks as opposed to only normalizing them
        no_urls=True,  # replace all URLs with a special token
        no_emoji=True,  # remove emojis
        no_emails=True,  # replace all email addresses with a special token
        no_phone_numbers=True,  # replace all phone numbers with a special token
        no_numbers=False,  # replace all numbers with a special token
        no_digits=False,  # replace all digits with a special token
        no_currency_symbols=False,  # replace all currency symbols with a special token
        no_punct=True,  # remove punctuations
        replace_with_punct="",  # instead of removing punctuations you may replace them
        replace_with_url="",
        replace_with_email="",
        replace_with_phone_number="<PHONE>",
        replace_with_number="<NUMBER>",
        replace_with_digit="0",
        replace_with_currency_symbol="<CUR>",
        lang="en",  # set to 'de' for German special handling
    )


def get_dict_val(dictionary: dict, key_list: list = []):
    """
    Return `dictionary` value at the end of the key path provided
    in `key_list`.
    Indicate what value to return based on the key_list provided.
    For example, from left to right, each string in the key_list
    indicates another nested level further down in the dictionary.
    If no value is present, a `None` is returned.
    Parameters:
    ----------
    - dictionary (dict) : the dictionary object to traverse
    - key_list (list) : list of strings indicating what dict_obj
        item to retrieve
    Returns:
    ----------
    - key value (if present) or None (if not present)
    Raises:
    ----------
    - TypeError
    Examples:
    ---------
    # Create dictionary
    dictionary = {
        "a" : 1,
        "b" : {
            "c" : 2,
            "d" : 5
        },
        "e" : {
            "f" : 4,
            "g" : 3
        },
        "h" : 3
    }
    ### 1. Finding an existing value
    # Create key_list
    key_list = ['b', 'c']
    # Execute function
    get_dict_val(dictionary, key_list)
    # Returns
    2
    ~~~
    ### 2. When input key_path doesn't exist
    # Create key_list
    key_list = ['b', 'k']
    # Execute function
    value = get_dict_val(dictionary, key_list)
    # Returns NoneType because the provided path doesn't exist
    type(value)
    NoneType
    """
    if not isinstance(dictionary, dict):
        raise TypeError("`dictionary` must be of type `dict`")

    if not isinstance(key_list, list):
        raise TypeError("`key_list` must be of type `list`")

    retval = dictionary
    for k in key_list:

        # If retval is not a dictionary, we're going too deep
        if not isinstance(retval, dict):
            return None

        if k in retval:
            retval = retval[k]

        else:
            return None
    return retval


class PostBase:
    """
    Base class for social media post.
    Classes for specific platforms can inheret it.
    It defines the common functions that the children classes
    should have.
    """

    def __init__(self, post_object):
        """
        This function initializes the instance by binding the post_object
        Parameters:
            - post_object (dict): the JSON object of the social media post
        """
        if post_object is None:
            raise ValueError("The post object cannot be None")
        self.post_object = post_object

    def is_valid(self):
        """
        Check if the data is valid
        """
        raise NotImplementedError

    def get_value(self, key_list: list = []):
        """
        This is the same as the midterm.get_dict_val() function
        Return `dictionary` value at the end of the key path provided
        in `key_list`.
        Indicate what value to return based on the key_list provided.
        For example, from left to right, each string in the key_list
        indicates another nested level further down in the dictionary.
        If no value is present, a `None` is returned.
        Parameters:
        ----------
        - dictionary (dict) : the dictionary object to traverse
        - key_list (list) : list of strings indicating what dict_obj
            item to retrieve
        Returns:
        ----------
        - key value (if present) or None (if not present)
        """
        return get_dict_val(self.post_object, key_list)

    def get_timestamp(self):
        """
        Return the post time-of-creation
        """
        raise NotImplementedError

    def get_post_ID(self):
        """
        Return the ID of the post as a string
        """
        raise NotImplementedError

    def get_link_to_post(self):
        """
        Return the link to the post so that one can click it and check
        the post in a web browser
        """
        raise NotImplementedError

    def get_user_ID(self):
        """
        Return the ID of the user as a string
        """
        raise NotImplementedError

    def get_URLs(self):
        """
        Return all URLs (list of dicts) embedded in the social media post
        Each element is a URL dict. Dict keys: {"raw_url", "expanded_url", "domain"}
        """
        raise NotImplementedError

    def get_hashtags(self):
        """
        Return the list of hashtags embedded in the social media post
        """
        raise NotImplementedError

    def get_text(self):
        """
        Return the text of the social media post
        """
        raise NotImplementedError

    def get_media(self):
        """
        Return the media (photo, video, etc.) embedded in the social media post
        """
        raise NotImplementedError

    def __repr__(self):
        """
        Define the representation of the object.
        """
        return f"<{self.__class__.__name__}() object>"


class FbIgPost(PostBase):
    """
    Class to handle Facebook/Instagram post obtained from CrowdTangle
    """

    def __init__(self, fb_ig_post):
        """
        This function initializes the instance by binding the fb_ig_post object
        Parameters:
            - fb_ig_post (dict): the JSON object of a post
        """
        super().__init__(fb_ig_post)

    def get_post_ID(self):
        """
        Return the ID of the post as a string.
        """
        post_id = self.get_value(["id"])
        if post_id is None:
            return None
        else:
            return str(post_id)

    def get_link_to_post(self):
        """
        Return the link to the FB/IG post so that one can click it and check
        the post in a web browser
        """
        return self.get_value(["postUrl"])

    def get_platform(self):
        """
        Return the platform of a post. {Facebook, Instagram}
        """
        return self.get_value(["platform"])

    def get_post_type(self):
        """
        Return the type of a post. {status, photo, album, link, live_video_complete, video, native_video, youtube}
        """
        return self.get_value(["type"])

    def convert_to_timestamp(self, date):
        """
        Convert date (str) of format "%Y-%m-%d %H:%M:%S" to timestamp (int)
        """

        return int(
            datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            .replace(tzinfo=timezone.utc)
            .timestamp()
        )

    def get_timestamp(self):
        """
        Return post timestamp (int)
        """
        date = self.get_value(["date"])
        if date is not None:
            return self.convert_to_timestamp(date)
        else:
            return None

    def get_update_timestamp(self):
        """
        Return post update timestamp (int)
        """
        date = self.get_value(["updated"])
        if date is not None:
            return self.convert_to_timestamp(date)
        else:
            return None

    def get_user_ID(self):
        """
        Return the ID of the account as a string.
        """
        user_id = self.get_value(["account", "id"])
        if user_id is None:
            return None
        else:
            return str(user_id)

    def get_text(self, clean=False, struct=False):
        """
        Extract the text of the post.
        The text could appear in multiple places:
            message, title, description, imageText
        Parameters:
            - clean (bool, default False): If True, the text will be cleaned;
                if False, return the raw text
            - struct (bool, default False): If True, return a dict;
                if False, return a string (concatenation of all the fields)
        Returns:
            - Depending on the value of struct, a string or a dict is returned.
                - If struct == False, the function will return the concatenation
                    of all text fields indicated above
                - If struct == True, the returned dictionary will contain each
                    field indicated above as a key, and its value will be the
                    text string from that field
        """
        text_obj = {}
        for text_field in ["message", "title", "description", "imageText"]:
            temp_text = self.get_value([text_field])
            if temp_text is not None:
                if clean:
                    temp_text = clean_text(temp_text)
                text_obj[text_field] = temp_text
        if struct:
            return text_obj
        else:
            return " ".join(text_obj.values())

    def get_hashtags(self):
        """
        Get all hashtags from the post by matching the # symbol in the text
        The code is borrowed from
        https://stackoverflow.com/questions/2527892/parsing-a-tweet-to-extract-hashtags-into-an-array
        Returns:
            - A list of strings representing the hashtags, # symbols are not included
        """
        text_string = self.get_text()
        return [part[1:] for part in text_string.split() if part.startswith("#")]

    def get_URLs(self):
        """
        Get all urls from the post.
        They can be found in the "expandedLinks" field.
        Returns:
            - A list of strings representing the URLs
        """
        urls = []
        expandedUrls = self.get_value(["expandedLinks"])
        if expandedUrls is not None:
            urls = [item["expanded"] for item in expandedUrls]
        return urls

    def get_media(self):
        """
        Get all media from the post.
        They can be found in the "extended_entities" field.
        Returns:
            - media (list of dicts) : A list of media objects that take the following form:
                {
                    'media_url' : <url_str>,
                    'media_type' : <type_str> # E.g., 'photo', 'video', 'gif'
                }
        """
        media = []
        media_list = self.get_value(["media"])
        if media_list is not None:
            for item in media_list:
                media_obj = {"media_url": item["url"], "media_type": item["type"]}
                if "full" in item:
                    media_obj["media_full_url"] = item["full"]
                media.append(media_obj)
        return media

    def __repr__(self):
        """
        Define the representation of the object.
        """
        return "".join(
            [
                f"<{self.__class__.__name__}() object> {self.get_value(['platform'])} post from @{self.get_value(['account', 'handle'])}\n",
                f"Link: {self.get_link_to_post()}",
            ]
        )
