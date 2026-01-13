import sys
import os

# Принудительная настройка для корректной работы matplotlib с PyQt6
os.environ["QT_API"] = "pyqt6"

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QLabel, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QCompleter, QFrame, QPushButton, QFileDialog)
from PyQt6.QtCore import Qt

# --- Стилизация интерфейса (Dark Mode) ---
DARK_STYLE = """
    QMainWindow { background-color: #0f0f12; }
    QWidget { background-color: #16161a; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    QFrame#Card { 
        background-color: #1f1f24; 
        border: 1px solid #333; 
        border-radius: 12px; 
    }
    QLineEdit { 
        background-color: #2a2a30; border: 1px solid #444; 
        padding: 8px; border-radius: 6px; color: white; font-size: 14px;
    }
    QPushButton {
        background-color: #bb86fc; color: #000; font-weight: bold;
        border-radius: 6px; padding: 10px; border: none;
    }
    QPushButton:hover { background-color: #d7b7fd; }
    QTableWidget { 
        background-color: #16161a; gridline-color: #333; border: none;
    }
    QHeaderView::section { 
        background-color: #25252b; color: #ff79c6; padding: 8px; border: none;
    }
"""

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(width, height), dpi=dpi)
        self.fig.patch.set_facecolor('#1f1f24')
        self.ax.set_facecolor('#1f1f24')
        super().__init__(self.fig)

class AnalyticsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Financial Efficiency Analyzer")
        self.resize(1280, 900)
        self.setStyleSheet(DARK_STYLE)
        
        self.data_df = self.load_data()
        self.init_ui()

    def load_data(self):
        path = r"D:/konfer/2025/export_dataset.csv"
        if os.path.exists(path):
            try:
                df = pd.read_csv(path, encoding='utf-8')
            except:
                df = pd.read_csv(path, encoding='cp1251')
            df['name'] = df['name'].astype(str).str.strip()
            df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)
            df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
            df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0)
            return df
        return pd.DataFrame()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # --- ЛЕВАЯ ПАНЕЛЬ ---
        side_panel = QVBoxLayout()
        
        ctrl_card = QFrame()
        ctrl_card.setObjectName("Card")
        ctrl_layout = QVBoxLayout(ctrl_card)
        
        # Выбор фирмы
        ctrl_layout.addWidget(QLabel("COMPANY NAME"))
        self.search_input = QLineEdit()
        if not self.data_df.empty:
            completer = QCompleter(sorted(self.data_df['name'].unique().tolist()))
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.search_input.setCompleter(completer)
        ctrl_layout.addWidget(self.search_input)
        
        # Выбор интервала
        ctrl_layout.addSpacing(15)
        ctrl_layout.addWidget(QLabel("YEAR RANGE (FROM - TO)"))
        range_box = QHBoxLayout()
        self.year_from = QLineEdit("2008")
        self.year_to = QLineEdit("2025")
        range_box.addWidget(self.year_from)
        range_box.addWidget(self.year_to)
        ctrl_layout.addLayout(range_box)
        
        # Кнопки
        ctrl_layout.addSpacing(20)
        self.btn_calc = QPushButton("CALCULATE")
        self.btn_calc.clicked.connect(self.update_analytics)
        ctrl_layout.addWidget(self.btn_calc)
        
        self.btn_pdf = QPushButton("EXPORT TO PDF")
        self.btn_pdf.clicked.connect(self.export_to_pdf)
        ctrl_layout.addWidget(self.btn_pdf)
        
        side_panel.addWidget(ctrl_card)
        side_panel.addStretch()
        
        # --- ПРАВАЯ ПАНЕЛЬ ---
        content_panel = QVBoxLayout()
        self.company_title = QLabel("Company: Not Selected")
        self.company_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #ff79c6;")
        content_panel.addWidget(self.company_title)

        self.canvas = MplCanvas(self)
        content_panel.addWidget(self.canvas)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["YEAR PAIR", "N (COSTS Δ)", "M (EFFICIENCY)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        content_panel.addWidget(self.table)

        layout.addLayout(side_panel, 1)
        layout.addLayout(content_panel, 3)

    def get_analysis_data(self):
        firm = self.search_input.text().strip()
        try:
            y_start = int(self.year_from.text())
            y_end = int(self.year_to.text())
        except:
            return None, []

        df = self.data_df[(self.data_df['name'] == firm) & 
                          (self.data_df['year'] >= y_start) & 
                          (self.data_df['year'] <= y_end)].sort_values('year')
        
        if df.empty: return firm, []

        results = []
        year_map = df.set_index('year').to_dict('index')
        sorted_years = sorted(year_map.keys())

        for i in range(len(sorted_years) - 1):
            y1, y2 = sorted_years[i], sorted_years[i+1]
            p, c = year_map[y1], year_map[y2]
            n = (c['sales'] - c['profit']) - (p['sales'] - p['profit'])
            m = (c['sales'] - p['sales']) / n if n != 0 else 0
            results.append((f"{y1}-{y2}", n, m))
        return firm, results

    def update_analytics(self):
        firm, results = self.get_analysis_data()
        if not results:
            self.company_title.setText(f"No data for {firm}")
            return

        self.company_title.setText(f"Company: {firm}")
        self.table.setRowCount(len(results))
        for i, (y, n, m) in enumerate(results):
            self.table.setItem(i, 0, QTableWidgetItem(y))
            self.table.setItem(i, 1, QTableWidgetItem(f"{n:,.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{m:.4f}"))

        self.canvas.ax.clear()
        n_pts = [x[1] for x in results]
        m_pts = [x[2] for x in results]
        self.canvas.ax.plot(n_pts, m_pts, marker='o', color='#ff79c6')
        for i, txt in enumerate([x[0] for x in results]):
            self.canvas.ax.annotate(txt, (n_pts[i], m_pts[i]), color='white', fontsize=8)
        self.canvas.ax.set_title(f"Efficiency Path: {firm}")
        self.canvas.draw()

    def export_to_pdf(self):
        firm, results = self.get_analysis_data()
        if not results: return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"{firm}_report.pdf", "PDF Files (*.pdf)")
        if file_path:
            # Временное переключение на светлую тему для печати, если нужно, 
            # но здесь сохраним текущий вид графика
            self.canvas.fig.savefig(file_path, format='pdf', bbox_inches='tight')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalyticsApp()
    window.show()
    sys.exit(app.exec())
