# sockettool
Share any data in any size and any format through ip and port technology on same network 
you can replace any mp3 music by alarm.mp3 just remember ro rename it to alarm.mp3 
## Installation
 `git clone https://github.com/Farzinkh/sockettool.git`
 
 `pip install -r requirements.txt`
## Usage
you can use graphical version or non graphical version as you wish 
for useing graphical version just run 

`python sockettool\Hotspot.py` in the project directory

and for useing non graphical version run 

`python sockettool\Hotspot_terminal.py`

also you can make executable versions by pyinstaller 

`pip install auto-py-to-exe` and run `auto-py-to-exe`
### Docker Usage
#### you can use this tool to update docker image to new image
At first you need an python image for example python=3.7.9

`docker pull python:3.7.9` => optional

then follow the instruction :

1>`docker run -it  -p 65432:65432 --name update image bash`

2>`git clone https://github.com/Farzinkh/sockettool`

3>`cd sockettool`

4>`pip install -r requirements.txt`

5>`python Hotspot_terminal.py s`
 
 downloaded file will be accessible in Data folder move it to whereever you want

 6>`exit`

 7>`docker commit update new_image_name`

 Enjoy :)