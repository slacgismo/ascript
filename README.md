# ASCRIPT - Advanced Smart Charting Infrastructure Planning Tool

To setup, do the following:

~~~
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install pip --upgrade -r requirements.txt
mkdir .venv/src
cd .venv/src
git clone https://github.com/slacgismo/speech --depth 1
python3 -m pip install speech
cd -
~~~

To run the scenario UI, do the following:

~~~
cd Task6
marimo run scenario.py
~~~
