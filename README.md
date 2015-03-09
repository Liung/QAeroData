QAeroData
=========

本应用使用PyQt用来处理动态气动数据

QAeroData为一款作者（Liung）在建模研究中使用Python语言和Qt框架写成的多文档气动数据处理软件，软件中使用了成熟的科学计算工具包，包括Numpy，Scipy，Pandas及具有出版印刷质量的绘图库Matplotlib。本应用具有基本的数据读写、数据图像展示功能，集成了数据滤波功能、天平数据转换功能及一些小型工具集。
编写GUI应用界面的目的在于可以加快处理与分析气动数据，方便查看数据趋势，特别针对动态数据问题。可以极大减少前期数据处理工作，进而可以将精力投入到气动数据分析与流场拓扑分析上。最重要的是该应用还在不断的添加新的功能和模块，并最终成为一款优秀的气动数据处理软件。
图C. 1是QAeroData的主界面，主要包括三个组件：工作区、画图模块、文件导航模块。工作区支持多文档载入与操作；画图模块用来展示选定数据列的变化趋势；通过双击文件管理器中的能够识别的动态数据文件，可以快速的实现载入文件操作。
QAeroData程序的文件菜单包括文件、编辑、View、天平数据、动态机构数据、工具、窗口和关于菜单，还含有两个可以浮动的工具条。

[!QAeroData](https://github.com/Liung/QAeroData/blob/master/screenshots/QAeroData.png)

[!QAeroData_about](https://github.com/Liung/QAeroData/blob/master/screenshots/QAeroData_about.png)

在数字滤波器中，设计了Butterworth滤波器，用来将原始动态文件进行滤波处理。图C. 3中的左图是单文件滤波，主要用来调节滤波器的参数：滤波阶数与截止频率。当点击开始滤波之后，界面就会弹出各个通道的原始数据图和滤波之后的曲线分布（红色标示）。当该系列文件的参数确定之后，就可以使用批处理滤波工具进行滤波操作，方便快捷。

[!QAeroData_singlefilter](https://github.com/Liung/QAeroData/blob/master/screenshots/QAeroData_singlefilter.png)

[!QAeroData_batchfilter](https://github.com/Liung/QAeroData/blob/master/screenshots/QAeroData_batchfilter.png)

图C. 4是天平数据转换工具。包括左图的单文件转换与右图的多文件转换。针对不同的天平类型，需要载入相应的天平系数文件。图C. 5是18杆天平的系数载入界面，允许天平系数的后期校准调节，并保存修改后的天平系数。

[!QAeroData_singletranslate](https://github.com/Liung/QAeroData/blob/master/screenshots/QAeroData_singletranslate.png)

[!QAeroData_batchtranslate](https://github.com/Liung/QAeroData/blob/master/screenshots/QAeroData_batchtranslate.png)

[!QAeroData_balance_coe](https://github.com/Liung/QAeroData/blob/master/screenshots/QAeroData_balance_coe.png)

通过在一般天平数据处理的基础上进一步开发了动态数据处理程序，包括滤波、周期平均等处理。如图C. 6所示。

[!QAeroData_dynamic_data_translate](https://github.com/Liung/QAeroData/blob/master/screenshots/QAeroData_dynamic_data_translate.png)