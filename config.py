import sys

token = 'ODg1MDY4MjMwNzgyMjUxMDE4.YThqBQ.62odci-MNAGgfNUK5J3brR2uHKI'
apikey = 'RGAPI-17945210-150d-4d68-b8de-09aac59b5f1f'
is_dev = True
if '-dev' not in sys.argv:
    is_dev = False
    apikey = 'RGAPI-17945210-150d-4d68-b8de-09aac59b5f1f'
    token = 'ODgzMzAxNDI4OTI2NTA5MDc3.YTH8jw.tkaKsWYwqscVDMAE-oc-G8Z2dcg'