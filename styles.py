def get_stylesheet(dark_mode=True):
    """Returns the appropriate stylesheet based on the mode (dark or light)."""
    
    if dark_mode:
        return {
            "background_style": """
                QWidget {
                    background-color: #21272A; /* Dark mode background */
                    color: #ffffff;
                }
            """,

            "button_style": """
                QPushButton {
                    border: 3px solid #C1C7CD;
                    border-radius: 15px;
                    padding: 5px;
                    color: #21272A;
                    background-color: #DDE1E6;
                }
                QPushButton:hover {
                    border: 3px solid #A2A9B0;
                    background-color: #C1C7CD;
                }
                QPushButton:pressed {

                    border: 3px solid #C1C7CD;
                    background-color: #C1C7CD;
                }
            """,

            "button_style_server": """
                QPushButton {
                    border: 3px solid #C1C7CD;
                    border-radius: 15px;
                    padding: 5px;
                    color: #21272A;
                    background-color: #DDE1E6;
                }
                QPushButton:hover {
                    background-color: #24A148;
                    border: 3px solid #198038;
                    color: #CCCCCC;
                }
                QPushButton:pressed {
                    background-color: #198038;
                    border: 3px solid #198038;
                    color: #CCCCCC;
                }
            """,

            "button_style_disconnect": """
                QPushButton {
                    border: 3px solid #C1C7CD;
                    border-radius: 15px;
                    padding: 5px;
                    color: #21272A;
                    background-color: #DDE1E6;
                }
                QPushButton:hover {
                    background-color: #DA1E28;
                    border: 3px solid #A2191F;
                    color: #CCCCCC;
                }
                QPushButton:pressed {
                    background-color: #A2191F;
                    border: 3px solid #A2191F;
                    color: #CCCCCC;
                }
            """,

            "button_style_inactive": """
                QPushButton {
                    border: 3px solid #4D5358;
                    border-radius: 15px;
                    padding: 5px;
                    color: #21272A;
                    background-color: #697077;
                }
                
            """,

            "button_small_style": """
                QPushButton {
                    border: 3px solid #A2191F;
                    border-radius: 15px;
                    padding: 5px 10px 5px 10px;
                    color: #FFFFFF;
                    background-color: #DA1E28;
                }
                QPushButton:hover {
                    border: 3px solid #750E13;
                    background-color: #A2191F;
                }
                QPushButton:pressed {
                    border: 3px solid #750E13;
                    background-color: #750e13;
                }
            """,

            "box_style": """
                QFrame {
                    border: 3px solid #0072C3;
                    padding: 5px 10px 5px 10px;
                    border-radius: 15px;
                    background-color: #1192E8;
                }
            """,

            "box_style_2": """
                QFrame {
                    border: none;
                    padding: 5px 10px 5px 10px;
                    border-radius: 15px;
                    background-color: #0072C3;
                }
            """,

            "box_style_3": """
                QFrame {
                    border: 3px solid #0072C3;;
                    border-radius: 15px;  /* Rounded corners */
                    color: #FFFFFF;
                    background-color: #1192E8;
                    padding: 5px 10px 5px 10px;
                }
            """,

            "label_style": """
                QLabel {
                    border: 3px solid #0072C3;  /* Red border */
                    border-radius: 15px;       /* Rounded edges */
                    padding: 5px 10px 5px 10px;
                }

                QLineEdit {
                    border: 3px solid #0072C3;;
                    border-radius: 15px;  /* Rounded corners */
                    color: #FFFFFF;
                    background-color: #1192E8;
                    padding: 5px 10px 5px 10px;
                }

                QLineEdit:hover {
                    border: 3px solid #00539A;;
                    border-radius: 15px;  /* Rounded corners */
                    color: #FFFFFF;
                    background-color: #0072C3;
                    padding: 5px 10px 5px 10px;
                }

                QLineEdit:focus {
                    color: #FFFFFF;
                    background-color: #061727;
                }
            """,

            "table_style": """
                QTableWidget {
                    border-radius: 15px;
                    border: none; /* Remove any direct border from the table itself */
                    background-color: #2B2B2B;      /* Table background color */
                    color: #FFFFFF;                /* Text color */
                    gridline-color: transparent;       /* Gridline color */
                    padding: 0px; /* Ensure no padding inside the table */
                }

                /* General Styling for Headers */
                QHeaderView::section {
                    background-color: transparent; /* Transparent header background */
                    color: #FFFFFF;                /* Header text color */
                    border: none;                  /* Remove border around header */
                    padding: 8px;                  /* Padding for header cells */
                }

                /* Horizontal Header Specific Styling */
                QHeaderView::section:horizontal {
                    background-color: #121619;     /* Horizontal header background */
                    color: #FFFFFF;                  /* Horizontal header text color */
                }

                /* Vertical Header Specific Styling */
                QHeaderView::section:vertical {
                    background-color: #171B1F;     /* Vertical header background */
                    color: #FFFFFF;                  /* Vertical header text color */
                    font-weight: bold;             /* Make vertical header text bold */
                }

                QTableView::item:selected {
                    background-color: #0072C3; /* Light orange background */
                    color: #FFFFFF; /* Black text */
                }
                
                QTableView {
                    selection-background-color: transparent; /* Removes default blue */
                    color: #FFFFFF; /* Black text */
                }

                QHeaderView::section:horizontal:last {
                    border-top-right-radius: 15px; /* Rounded corner for the last horizontal header cell */
                }

                /* Rounded corners */

                QHeaderView::section:vertical:last {
                    border-bottom-left-radius: 15px; /* Rounded corner for the last vertical header cell */
                }

                /* Corner Button Styling */
                QTableCornerButton::section {
                    background-color: #121619;     /* Corner button background color */
                    border: none;                  /* Remove border around the corner button */
                    border-top-left-radius: 15px;  /* Rounded corner for the top-left corner button */
                }

                /* QFrame Styling (Wrapping the Table) */
                QFrame {
                    border-radius: 15px;           /* Round corners of the frame wrapping the table */
                    background-color: #1D2226;     /* Frame background color */
                    border: none;     /* Transparent border for the frame */
                    padding: 0px; /* Ensure no internal padding */
                    margin: 0px;
                }
            """
        }
    
    else:  # Light mode
        return {
            "background_style": """
                QWidget {
                    background-color: #FCFDFF; /* Light mode background */
                    color: #121619;
                }
            """,
            

            "button_style": """
                QPushButton {
                    border: 3px solid #DDE1E6;
                    border-radius: 15px;
                    padding: 5px;
                    color: #121619;
                    background-color: #FFFFFF;
                }
                QPushButton:hover {
                    border: 3px solid #C1C7CD;
                    background-color: #DDE1E6;
                }
                QPushButton:pressed {

                    border: 3px solid #DDE1E6;
                    background-color: #DDE1E6;
                }
            """,

            "button_style_server": """
                QPushButton {
                    border: 3px solid #DDE1E6;
                    border-radius: 15px;
                    padding: 5px;
                    color: #121619;
                    background-color: #FFFFFF;
                }
                QPushButton:hover {
                    background-color: #6FDC8C;
                    border: 3px solid #42BE65;
                    color: #F2F4F8;
                }
                QPushButton:pressed {
                    background-color: #6FDC8C;
                    border: 3px solid #6FDC8C;
                    color: #F2F4F8;
                }
            """,

            "button_style_disconnect": """
                QPushButton {
                    border: 3px solid #DDE1E6;
                    border-radius: 15px;
                    padding: 5px;
                    color: #121619;
                    background-color: #FFFFFF;
                }
                QPushButton:hover {
                    background-color: #FA4D56;
                    border: 3px solid #DA1E28;
                    color: #F2F4F8;
                }
                QPushButton:pressed {
                    background-color: #FA4D56;
                    border: 3px solid #FA4D56;
                    color: #F2F4F8;
                }
            """,

            "button_style_inactive": """
                QPushButton {
                    border: 3px solid #A2A9B0;
                    border-radius: 15px;
                    padding: 5px;
                    color: #F2F4F8;
                    background-color: #C1C7CD;
                }
                
            """,

            "button_small_style": """
                QPushButton {
                    border: 3px solid #DA1E28;
                    border-radius: 15px;
                    padding: 5px 10px 5px 10px;
                    color: #FFFFFF;
                    background-color: #FA4D56;
                }
                QPushButton:hover {
                    border: 3px solid #FA4D56;
                    background-color: #DA1E28;
                }
                QPushButton:pressed {
                    border: 3px solid #DA1E28;
                    background-color: #DA1E28;
                }
            """,

            "box_style": """
                QFrame {
                    border: 3px solid #F2F4F8;
                    padding: 5px 10px 5px 10px;
                    border-radius: 15px;
                    background-color: #1192E8;
                }
            """,

            "box_style_2": """
                QFrame {
                    border: none;
                    padding: 5px 10px 5px 10px;
                    border-radius: 15px;
                    background-color: #1192E8;
                    color: #F2F4F8;
                }
            """,

            "box_style_3": """
                QFrame {
                    border: 3px solid #1192E8;;
                    border-radius: 15px;  /* Rounded corners */
                    color: #F2F4F8;
                    background-color: #33B1FF;
                    padding: 5px 10px 5px 10px;
                }
            """,

            "label_style": """
                QLabel {
                    border: 3px solid #0072C3;  /* Red border */
                    border-radius: 15px;       /* Rounded edges */
                    padding: 5px 10px 5px 10px;
                }

                QLineEdit {
                    border: 3px solid #1192E8;;
                    border-radius: 15px;  /* Rounded corners */
                    color: #FFFFFF;
                    background-color: #33B1FF;
                    padding: 5px 10px 5px 10px;
                }

                QLineEdit:hover {
                    border: 3px solid #33B1FF;;
                    border-radius: 15px;  /* Rounded corners */
                    color: #FFFFFF;
                    background-color: #1192E8;
                    padding: 5px 10px 5px 10px;
                }

                QLineEdit:focus {
                    color: #121619;
                    background-color: #E5F6FF;
                }
            """,

            "table_style": """
                QTableWidget {
                    border-radius: 15px;
                    border: none; /* Remove any direct border from the table itself */
                    background-color: #2B2B2B;      /* Table background color */
                    color: #121619;                /* Text color */
                    gridline-color: transparent;       /* Gridline color */
                    padding: 0px; /* Ensure no padding inside the table */
                }

                /* General Styling for Headers */
                QHeaderView::section {
                    background-color: transparent; /* Transparent header background */
                    color: #121619;                /* Header text color */
                    border: none;                  /* Remove border around header */
                    padding: 8px;                  /* Padding for header cells */
                }

                /* Horizontal Header Specific Styling */
                QHeaderView::section:horizontal {
                    background-color: #C1C7CD;     /* Horizontal header background */
                    color: #121619;                  /* Horizontal header text color */
                }

                /* Vertical Header Specific Styling */
                QHeaderView::section:vertical {
                    background-color: #DDE1E6;     /* Vertical header background */
                    color: #121619;                  /* Vertical header text color */
                    font-weight: bold;             /* Make vertical header text bold */
                }

                QTableView::item:selected {
                    background-color: #1192E8; /* Light orange background */
                    color: #F2F4F8; /* Black text */
                }
                
                QTableView {
                    selection-background-color: transparent; /* Removes default blue */
                    color: #121619; /* Black text */
                }

                QHeaderView::section:horizontal:last {
                    border-top-right-radius: 15px; /* Rounded corner for the last horizontal header cell */
                }

                /* Rounded corners */

                QHeaderView::section:vertical:last {
                    border-bottom-left-radius: 15px; /* Rounded corner for the last vertical header cell */
                }

                /* Corner Button Styling */
                QTableCornerButton::section {
                    background-color: #C1C7CD;     /* Corner button background color */
                    border: none;                  /* Remove border around the corner button */
                    border-top-left-radius: 15px;  /* Rounded corner for the top-left corner button */
                }

                /* QFrame Styling (Wrapping the Table) */
                QFrame {
                    border-radius: 15px;           /* Round corners of the frame wrapping the table */
                    background-color: #F2F4F8;     /* Frame background color */
                    border: none;     /* Transparent border for the frame */
                    padding: 0px; /* Ensure no internal padding */
                    margin: 0px;
                }
            """
        }