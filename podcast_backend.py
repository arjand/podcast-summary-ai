import modal


def download_whisper():
    # Load the Whisper model
    import os
    import whisper

    print("Download the Whisper model")

    # Perform download only once and save to Container storage
    whisper._download(whisper._MODELS["medium"], "/content/podcast/", False)


stub = modal.Stub("podcast-summarizer-project")
podcast_modal_image = (
    modal.Image.debian_slim()
    .pip_install(
        "feedparser",
        "https://github.com/openai/whisper/archive/9f70a352f9f8630ab3aa0d06af5cb9532bd8c21d.tar.gz",
        "requests",
        "ffmpeg",
        "openai",
        "tiktoken",
        "wikipedia",
        "ffmpeg-python",
    )
    .apt_install("ffmpeg")
    .run_function(download_whisper)
)


@stub.function(image=podcast_modal_image, gpu="any", timeout=600)
def get_transcribe_podcast(rss_url, local_path):
    # Read from the RSS Feed URL
    import feedparser

    rss_feed = feedparser.parse(rss_url)
    podcast_title = rss_feed["feed"]["title"]
    episode_title = rss_feed.entries[0]["title"]
    episode_image = rss_feed["feed"]["image"].href

    for item in rss_feed.entries[0].links:
        if item["type"] == "audio/mpeg":
            episode_url = item.href
    episode_name = "podcast_episode.mp3"
    print("RSS URL read and episode URL: ", episode_url)

    # Download the podcast episode by parsing the RSS feed
    from pathlib import Path

    p = Path(local_path)
    p.mkdir(exist_ok=True)

    import requests

    with requests.get(episode_url, stream=True) as r:
        r.raise_for_status()
        episode_path = p.joinpath(episode_name)
        with open(episode_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    import os
    import whisper

    # Load the Whisper model from saved location
    model = whisper.load_model(
        "medium", device="cuda", download_root="/content/podcast/"
    )

    # Perform the podcast transcription
    result = model.transcribe(local_path + episode_name)

    # Return the transcribed text
    output = {}
    output["podcast_title"] = podcast_title
    output["episode_title"] = episode_title
    output["episode_image"] = episode_image
    output["episode_transcript"] = result["text"]
    return output


@stub.function(
    image=podcast_modal_image, secret=modal.Secret.from_name("my-openai-secret")
)
def get_podcast_summary(podcast_transcript):
    import openai

    instructPrompt = """
  You are an expert copywriter who is good at summarizing content to make readers interested in reading the full content.
  Please write a summary of this podcast making sure to cover the important topics of the podcast. Please keep it concise. The transcript of the podcast is provided below.
  """

    request = instructPrompt + podcast_transcript

    chat_output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": request},
        ],
    )
    podcastSummary = chat_output.choices[0].message.content
    return podcastSummary


@stub.function(
    image=podcast_modal_image, secret=modal.Secret.from_name("my-openai-secret")
)
def get_podcast_guest(podcast_transcript):
    import openai
    import wikipedia
    import json

    output = {}

    request = podcast_transcript[:5000]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": request}],
        functions=[
            {
                "name": "get_podcast_guest_information",
                "description": "Get information on the podcast guest using their full name and the name of the organization they are part of to search for them on Wikipedia or Google",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "guest_name": {
                            "type": "string",
                            "description": "The full name of the guest who is speaking in the podcast",
                        },
                        "guest_organization": {
                            "type": "string",
                            "description": "The full name of the organization that the podcast guest belongs to or runs",
                        },
                        "guest_title": {
                            "type": "string",
                            "description": "The title, designation or role of the podcast guest in their organization",
                        },
                    },
                    "required": ["guest_name"],
                },
            }
        ],
        function_call={"name": "get_podcast_guest_information"},
    )

    podcast_guest = ""
    podcast_guest_org = ""
    podcast_guest_title = ""
    response_message = completion["choices"][0]["message"]
    if response_message.get("function_call"):
        function_args = json.loads(response_message["function_call"]["arguments"])
        podcast_guest = function_args.get("guest_name")
        podcast_guest_org = function_args.get("guest_organization")
        podcast_guest_title = function_args.get("guest_title")

    if podcast_guest_org is None:
        podcast_guest_org = ""
    if podcast_guest_title is None:
        podcast_guest_title = ""

    try:
        guest_summary_wiki = wikipedia.page(
            podcast_guest + " " + podcast_guest_org + " " + podcast_guest_title,
            auto_suggest=True,
        )
        guest_summary = guest_summary_wiki.summary
    except (wikipedia.PageError, wikipedia.DisambiguationError) as e:
        guest_summary = "No guest information available."

    output["name"] = podcast_guest
    output["summary"] = (
        podcast_guest_title + " " + podcast_guest_org + " " + guest_summary
    )

    return output


@stub.function(
    image=podcast_modal_image, secret=modal.Secret.from_name("my-openai-secret")
)
def get_podcast_highlights(podcast_transcript):
    import openai

    instruct_prompt = """
  You are an expert copywriter and marketer. Make a list of key moments, interesting insights, controversial opinions, and critical questions from the podcast.
  From this list, pick only 3 that are the most attention grabbing and write them below. Discard the rest.
  Please keep it concise. The transcript of the podcast is provided below.
  """

    request = instruct_prompt + podcast_transcript
    chat_output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": request},
        ],
    )
    podcast_highlights = chat_output.choices[0].message.content
    return podcast_highlights


@stub.function(
    image=podcast_modal_image,
    secret=modal.Secret.from_name("my-openai-secret"),
    timeout=1200,
)
def process_podcast(url, path):
    output = {}
    podcast_details = get_transcribe_podcast.remote(url, path)
    podcast_summary = get_podcast_summary.remote(podcast_details["episode_transcript"])
    podcast_guest = get_podcast_guest.remote(podcast_details["episode_transcript"])
    podcast_highlights = get_podcast_highlights.remote(
        podcast_details["episode_transcript"]
    )
    output["podcast_details"] = podcast_details
    output["podcast_summary"] = podcast_summary
    output["podcast_guest"] = podcast_guest
    output["podcast_highlights"] = podcast_highlights
    return output


@stub.local_entrypoint()
def test_method(url, path):
    podcast_details = get_transcribe_podcast.remote(url, path)
    print(
        "Podcast Summary: ",
        get_podcast_summary.remote(podcast_details["episode_transcript"]),
    )
    print(
        "Podcast Guest Information: ",
        get_podcast_guest.remote(podcast_details["episode_transcript"]),
    )
    print(
        "Podcast Highlights: ",
        get_podcast_highlights.remote(podcast_details["episode_transcript"]),
    )
