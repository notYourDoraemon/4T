def check_terminal_size(term, min_width=50, min_height=15):
    """Check if terminal meets minimum size requirements"""
    return term.width >= min_width and term.height >= min_height

def center_text(term, text):
    """Center text on the terminal"""
    return term.center(text)
