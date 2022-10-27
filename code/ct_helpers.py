"""
Some simple functions that will help to grab data from CrowdTangle
"""
import requests
import time


def ct_get_lists(api_token=None):
    """
    Retrieve all CrowdTangle lists, saved searches, and saved post lists
        associated with the the input API token.
    Parameters:
    - api_token (str, optional): A valid CrowdTangle API Token. You can locate your API token
        via your Crowdtangle dashboard by clicking the Gear icon in the top right ("Settings")
        and then selecting "API Access".
    Returns:
    response (dict): The response from CrowdTangle which contains both a status code and a result.
        The status will always be 200 if there is no error.
        Inside of `response["result"]["lists"]` is an array of dictionaries, each for an individual
        list in your dashboard.
        One list item looks like the below:
            {
                'id': 34083,                 # The list ID number (int)
                'title': 'US General Media', # Name of list in your dashboard
                'type': 'LIST'               # Options: ["LIST", "SAVED_SEARCH", "SAVED_POST"]
            }
        Example of full response payload: https://github.com/CrowdTangle/API/wiki/lists#response
    Errors:
    - ValueError
    Example:
        ct_get_lists(api_token="AKJHXDFYTGEBKRJ6535")
    """
    if api_token is None:
        raise ValueError("No API token was provided!")

    # api-endpoint
    URL_BASE = "https://api.crowdtangle.com/lists"
    # defining a params dict for the parameters to be sent to the API
    PARAMS = {"token": api_token}

    # sending get request and saving the response as response object
    r = requests.get(url=URL_BASE, params=PARAMS)
    if r.status_code != 200:
        out = r.json()
        print(f"status: {out['status']}")
        print(f"Code error: {out['code']}")
        print(f"Message: {out['message']}")
    return r.json()


def ct_get_posts(
    count=10,
    start_time=None,
    end_time=None,
    include_history=None,
    sort_by="date",
    types=None,
    search_term=None,
    min_interactions=0,
    offset=0,
    api_token=None,
    listIds=None,
):
    """
    Retrieve a set of posts for the given parameters from CrowdTangle using the
    `posts` endpoint with the `listIds` parameter.
    Parameters:
    - count (int, optional): The number of posts to return. Defaults to 100.
        - Options [1-100] (or higher, if you have additional access)
    - start_time (str, optional): The earliest time at which a post could be posted. Time zone is UTC.
        - Format: “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd”
            - If date with no time is passed, default time granularity = 00:00:00
    - end_time (str, optional): The latest time at which a post could be posted. Time zone is UTC.
        - Format: “yyyy-mm-ddThh:mm:ss” or “yyyy-mm-dd”
            - If date with no time is passed, default time granularity = 00:00:00
        - Default time: "now"
    - include_history (str, optional): Includes time step data for the growth of each post returned.
        - Options: 'true'
        - Default: None (not included)
    - sort_by (str, optional): The method by which to filter and order posts.
        - Options:
            - 'date'
            - 'interaction_rate'
            - 'overperforming'
            - 'total_interactions'
            - 'underperforming'
        - Default: 'overperforming'
    - types (str, optional): The types of post to include. These can be separated by commas to
        include multiple types. If you want all live videos (whether currently or formerly live),
        be sure to include both live_video and live_video_complete. The "video" type does not
        mean all videos, it refers to videos that aren't native_video, youtube or vine (e.g. a
        video on Vimeo).
        - Options:
            - "episode"
            - "extra_clip"
            - "link"
            - "live_video"
            - "live_video_complete"
            - "live_video_scheduled"
            - "native_video"
            - "photo"
            - "status"
            - "trailer"
            - "video"
            - "vine"
            -  "youtube"
        - Default: all
    - search_term (str, optional): Returns only posts that match this search term.
        Terms AND automatically. Separate with commas for OR, use quotes for phrases.
        E.g. CrowdTangle API -> AND. CrowdTangle, API -> OR. "CrowdTangle API" -> AND in that
        exact order. You can also use traditional Boolean search with this parameter.
        Default: None (no search term)
    - min_interactions (int, optional): If set, will exclude posts with total interactions
        below this threshold.
        - Options: int >= 0
        - Default: 0
    - offset (int, optional): The number of posts to offset (generally used for pagination).
        Pagination links will also be provided in the response.
    - api_token (str, optional): The API token needed to pull data. You can locate your API
        token via your CrowdTangle dashboard under Settings > API Access.
    - listIds: The IDs of lists or saved searches to retrieve. These can be separated by commas
        to include multiple lists.
        - Default: None (i.e posts from all Lists, not including saved searches or saved posts
            lists, in the Dashboard)
    Returns:
    [dict]: The Response contains both a status code and a result. The status will always
        be 200 if there is no error. The result contains an array of post objects and
        a pagination object with URLs for both the next and previous page, if they exist
    Example:
        ct_get_posts(include_history = 'true', api_token="AKJHXDFYTGEBKRJ6535")
    """

    # api-endpoint
    URL_BASE = "https://api.crowdtangle.com/posts"
    # defining a params dict for the parameters to be sent to the API
    PARAMS = {
        "count": count,
        "sortBy": sort_by,
        "token": api_token,
        "minInteractions": min_interactions,
        "offset": offset,
    }

    # add params parameters
    if start_time:
        PARAMS["startDate"] = start_time
    if end_time:
        PARAMS["endDate"] = end_time
    if include_history == "true":
        PARAMS["includeHistory"] = include_history
    if types:
        PARAMS["types"] = types
    if search_term:
        PARAMS["searchTerm"] = search_term
    if listIds:
        PARAMS["listIds"] = listIds

        # sending get request and saving the response as response object
    r = requests.get(url=URL_BASE, params=PARAMS)
    if r.status_code != 200:
        print(f"status: {r.status_code}")
        print(f"reason: {r.reason}")
        print(f"details: {r.raise_for_status()}")
    return r.json()


