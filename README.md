# Python Flask Email Thread Microservice

This microservice is designed to process email threads (with string inputs) to provide two primary transformations:

trimmed - represents the email with header information, signature information, and duplicate subject information removed.

cleansed - the trimmed message, but with all "troublesome" tokens removed so that they can be processed using Watson Knowledge Studio


## API Endpoint

/api/pre_process_email

requires object:
{
  "source_id": "<some id>",
  "source_email": "<email body text>"
}

pre-processing library assumes standard format that has been seen to date with Hartford Outlook forwarded emails.

## Run the app locally

1. [Install Python][]
1. cd into this project's root directory
1. Run `pip install -r requirements.txt` to install the app's dependencies
1. Run `python email_pre_processing_microservice.py`
1. Access the running app in a browser at <http://localhost:5000>

[Install Python]: https://www.python.org/downloads/

To test this application *using python 2*:

1. Run the app locally (see instructions below)
2. Run python test_microservice.py

Note: there is further testing to be done on utf-8 characters and their conversion.
Currently, the test file contains ASCII characters only.
