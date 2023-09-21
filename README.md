# Podcast Summary App

This web application allows viewers to see information about recent podcast episodes. It includes a summary, guest details, and key moments. There are 3 example summaries as well as the option for users to get a summary of a podcast by submitting an RSS feed.

This is a simple project to demonstrate an AI application. It uses Open AI Whisper to do the audio transcription of the podcast, OpenAI gpt-3.5-turbo model to generate the summary, key moments, and guest information from the podcast, Modal to host cloud functions to do the processing, and Streamlit to provide a basic UI for people to interface with.

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
