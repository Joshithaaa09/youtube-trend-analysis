import streamlit as st
import os
import gc
import time
import yaml

from tqdm import tqdm
from brightdata_scrapper import *

from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import FileReadTool


docs_tool = FileReadTool()


@st.cache_resource
def load_llm():
    llm = LLM(
        model="ollama/llama3.2:1b",
        base_url="http://localhost:11434"
    )

    return llm


# ===========================
# Define Agents & Tasks
# ===========================

def create_agents_and_tasks():
    """Creates a Crew for analysis of the channel scraped output."""

    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    analysis_agent = Agent(
        role=config["agents"][0]["role"],
        goal=config["agents"][0]["goal"],
        backstory=config["agents"][0]["backstory"],
        verbose=True,
        tools=[docs_tool],
        llm=load_llm()
    )

    response_synthesizer_agent = Agent(
        role=config["agents"][1]["role"],
        goal=config["agents"][1]["goal"],
        backstory=config["agents"][1]["backstory"],
        verbose=True,
        llm=load_llm()
    )

    analysis_task = Task(
        description=config["tasks"][0]["description"],
        expected_output=config["tasks"][0]["expected_output"],
        agent=analysis_agent
    )

    response_task = Task(
        description=config["tasks"][1]["description"],
        expected_output=config["tasks"][1]["expected_output"],
        agent=response_synthesizer_agent
    )

    crew = Crew(
        agents=[analysis_agent, response_synthesizer_agent],
        tasks=[analysis_task, response_task],
        process=Process.sequential,
        verbose=True
    )

    return crew


# ===========================
# Streamlit Setup
# ===========================

st.title("YouTube Trend Analysis")
st.caption("Powered by CrewAI, Streamlit, and Ollama")


if "messages" not in st.session_state:
    st.session_state.messages = []

if "response" not in st.session_state:
    st.session_state.response = None

if "crew" not in st.session_state:
    st.session_state.crew = None


def reset_chat():
    st.session_state.messages = []
    gc.collect()


def start_analysis():
    with st.spinner("Scraping videos... This may take a moment."):

        status_container = st.empty()

        status_container.info("Extracting videos from the channels...")

        channel_snapshot_id = trigger_scraping_channels(
            st.session_state.youtube_channels,
            10,
            st.session_state.start_date,
            st.session_state.end_date,
            "Latest",
            ""
        )

        status = get_progress(
            channel_snapshot_id["snapshot_id"]
        )

        while status["status"] != "ready":

            status_container.info(
                f"Current status: {status['status']}"
            )

            time.sleep(10)

            status = get_progress(
                channel_snapshot_id["snapshot_id"]
            )

            if status["status"] == "failed":
                status_container.error(
                    f"Scraping failed: {status}"
                )
                return

        if status["status"] == "ready":

            status_container.success(
                "Scraping completed successfully!"
            )

            channel_scrapped_output = get_output(
                status["snapshot_id"],
                format="json"
            )

            st.markdown("## YouTube Videos Extracted")

            carousel_container = st.container()

            videos_per_row = 3

            with carousel_container:

                num_videos = len(channel_scrapped_output[0])

                num_rows = (
                    num_videos + videos_per_row - 1
                ) // videos_per_row

                for row in range(num_rows):

                    cols = st.columns(videos_per_row)

                    for col_idx in range(videos_per_row):

                        video_idx = (
                            row * videos_per_row
                            + col_idx
                        )

                        if video_idx < num_videos:

                            with cols[col_idx]:

                                st.video(
                                    channel_scrapped_output[0][video_idx]["url"]
                                )

            status_container.info(
                "Processing transcripts..."
            )

            st.session_state.all_files = []

            for i in tqdm(
                range(len(channel_scrapped_output[0]))
            ):

                youtube_video_id = (
                    channel_scrapped_output[0][i]["shortcode"]
                )

                file = (
                    "transcripts/"
                    + youtube_video_id
                    + ".txt"
                )

                st.session_state.all_files.append(file)

                os.makedirs("transcripts", exist_ok=True)

                with open(file, "w", encoding="utf-8") as f:

                    for j in range(
                        len(
                            channel_scrapped_output[0][i][
                                "formatted_transcript"
                            ]
                        )
                    ):

                        text = (
                            channel_scrapped_output[0][i][
                                "formatted_transcript"
                            ][j]["text"]
                        )

                        start_time = (
                            channel_scrapped_output[0][i][
                                "formatted_transcript"
                            ][j]["start_time"]
                        )

                        end_time = (
                            channel_scrapped_output[0][i][
                                "formatted_transcript"
                            ][j]["end_time"]
                        )

                        f.write(
                            f"({start_time:.2f}-{end_time:.2f}): "
                            f"{text}\n"
                        )

            st.session_state.channel_scrapped_output = (
                channel_scrapped_output
            )

            status_container.success(
                "Scraping complete! "
                "We shall now analyze the videos and report trends..."
            )

        else:

            status_container.error(
                f"Scraping failed with status: {status}"
            )

    if status["status"] == "ready":

        status_container = st.empty()

        with st.spinner(
            "The agent is analyzing the videos... This may take a moment."
        ):

            st.session_state.crew = (
                create_agents_and_tasks()
            )

            st.session_state.response = (
                st.session_state.crew.kickoff(
                    inputs={
                        "file_paths": ", ".join(
                            st.session_state.all_files
                        )
                    }
                )
            )


# ===========================
# Sidebar
# ===========================

with st.sidebar:

    st.header("YouTube Channels")

    if "youtube_channels" not in st.session_state:
        st.session_state.youtube_channels = [""]

    def add_channel_field():
        st.session_state.youtube_channels.append("")

    for i, channel in enumerate(
        st.session_state.youtube_channels
    ):

        col1, col2 = st.columns([6, 1])

        with col1:

            st.session_state.youtube_channels[i] = (
                st.text_input(
                    "Channel URL",
                    value=channel,
                    key=f"channel_{i}",
                    label_visibility="collapsed"
                )
            )

        with col2:

            if i > 0:

                if st.button(
                    "Remove",
                    key=f"remove_{i}"
                ):

                    st.session_state.youtube_channels.pop(i)
                    st.rerun()

    st.button(
        "Add Channel",
        on_click=add_channel_field
    )

    st.divider()

    st.subheader("Date Range")

    col1, col2 = st.columns(2)

    with col1:

        start_date = st.date_input("Start Date")

        st.session_state.start_date = (
            start_date.strftime("%Y-%m-%d")
        )

    with col2:

        end_date = st.date_input("End Date")

        st.session_state.end_date = (
            end_date.strftime("%Y-%m-%d")
        )

    st.divider()

    st.button(
        "Start Analysis",
        type="primary",
        on_click=start_analysis
    )


# ===========================
# Main Chat Interface
# ===========================

if st.session_state.response:

    with st.spinner(
        "Generating content... This may take a moment."
    ):

        try:

            result = st.session_state.response

            st.markdown("### Generated Analysis")

            st.markdown(result)

            st.download_button(
                label="Download Content",
                data=result.raw,
                file_name="youtube_trend_analysis.md",
                mime="text/markdown"
            )

        except Exception as e:

            st.error(
                f"An error occurred: {str(e)}"
            )


# ===========================
# Footer
# ===========================

st.markdown("---")

st.markdown(
    "Built with CrewAI, Streamlit, and Ollama"
)
