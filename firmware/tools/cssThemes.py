class CSSThemes:
    def __init__(self):
        pass

    def orange_theme(self):
        stylesheet = '''QWidget#simulationView{
background-color:#FF9F1C;
color:#FFFFFF;
}

QWidget#mainWindow{
background-color:#FF9F1C;
color:#FFFFFF;
}

QWidget{
color:#FFFFFF;
	font: 25 10pt "Mont ExtraLight DEMO";
border-width:3px;
}

QPushButton{
display:inline-block;
padding:0.35em 1.2em;
border:0.1em solid #FFFFFF;
margin:0 0.3em 0.3em 0;
border-radius:0.12em;box-sizing: border-box;
text-decoration:none;
font-family:'Roboto',sans-serif;
font-weight:300;
color:#0B0B0B;
text-align:center;
transition: all 0.2s;
background-color:#FFFFFF ;
}

QPushButton::hover{
color:#0B0B0B;
background-color:#CBF3F0;
}

QPushButton::pressed{
background-color:#2EC4B6;
color:#000000;
}
}'''
        return stylesheet
