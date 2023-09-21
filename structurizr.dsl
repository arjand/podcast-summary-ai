workspace {

    model {
        user = person "User" "Interesed in seeing podcast summaries"
        softwareSystem = softwareSystem "Podcast AI Summarizer" {
            streamlit = container "Streamlit app" "Provides framework for python data apps" "Python and React"
            modal = container "Modal" "Provides cloud compute infrastructure and does podcast transcription" "Python"
        }
        openai = softwareSystem "Open AI" "Provides APIs to ChatGPT 3.5 Turbo"
        wikipedia = softwareSystem "Wikipedia" "Provides background information on podcast guests"
        
        #relationships
        user -> softwareSystem "Views summaries of podcasts"
        
        # relationships to/from containers
        user -> streamlit "Views and requests podcast summaries"
        streamlit -> modal "Gets podcast transcription and summary"
        modal -> openai "Gets podcast summary and guests from transcript"
        modal -> wikipedia "Gets background info on a person"
    }    
    
    views {
        systemContext softwareSystem {
            include *
            autolayout
        }
        
        container softwareSystem "Containers" {
            include *
            animation {
                streamlit
                modal
                openai
            }
            autoLayout
            description "hi"
        }

        theme default
    }
    
}