#coding=utf-8 
from array import array 
from math import sin, cos 
import numpy as np 
from PyQt4.QtGui import * 
from PyQt4.QtCore import Qt 
from guiqwt.plot import PlotManager, CurvePlot 
from guiqwt.builder import make 
  
PLOT_DEFINE = [[u"sin1f",u"cos1f"],[u"sin3f",u"cos3f"],[u"sin合成",u"cos合成"]] 
COLORS = ["blue", "red"] 
DT = 0.001 
  
def get_peak_data(x, y, x0, x1, n, rate): 
    if len(x) == 0: 
        return [0], [0] 
    x = np.frombuffer(x) 
    y = np.frombuffer(y) 
    index0 = int(x0*rate) 
    index1 = int(x1*rate) 
    step = (index1 - index0) // n 
    if step == 0: 
        step = 1 
    index1 += 2 * step 
    if index0 < 0: 
        index0 = 0 
    if index1 > len(x) - 1: 
        index1 = len(x) - 1 
    x = x[index0:index1+1] 
    y = y[index0:index1+1] 
    y = y[:len(y)//step*step] 
    yy = y.reshape(-1, step) 
    index = np.c_[np.argmin(yy, axis=1), np.argmax(yy, axis=1)] 
    index.sort(axis=1) 
    index += np.arange(0, len(y), step).reshape(-1, 1) 
    index = index.reshape(-1) 
    return x[index], y[index] 
  
class RealtimeDemo(QWidget): 
    def __init__(self): 
        super(RealtimeDemo, self).__init__() 
        self.setWindowTitle(u"Realtime Demo") 
  
        self.data = {u"t":array("d")} 
        for name in sum(PLOT_DEFINE, []): 
            self.data[name] = array("d") 
  
        self.curves = {} 
        self.t = 0 
        vbox = QVBoxLayout() 
        vbox.addWidget(self.setup_toolbar()) 
        self.manager = PlotManager(self) 
        self.plots = [] 
        for i, define in enumerate(PLOT_DEFINE): 
            plot = CurvePlot() 
            plot.axisScaleDraw(CurvePlot.Y_LEFT).setMinimumExtent(60) 
            self.manager.add_plot(plot) 
            self.plots.append(plot) 
            plot.plot_id = id(plot) 
            for j, curve_name in enumerate(define): 
                curve = self.curves[curve_name] = make.curve([0], [0], color=COLORS[j], title=curve_name) 
                plot.add_item(curve) 
            plot.add_item(make.legend("BL")) 
            vbox.addWidget(plot) 
        self.manager.register_standard_tools() 
        self.manager.get_default_tool().activate() 
        self.manager.synchronize_axis(CurvePlot.X_BOTTOM, self.manager.plots.keys()) 
        self.setLayout(vbox) 
        self.startTimer(100) 
  
    def setup_toolbar(self): 
        toolbar = QToolBar() 
        self.auto_yrange_checkbox = QCheckBox(u"Y轴自动调节") 
        self.auto_xrange_checkbox = QCheckBox(u"X轴自动调节") 
        self.xrange_box = QSpinBox() 
        self.xrange_box.setMinimum(5) 
        self.xrange_box.setMaximum(50) 
        self.xrange_box.setValue(10) 
        self.auto_xrange_checkbox.setChecked(True) 
        self.auto_yrange_checkbox.setChecked(True) 
        toolbar.addWidget(self.auto_yrange_checkbox) 
        toolbar.addWidget(self.auto_xrange_checkbox) 
        toolbar.addWidget(self.xrange_box) 
        return toolbar 
  
    def timerEvent(self, event): 
        for i in xrange(100): 
            t = self.t 
            self.data[u"t"].append(t) 
            self.data[u"sin1f"].append(sin(t)) 
            self.data[u"cos1f"].append(cos(t)) 
            self.data[u"sin3f"].append(sin(3*t)/6) 
            self.data[u"cos3f"].append(cos(3*t)/6) 
            self.data[u"sin合成"].append(sin(t)+sin(3*t)/6) 
            self.data[u"cos合成"].append(cos(t)+cos(3*t)/6) 
            self.t += DT 
  
        if self.auto_xrange_checkbox.isChecked(): 
            xmax = self.data["t"][-1] 
            xmin = max(xmax - self.xrange_box.value(), 0) 
        else: 
            xmin, xmax = self.plots[0].get_axis_limits('bottom') 
  
        for key, curve in self.curves.iteritems(): 
            xdata = self.data["t"] 
            ydata = self.data[key] 
            x, y = get_peak_data(xdata, ydata, xmin, xmax, 600, 1/DT) 
            curve.set_data(x, y) 
  
        for plot in self.plots: 
            if self.auto_yrange_checkbox.isChecked() and self.auto_xrange_checkbox.isChecked(): 
                plot.do_autoscale() 
            elif self.auto_xrange_checkbox.isChecked(): 
                plot.set_axis_limits("bottom", xmin, xmax) 
                plot.replot() 
            else: 
                plot.replot() 
  
def main(): 
    import sys 
    app = QApplication(sys.argv) 
    form = RealtimeDemo() 
    form.show() 
    sys.exit(app.exec_()) 
  
if __name__ == '__main__': 
    main()
