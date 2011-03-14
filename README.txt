
Experimental remote monitoring and control system for Repraps/Repstraps/3d scanners. 
It includes a Web client (using Javascript + Jquery + WebGl) and server (pure Python ):

//////////////////////////////

Depencies:
* For now only tested with python 2.6
* You will need to have pySerial installed
* By default , the web server is now set to use wsgiref (no external dependency required) : to change that , just change the ServerType in the config.cfg file in the "WebServer" section
to any other web server supported by Bottle (preferably Tornado for now)

For more info 
please see the wiki pages at http://github.com/kaosat-dev/Doboz/wiki/Doboz-web

//////////////////////////////
Doboz-web : Licensed under the GPL license
© 2011 by Mark "Ckaos" Moissette 