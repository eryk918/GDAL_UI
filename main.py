# -*- coding: utf-8 -*-
import sys

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import QApplication

from UI.main_window import MainWindowDialog

main_app = QApplication(sys.argv)
main_app.setStyle('Fusion')

main_dlg = MainWindowDialog()
main_dlg.show_dialog()

main_app.exec()

# xpoints = np.array([150, 187])
#
# plt.plot(xpoints)
# plt.show()
