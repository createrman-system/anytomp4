# anytomp4
Python script for encoding/decoding any file to mp4
---
## You will need to install the dependencies
><br/> pip install opencv-python numpy
---
# To encode any file in cmd.exe:
><br/><code>python coder.py encode FILENAME.xxx FILENAME.mp4</code>
<br/>Where .xxx is the extension of your file, which is located in the same folder as coder.py
---
# To decode a video file:
><br/><code>python coder.py decode FILENAME.mp4</code>
---
## Encryption key
><br/>You can create a file in the folder with coder.py <code>key.txt</code> and write an encryption key of any length inside it. After that, the code will take into account the presence of key.txt when encoding files, and in the future, such video files will only decode correctly with the correct key specified in key.txt.

