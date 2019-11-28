userAgent = "RedditToTwitter"
reddit = dict(
    subreddit = "pics",
    checkDelay = 60,
    maxResults = 10,
    account = dict(
        clientId = "",
        clientSecret = "",
        username = "",
        password = "",
    ),
)
twitter = dict(
    account = dict(
        consumerKey = "",
        consumerSecret = "",
        accessToken = "",
        accessTokenSecret = "",
    ),
)
redis = dict(
    host = "localhost",
    port = "6379",
    db = "0",
    tempcachekey = "RTT_Pics_Cache",
)