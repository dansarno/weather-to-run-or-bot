import time
from weather import day_weather
from weather import forecast
from bots import tweet_composer
from bots import config


def rankings_interpreter(rankings):
    # Simple ranking interpreter that returns the best ranked day segments
    segments = []
    alert_level = ""
    is_first = True
    for level, segs in rankings.items():
        if segs:
            for seg in segs:
                segments.append(seg.name)
            if is_first:
                alert_level = level
                is_first = False
    return segments, alert_level


def produce_dashboard_image(day, rankings, filename, to_show=False):
    fig_handle = forecast.plot_scores(day, rankings, to_show)
    fig_handle.savefig(filename)


def daily_tweet(api_obj):
    tomorrow = day_weather.Day()
    tomorrow.score_forecast()
    tomorrow.rank_segments()
    choices, tone = rankings_interpreter(tomorrow.rankings)

    fname = f"dashboards/dashboard_{tomorrow.date.strftime('%d-%m-%y')}.jpg"
    produce_dashboard_image(tomorrow, choices, fname, to_show=False)

    tweet_templates = tweet_composer.get_tweet_templates("bots/tweet_content.yaml")
    tweet_text = tweet_composer.compose_tweet(choices, tone, tweet_templates)

    # Upload media
    media = api_obj.media_upload(fname)  # 5MB limit
    # Create a test tweet
    api_obj.update_status(status=tweet_text, media_ids=[media.media_id])


def tweet_your_weather(location):
    your_tomorrow = day_weather.Day(location=location)
    your_tomorrow.score_forecast()
    your_tomorrow.rank_segments()
    choices, tone = rankings_interpreter(your_tomorrow.rankings)

    fname = f"dashboards/test_dashboard_{your_tomorrow.date.strftime('%d-%m-%y')}.jpg"
    produce_dashboard_image(your_tomorrow, choices, fname, to_show=True)

    tweet_templates = tweet_composer.get_tweet_templates("bots/tweet_content.yaml")
    tweet_text = tweet_composer.compose_tweet(choices, tone, tweet_templates)
    # TODO finish this function


if __name__ == "__main__":

    # Create API object
    api = config.create_api()
    daily_tweet(api)

    # test_loc = {"Tokyo": (35.6974, 139.7946)}
    # tweet_your_weather(test_loc)
