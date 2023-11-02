import plotly.graph_objects as go
import requests
import threading

class UiComponentException(Exception):
    pass

class GoIndicator:

    def __init__(self,**kwargs):
        self.config = kwargs
        self.fig = self.get_figure()
        self.thread = None
        self.freq = None

    def get_figure(self):
        return go.Figure(go.Indicator(**self.config))

    def start_polling(self,source,freq,parser=lambda x:x,replace=True):
        if self.thread != None and not replace:
            raise UiComponentException("polling is already started")
        if self.freq <= 0:
            raise UiComponentException("update frequency must be stricly positive")
        def updater(self):
            if self.freq == None:
                return
            if callable(self.source):
                parse(self.source())
            elif type(self.source) is str:
                res = requests.get(self.source)
                self.config["value"] = parser(res.text)
            else:
                raise UiComponentException("source is not callable or URL")
            time.sleep(self.freq)
        self.freq = freq
        self.thread = threading.Thread(target=lambda:updater(self))
        self.thread.start()

    def stop_polling(self,ignore=True):
        if self.thread == None and not ignore:
            raise UiComponentException("polling was not started")
        self.freq = None
        self.thread.join()

    def set_value(self,value):
        self.config["value"] = value

    def get_value(self):
        return self.config["value"]

if __name__ == "__main__":

    import unittest

    class TestIndicator(unittest.TestCase):

        def test_indicator(self):
            fig = fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 0,
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {'axis':{'range':[0,100]}},
                title = {'text': "Test"}))
            self.assertTrue(fig!=None)

    unittest.main()