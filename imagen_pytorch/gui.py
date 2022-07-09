from dataclasses import dataclass



@dataclass
class GUI:
    pbar: object # streamlit.DeltaGenerator
    canvases: list # list[streamlit.DeltaGenerator]
