#!/usr/bin/python

import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import tkinter as tk
from tkinter import filedialog
import subprocess
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

def browse_folder():
    folder_path = filedialog.askdirectory()
    entry_folder.delete(0, tk.END)
    entry_folder.insert(0, folder_path)


def execute_command():
    global script_dir 
    folder_path = entry_folder.get()
    title = entry_title.get()
    description = entry_description.get()
    keywords = entry_keywords.get()
    category = entry_category.get()
    privacy_status = entry_privacy_status.get()

    # Check if the folder exists and contains video files
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        video_files = [file for file in os.listdir(folder_path) if file.lower().endswith(('.mp4', '.avi', '.mov'))]
        if not video_files:
            output_text.insert(tk.END, "No video files found in the selected folder.")
            return

        # Loop through all video files in the folder and execute the command for each file
    i = 0
    j=1
    for video_file in video_files:
        if i == 6 :
           CLIENT_SECRETS_FILE = f"C:\\Users\\adamt\\Desktop\\Python-youtube-upload\\client_secrets{j}.json"
           j=j+1
           i=0
        else :
          video_path = os.path.join(folder_path, video_file)
          # Replace backslashes with forward slashes
          video_path = video_path.replace("\\", "/")
          cmd = f'python "{os.path.join(script_dir, "youtube-uploader.py")}" --file="{video_path}" --title="{title}" --description="{description}" --keywords="{keywords}" --category="{category}" --privacyStatus="{privacy_status}"'
          try:
              # Use subprocess.PIPE to capture the output
              result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
              # Extract the output
              output = result.stdout + result.stderr
              output_text.insert(tk.END, output)
          except Exception as e:
              output_text.insert(tk.END, str(e) + "\n")

    else:
        output_text.insert(tk.END, "Invalid folder path.")

# Create the main application window
root = tk.Tk()
root.title("YouTube Uploader")

# Input fields
label_folder = tk.Label(root, text="Video Folder:")
label_folder.pack()
entry_folder = tk.Entry(root, width=50)
entry_folder.pack()
btn_browse = tk.Button(root, text="Browse", command=browse_folder)
btn_browse.pack()

label_title = tk.Label(root, text="Title:")
label_title.pack()
entry_title = tk.Entry(root, width=50)
entry_title.pack()

label_description = tk.Label(root, text="Description:")
label_description.pack()
entry_description = tk.Entry(root, width=50)
entry_description.pack()

label_keywords = tk.Label(root, text="Keywords:")
label_keywords.pack()
entry_keywords = tk.Entry(root, width=50)
entry_keywords.pack()

label_category = tk.Label(root, text="Category:")
label_category.pack()
entry_category = tk.Entry(root, width=50)
entry_category.pack()

label_privacy_status = tk.Label(root, text="Privacy Status:")
label_privacy_status.pack()
entry_privacy_status = tk.Entry(root, width=50)
entry_privacy_status.pack()

# Execute Button
btn_execute = tk.Button(root, text="Execute", command=execute_command)
btn_execute.pack()

# Output Text Area
output_text = tk.Text(root, height=10, width=80)
output_text.pack()

root.mainloop()


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google API Console at
# https://console.cloud.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "C:\\Users\\adamt\\Desktop\\Python-youtube-upload\\client_secrets.json"

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, options):
  tags = None
  if options.keywords:
    tags = options.keywords.split(",")

  body=dict(
    snippet=dict(
      title=options.title,
      description=options.description,
      tags=tags,
      categoryId=options.category
    ),
    status=dict(
      privacyStatus=options.privacyStatus
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print ("Uploading file...")
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
          print ("Video id '%s' was successfully uploaded." % response['id'])
        else:
          exit("The upload failed with an unexpected response: %s" % response)
    except HttpError as e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print (error)
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print ("Sleeping %f seconds and then retrying..." % sleep_seconds)
      time.sleep(sleep_seconds)

if __name__ == '__main__':
  argparser.add_argument("--file", required=True, help="Video file to upload")
  argparser.add_argument("--title", help="Video title", default="Test Title")
  argparser.add_argument("--description", help="Video description",
    default="Test Description")
  argparser.add_argument("--category", default="22",
    help="Numeric video category. " +
      "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
  argparser.add_argument("--keywords", help="Video keywords, comma separated",
    default="")
  argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
    default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
  args = argparser.parse_args()

  if not os.path.exists(args.file):
    exit("Please specify a valid file using the --file= parameter.")

  youtube = get_authenticated_service(args)
  try:
    initialize_upload(youtube, args)
  except HttpError as e:
    print ("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))