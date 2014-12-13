#coding: UTF-8
from __future__ import division
import numpy as np
from scipy.signal import butter, filtfilt
import sys
sys.path.append("D:/Users/LC/GitHub/QAeroData/")
from widget.matplotlibWidget import MatplotlibWidget

__author__ = 'Vincent'


class DataFilter(object):
    """
    定义一个滤波器，用来对实验数据进行滤波处理
        system sampling rate        系统采样率
        cut-off fre                 低通滤波器截止频率
        filter order                滤波阶数
    """
    def __init__(self, samplingRate=1000., filterOrder=5, cutoffFre=4.):
        self._samplingRate = samplingRate
        self._filterOrder = filterOrder
        self._cutoffFre = cutoffFre

        self._fileFre = None
        self._rawFile = None
        self._filtFile = None
        self._headerRows = None

        self._forceStartCol = 6
        self._forceEndCol = 11

    def setFileFre(self, fre):
        self._fileFre = fre

    def setCutoffFreRatio(self, ratio):
        self._cutoffFre = self._fileFre * ratio

    def setRawFile(self, rawFile):
        self._rawFile = rawFile

    def setFiltFile(self, filtFile):
        self._filtFile = filtFile

    def setHeaderRows(self, headerRows=1):
        self._headerRows = headerRows

    def setForceStartCol(self, forceStartCol):
        self._forceStartCol = forceStartCol

    def setForceEndCol(self, forceEndCol):
        self._forceEndCol = forceEndCol

    def filt(self):
        """butter 指令來設計一個 Butterworth 低通濾波器，其格式如下：
                    [b, a] = butter(order, Wn, function)
        對於輸入參數，說明如下：
                order 是濾波器的階數，階數越大，濾波效果越好，但是計算量也會跟著變大。所產生的濾波器參數 a 和 b 的長度，等於 order+1。
                Wn 是正規化的截止頻率，介於 0 和 1 之間，當取樣頻率是 fs 時，所能處理的最高頻率是 fs/2，所以如果實際的截止頻率是 f = 1000，
            那麼 Wn = f/(fs/2)。
                function 是一個字串，function = 'low' 代表是低通濾波器，function = 'high' 代表是高通濾波器。

        scipy.signal.butter(N, Wn, btype='low', analog=False, output='ba')
            Butterworth digital and analog filter design.

            Design an Nth order digital or analog Butterworth filter and return the filter coefficients in (B,A) or
            (Z,P,K) form.

            Parameters :
                N : int
                    The order of the filter.
                Wn : array_like
                    A scalar or length-2 sequence giving the critical frequencies. For a Butterworth filter, this is the
                     point at which the gain drops to 1/sqrt(2) that of the passband (the “-3 dB point”). For digital
                     filters, Wn is normalized from 0 to 1, where 1 is the Nyquist frequency, pi radians/sample.
                     Wn is thus in half-cycles / sample.)
                     For analog filters, Wn is an angular frequency (e.g. rad/s).
                btype : {‘lowpass’, ‘highpass’, ‘bandpass’, ‘bandstop’}, optional
                    The type of filter. Default is ‘lowpass’.
                analog : bool, optional
                    When True, return an analog filter, otherwise a digital filter is returned.
                output : {‘ba’, ‘zpk’}, optional
                Type of output: numerator/denominator (‘ba’) or pole-zero (‘zpk’). Default is ‘ba’.
            Returns :
                b, a : ndarray, ndarray
                    Numerator (b) and denominator (a) polynomials of the IIR filter. Only returned if output='ba'.
                z, p, k : ndarray, ndarray, float
                    Zeros, poles, and system gain of the IIR filter transfer function. Only returned if output='zpk'.

        scipy.signal.filtfilt(b, a, x, axis=-1, padtype='odd', padlen=None)
            A forward-backward filter.

            This function applies a linear filter twice, once forward and once backwards. The combined filter has linear
            phase.

            Before applying the filter, the function can pad the data along the given axis in one of three ways: odd,
            even or constant. The odd and even extensions have the corresponding symmetry about the end point of the
            data.
            The constant extension extends the data with the values at end points. On both the forward and backwards
            passes,
            the initial condition of the filter is found by using lfilter_zi and scaling it by the end point of the
            extended data.

            Parameters :
                b : (N,) array_like
                    The numerator coefficient vector of the filter.
                a : (N,) array_like
                    The denominator coefficient vector of the filter. If a[0] is not 1, then both a and b are
                    normalized by a[0].
                x : array_like
                    The array of data to be filtered.
                axis : int, optional
                    The axis of x to which the filter is applied. Default is -1.
                padtype : str or None, optional
                    Must be ‘odd’, ‘even’, ‘constant’, or None. This determines the type of extension to use for the
                    padded signal to which the filter is applied. If padtype is None, no padding is used. The default
                    is ‘odd’.
                padlen : int or None, optional
                    The number of elements by which to extend x at both ends of axis before applying the filter. This
                    value must be less than x.shape[axis]-1. padlen=0 implies no padding. The default value is
                    3*max(len(a),len(b)).
            Returns :
                y : ndarray
                    The filtered output, an array of type numpy.float64 with the same shape as x."""
        fileName = self._rawFile
        headerNums = self._headerRows
        rawData = np.loadtxt(fileName, skiprows=headerNums)
        b, a = butter(self._filterOrder, self._cutoffFre/(self._samplingRate/2.), btype='low')
        filterData = np.zeros_like(rawData)

        for i in xrange(rawData.shape[1]):
            if self._forceStartCol - 1 <= i < self._forceEndCol:    # 只对力和力矩进行滤波处理，角度列不进行滤波
                filterData[:, i] = filtfilt(b, a, rawData[:, i])
            else:
                filterData[:, i] = rawData[:, i]

        return filterData

    def toDataFile(self):

        rawFileName = self._rawFile
        filterFileName = self._filtFile
        headerNums = self._headerRows

        filterData = self.filt()
        # read the raw file's headers
        headerLines = []
        with open(rawFileName, 'r') as f1:
            for i in range(headerNums):
                headerLines.append(f1.readline())

        # write filt data to filter file
        np.savetxt(filterFileName, filterData,
                   fmt="%-10.8f", header='\n'.join(headerLines),
                   comments='')

        # with open(filterFileName, 'w') as f2:
        #     f2.writelines(headerLines)
        #     m, n = filterData.shape
        #     for i in xrange(m):
        #         for j in xrange(n):
        #             f2.write("%-10.8f\t" % filterData[i, j])
        #         f2.write("\n")
        return True

    def showWidget(self, parent):

        rawData = np.loadtxt(self._rawFile, skiprows=self._headerRows)
        filterData = self.filt()

        mpl1 = MatplotlibWidget(parent)
        ax1 = mpl1.canvas.fig.add_subplot(111)
        ax1.plot(rawData[:, 5])
        ax1.plot(filterData[:, 5], 'r')
        ax1.set_xlabel('t/s')
        ax1.set_ylabel('Cx')

        mpl2 = MatplotlibWidget(parent)
        ax2 = mpl2.canvas.fig.add_subplot(111)
        ax2.plot(rawData[:, 6])
        ax2.plot(filterData[:, 6], 'r')
        ax2.set_xlabel('t/s')
        ax2.set_ylabel('Cy')

        mpl3 = MatplotlibWidget(parent)
        ax3 = mpl3.canvas.fig.add_subplot(111)
        ax3.plot(rawData[:, 7])
        ax3.plot(filterData[:, 7], 'r')
        ax3.set_xlabel('t/s')
        ax3.set_ylabel('Cz')

        mpl4 = MatplotlibWidget(parent)
        ax4 = mpl4.canvas.fig.add_subplot(111)
        ax4.plot(rawData[:, 8])
        ax4.plot(filterData[:, 8], 'r')
        ax4.set_xlabel('t/s')
        ax4.set_ylabel('Cmx')

        mpl5 = MatplotlibWidget(parent)
        ax5 = mpl5.canvas.fig.add_subplot(111)
        ax5.plot(rawData[:, 9])
        ax5.plot(filterData[:, 9], 'r')
        ax5.set_xlabel('t/s')
        ax5.set_ylabel('Cmy')

        mpl6 = MatplotlibWidget(parent)
        ax6 = mpl6.canvas.fig.add_subplot(111)
        ax6.plot(rawData[:, 10])
        ax6.plot(filterData[:, 10], 'r')
        ax6.set_xlabel('t/s')
        ax6.set_ylabel('Cmz')

        return mpl1, mpl2, mpl3, mpl4, mpl5, mpl6

