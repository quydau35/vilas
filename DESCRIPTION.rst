Need software
1. Python version >= 2.7
sudo apt-get install python python-setuptools python-dev python-augeas python-opengl python-imaging python-pyrex python-pyside.qtopengl python-qt4 python-qt4-gl python-lxml

2. Gromacs version >= 4.6
sudo apt-get install gromacs

3. Openbabel
sudo apt-get install openbabel
or 
sudo pip insatall openbabel

4. Avogadro for python
sudo apt-get install avogadro

5. Pymol
sudo apt-get install pymol

6. Xmgrace
sudo apt-get install grace


How to install labpi in Ubuntu
1. Install pip
sudo apt-get install python-pip
2. Install Labpi
sudo pip install labpi


*** If you get error while installing, maybe it lacks some below packages

** Error when install Cython:
sudo apt-get install cython
or
sudo pip install cython

** Missing openGL:
sudo apt-get install build-essential
sudo apt-get install freeglut3-dev

** Missing pygame:
sudo apt-get install python-pygame
or
sudo pip install hg+http://bitbucket.org/pygame/pygame

** Missing some package
sudo apt-get installgcc swig dialog

sudo apt-get install -y python-pip build-essential libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev

sudo apt-get install libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0

sudo apt-get install xmlsec1 openssl libxmlsec1 libxmlsec1-dev

sudo apt-get install build-essential autoconf libtool pkg-config  idle-python2.7 qt4-dev-tools qt4-designer libqtgui4 libqtcore4 libqt4-xml libqt4-test libqt4-script libqt4-network libqt4-dbus libgle3