def download_posts(crowdtangle_list_id, start, end, max_queries, api_token):

    total_posts = 0
    query_count = 0
    retry_count = 0
    max_retries = 10

    data = []

    first_call = True
    more_data = False
    while first_call or more_data:
        try:
            if first_call:
                time.sleep(0.5)
                results = ct_get_posts(
                    count=100,
                    start_time=start,
                    end_time=end,
                    include_history="true",
                    sort_by="date",
                    api_token=api_token,
                    listIds=crowdtangle_list_id,
                )

            else:
                # This is the full URL returned by CT to continue pulling data
                # from the next page. See block below.
                time.sleep(0.5)
                response = requests.get(next_page_url)
                results = response.json()

            # Returns a list of dictionaries where each dict represents one post.
            posts = results["result"]["posts"]
            num_posts = len(posts)

            # Flip first_call if we get a successful first call with posts
            # NOTE: repeated first calls with no data will break after too many attempts
            if first_call:
                if (results["status"] == 200) and (num_posts != 0):
                    print("Successful first call.")
                    print("Setting first_call = False")
                    first_call = False

            # Reset and then grab the pagination url if it is there
            next_page_url = None
            if "pagination" in results["result"]:
                if "nextPage" in results["result"]["pagination"]:
                    next_page_url = results["result"]["pagination"]["nextPage"]
                    print(f"Found next page: {next_page_url}")
                    more_data = True

            if next_page_url is None:
                more_data = False

        # TODO: Check the rate limit without fpierri's increase. Matt added wait time
        # between calls to be safe.
        except Exception as e:  # 6 calls/minute limit if you request them
            print(e)

            # Handle the retries...
            print(f"There are {max_retries-retry_count} retries left.")
            retry_count += 1
            if (max_retries - retry_count) <= 0:
                break
            else:
                wait_time = 5 * retry_count
                print(f"Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                print(f"Retrying...")
                continue

        else:
            if num_posts == 0:
                print("Zero posts were returned.")
                print(f"There are {max_retries-retry_count} retries left.")
                retry_count += 1

                if (max_retries - retry_count) <= 0:
                    break
                else:
                    wait_time = 5 * retry_count
                    print(f"Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    print(f"Retrying...")
                    continue

            else:
                # Reset the retry count to zero
                retry_count = 0

                most_recent_date_str = posts[0]["date"]
                oldest_date_str = posts[-1]["date"]
                print(
                    f"\t|--> {oldest_date_str} - {most_recent_date_str}"
                    f": {num_posts:,} posts."
                )

                # Convert each post into bytes with a new-line (`\n`)
                for post in posts:
                    data.append(post)

                total_posts += num_posts
                print(f"Total posts collected: {total_posts:,}")

            # Increment for successful call and break after we get the total
            # number of queries.
            query_count += 1
            if query_count >= max_queries:
                break

    print("All data downloaded.")
    return data
