import streamlit as st
import modal
import json
import os


def main():
    st.title("Podcast Summaries")

    if "podcasts" not in st.session_state:
        available_podcast_info = create_dict_from_json_files(".")
        st.session_state.podcasts = available_podcast_info

    if "podcast_names" not in st.session_state:
        st.session_state.podcast_names = list(available_podcast_info.keys())

    # Left section - Input fields
    st.sidebar.header("Choose a Podcast")

    # Dropdown box
    st.sidebar.subheader("Available Podcasts Feeds")
    selected_podcast = st.sidebar.selectbox(
        "Select a Podcast",
        options=st.session_state.podcast_names,
        placeholder="Select a Podcast",
        key="selectedPodcast",
        label_visibility="collapsed",
    )

    if selected_podcast:
        podcast_info = st.session_state.podcasts[selected_podcast]

        # Display the podcast title
        st.subheader("Episode Title")
        st.write(podcast_info["podcast_details"]["episode_title"])

        # Display the podcast summary and the cover image in a side-by-side layout
        col1, col2 = st.columns([7, 3])

        with col1:
            # Display the podcast episode summary
            st.subheader("Podcast Episode Summary")
            st.write(podcast_info["podcast_summary"])

        with col2:
            st.image(
                podcast_info["podcast_details"]["episode_image"],
                caption="Podcast Cover",
                width=300,
                use_column_width=True,
            )

        # Display the podcast guest and their details in a side-by-side layout
        col3, col4 = st.columns([3, 7])

        with col3:
            st.subheader("Podcast Guest")
            st.write(podcast_info["podcast_guest"]["name"])

        with col4:
            st.subheader("Podcast Guest Details")
            st.write(podcast_info["podcast_guest"]["summary"])

        # Display the five key moments
        st.subheader("Key Moments")
        key_moments = podcast_info["podcast_highlights"]
        for moment in key_moments.split("\n"):
            st.markdown(
                f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True
            )

    # User Input box
    st.sidebar.subheader("Add New Podcast Feed")
    url = st.sidebar.text_input("Link to RSS Feed")

    process_button = st.sidebar.button("Add Podcast Feed")
    st.sidebar.markdown("**Note**: Podcast processing can take up to 5 mins.")

    if process_button:
        st.toast("Processing new podcast")
        # Call the function to process the URLs and retrieve podcast guest information
        podcast_info = process_podcast_info(url)
        st.balloons()

        # add new podcast to dropdown
        name = podcast_info["podcast_details"]["podcast_title"]
        st.session_state.podcast_names = [name] + st.session_state.podcast_names
        st.session_state.podcasts[name] = podcast_info

        st.experimental_rerun()


def create_dict_from_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    data_dict = {}

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "r") as file:
            podcast_info = json.load(file)
            podcast_name = podcast_info["podcast_details"]["podcast_title"]
            data_dict[podcast_name] = podcast_info

    return data_dict


# Get previous podcasts from Streamlit cache
def create_dict_from_cache():
    data_dict = {}
    podcasts = st.session_state.podcasts

    for p in podcasts.values():
        st.write(p)
        podcast_name = p["podcast_details"]["podcast_title"]
        data_dict[podcast_name] = p

    return data_dict

@st.cache_data
def process_podcast_info(url):
    f = modal.Function.lookup("podcast-summarizer-project", "process_podcast")
    output = f.remote(url, "/content/podcast/")
    return output


if __name__ == "__main__":
    main()
