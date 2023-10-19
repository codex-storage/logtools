"""Ad-hoc script which tags uploads with a sequential number."""
import sys

uploading = False
upload_no = 0
for line in sys.stdin:
    if 'Handling file upload' in line:
        upload_no += 1
        uploading = True

    if uploading:
        line = line.strip()
        line = line.rsplit(' ', maxsplit=1)
        line = ' '.join([line[0], f'upload={upload_no}', line[1]])
        print(line)

    if 'Uploaded file' in line:
        uploading = False
