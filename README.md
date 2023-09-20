# Podcast Summary App

This web application allows viewers to see summaries of podcast episodes. There are 3 example summaries as well as the option for users to get a summary of a podcast by submitting an RSS feed. Podcast sumaries are created by transcribing audio to text using OpenAI Whisper and then summarizing using the Open AI gpt-3.5-turbo model.

This app was built as part of the course [Building AI Products with OpenAI](https://uplimit.com/course/building-ai-products-with-openai).

## Deployment

### Backend

The backend is deployed to [Modal](https://modal.com/). [Link to Modal docs](https://modal.com/docs/guide).
For first time Modal users, see [setup instructions](https://modal.com/docs/guide) to create an account, install modal cli, and setup a modal token locally.

To test changes, use `modal run podcast_backend.py`.

To deploy changes, use `modal deploy podcast_backend.py`

### Fronted

The frontend is written using [Streamlit](https://streamlit.io/).
[Deployment instructions are here](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app).

## Misc

[ListenNotes](https://www.listennotes.com/) useful for getting podcast RSS feeds.
