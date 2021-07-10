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

`python sockettool\Hotspot_terminal.py -h`

there are two folder in the project directory which are "SEND" & "DATA" what ever you want to send just put it in "SEND" directory
and what ever you download will be found in "DATA" directory

also you can make executable versions by pyinstaller 

`pip install auto-py-to-exe` and run `auto-py-to-exe`
## Example for non graphical version
in receiver part run :

`python sockettool\Hotspot_terminal.py s`

read the server ip and port and keep them in mind

and in sender part place a file or files and run this:

`python sockettool\Hotspot_terminal.py c -ip <reciver ip> -p <server port>`

and wait for finish you can always cancel it by `ctrl+C

### Android Usage

for running this project an android devices you need to install some aplicatons and follow this steps:

1. install [Termux](https://play.google.com/store/apps/details?id=com.termux)

2. install [port forwarder](https://play.google.com/store/apps/details?id=com.elixsr.portforwarder)

3. install python in termux:

- `pkg install python`

4. go to your your internal storage directory

- `cd storage/shared`

5. create a folder and cd to it

6. download project

- `git clone https://github.com/Farzinkh/sockettool`

7. install packages

- `pip install tqdm==4.59.0 psutil==5.8.0`

8. port forwarding when ever you want to send or recive a file run server side script on other device

- `python sockettool\Hotspot_terminal.py s`

- and keep in mind ip and port and insert them in portforwarding aplication in android device then run sender side in termux

- `python sockettool\Hotspot_terminal.py c -ip <reciver ip> -p <server port>`

### Docker Usage
#### you can use this tool to update docker image to new image
At first you need an python image for example python=3.7.9

`docker pull python:3.7.9` => optional

then follow the instruction :

1. `docker run -it  -p 65432:65432 --name update image bash`

2. `git clone https://github.com/Farzinkh/sockettool`

3. `cd sockettool`

4. `pip install -r requirements.txt`

5. `python Hotspot_terminal.py s -p 65432`
 
 - downloaded file will be accessible in Data folder move it to whereever you want

6. `exit`

7. `docker commit update new_image_name`

 *Enjoy :)*

 You can find me on [![Twitter][1.2]][1], or on [![LinkedIn][3.2]][3].

<!-- Icons -->

[1.2]: http://i.imgur.com/wWzX9uB.png (twitter icon without padding)
[2.2]: https://raw.githubusercontent.com/MartinHeinz/MartinHeinz/master/linkedin-3-16.png (LinkedIn icon without padding)

<!-- Links to your social media accounts -->

[1]: https://twitter.com/FarzinKhodavei1
[2]: https://www.linkedin.com/in/farzin-khodaveisi-84288a18a/