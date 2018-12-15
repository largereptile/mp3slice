# mp3slice
cuts up long mp3s of albums or something into mp3s of predefined length


## Usage

### Arguments
* --meta: path to metadata file with correct formatting (check example.txt)
* --local: path to mp3 file to cut up
* --url: publicly available url to download and cut up
* --cover: path to image to use as cover art in mp3 metadata

### Example
```
python3 slice.py --url https://harru.club/example.mp3 --meta example.txt --cover /home/harru/images/cover.jpg
```
