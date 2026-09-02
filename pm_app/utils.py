import datetime
import tkinter as tk


# Accessibility/theme flag
HIGH_CONTRAST = False


def set_high_contrast(flag: bool):
    global HIGH_CONTRAST
    HIGH_CONTRAST = bool(flag)


def get_theme():
    if HIGH_CONTRAST:
        return {
            'accent': '#ffff00',
            'bg': '#000000',
            'card_bg': '#000000',
            'fg': '#ffffff',
        }
    else:
        return {
            'accent': '#06b6d4',
            'bg': '#0f1724',
            'card_bg': '#111827',
            'fg': '#e6eef6',
        }


def parse_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return None


def center_window(win, width=None, height=None, parent=None):
    """Center a window. If width/height provided, set geometry accordingly; otherwise use current size."""
    try:
        if parent is None:
            # prefer a provided root-like object; fall back to win if it is a Tk instance
            if hasattr(win, 'winfo_screenwidth'):
                p = win
            else:
                p = getattr(win, 'master', None)
        else:
            p = parent
        if p is not None:
            p.update_idletasks()
        screen_w = p.winfo_screenwidth()
        screen_h = p.winfo_screenheight()
        if width is None or height is None:
            win.update_idletasks()
            w = win.winfo_width()
            h = win.winfo_height()
        else:
            w = width
            h = height
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")
    except Exception:
        pass


class RoundedButton:
    """A simple rounded-corner button implemented on a Canvas.
    Provides `pack`, `grid`, and `place` proxies so it can be used like a widget.
    """
    def __init__(self, master, text, command=None, width=120, height=36, radius=10, bg='#06b6d4', fg='white', font=None):
        self.master = master
        self._cmd = command
        self.width = width
        self.height = height
        self.radius = radius
        self.bg = bg
        self.fg = fg
        self.font = font or ('Helvetica Neue', 12, 'bold')

        self.canvas = tk.Canvas(master, width=width, height=height, highlightthickness=0, bd=0, bg=master.cget('background'))
        # make focusable for keyboard navigation
        try:
            self.canvas.configure(takefocus=1)
        except Exception:
            pass
        self._has_focus = False
        self._is_hover = False
        self._draw()
        self.canvas.tag_bind('btn', '<Button-1>', lambda e: self._on_click())
        self.canvas.tag_bind('btn', '<Enter>', lambda e: self._on_hover(True))
        self.canvas.tag_bind('btn', '<Leave>', lambda e: self._on_hover(False))
        self.canvas.bind('<FocusIn>', lambda e: self._set_focus(True))
        self.canvas.bind('<FocusOut>', lambda e: self._set_focus(False))
        self.canvas.bind('<Key-Return>', lambda e: self._on_click())
        self.canvas.bind('<Key-space>', lambda e: self._on_click())

    def _on_hover(self, entering: bool):
        self._is_hover = bool(entering)
        try:
            if self._is_hover:
                self.canvas.config(cursor='hand2')
            else:
                self.canvas.config(cursor='')
        except Exception:
            pass
        self._draw()

    def _set_focus(self, val: bool):
        self._has_focus = bool(val)
        self._draw()

    def _draw(self):
        self.canvas.delete('all')
        w = self.width
        h = self.height
        r = min(self.radius, h//2, w//2)
        # Rounded rectangle: draw center rect and four arcs
        self.canvas.create_rectangle(r, 0, w-r, h, outline=self.bg, fill=self.bg, tags=('btn',))
        self.canvas.create_rectangle(0, r, w, h-r, outline=self.bg, fill=self.bg, tags=('btn',))
        self.canvas.create_oval(0, 0, 2*r, 2*r, outline=self.bg, fill=self.bg, tags=('btn',))
        self.canvas.create_oval(w-2*r, 0, w, 2*r, outline=self.bg, fill=self.bg, tags=('btn',))
        self.canvas.create_oval(0, h-2*r, 2*r, h, outline=self.bg, fill=self.bg, tags=('btn',))
        self.canvas.create_oval(w-2*r, h-2*r, w, h, outline=self.bg, fill=self.bg, tags=('btn',))
        # hovered/dim effect
        fill_color = self.bg
        if self._is_hover:
            # slightly darker on hover
            fill_color = self._darker(self.bg, 0.9)
        # draw shapes with fill_color
        self.canvas.create_rectangle(r, 0, w-r, h, outline=fill_color, fill=fill_color, tags=('btn',))
        self.canvas.create_rectangle(0, r, w, h-r, outline=fill_color, fill=fill_color, tags=('btn',))
        self.canvas.create_oval(0, 0, 2*r, 2*r, outline=fill_color, fill=fill_color, tags=('btn',))
        self.canvas.create_oval(w-2*r, 0, w, 2*r, outline=fill_color, fill=fill_color, tags=('btn',))
        self.canvas.create_oval(0, h-2*r, 2*r, h, outline=fill_color, fill=fill_color, tags=('btn',))
        self.canvas.create_oval(w-2*r, h-2*r, w, h, outline=fill_color, fill=fill_color, tags=('btn',))
        self.canvas.create_text(w//2, h//2, text=str(self._get_text()), fill=self.fg, font=self.font, tags=('btn',))
        # focus outline
        if self._has_focus:
            try:
                self.canvas.create_rectangle(2, 2, w-2, h-2, outline='#ffff80', width=2, tags=('focus',))
            except Exception:
                pass

    def _darker(self, hexcol, factor=0.9):
        try:
            hexcol = hexcol.lstrip('#')
            r = int(hexcol[0:2], 16)
            g = int(hexcol[2:4], 16)
            b = int(hexcol[4:6], 16)
            r = max(0, int(r * factor))
            g = max(0, int(g * factor))
            b = max(0, int(b * factor))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hexcol

    def _get_text(self):
        return getattr(self, '_text', '')

    def _on_click(self):
        if callable(self._cmd):
            try:
                self._cmd()
            except Exception:
                pass

    # proxy geometry methods
    def pack(self, *args, **kwargs):
        return self.canvas.pack(*args, **kwargs)

    def grid(self, *args, **kwargs):
        return self.canvas.grid(*args, **kwargs)

    def place(self, *args, **kwargs):
        return self.canvas.place(*args, **kwargs)

    def config(self, **kwargs):
        # allow updating text, bg, fg
        if 'text' in kwargs:
            self._text = kwargs.pop('text')
        if 'bg' in kwargs:
            self.bg = kwargs.pop('bg')
        if 'fg' in kwargs:
            self.fg = kwargs.pop('fg')
        if 'font' in kwargs:
            self.font = kwargs.pop('font')
        self._draw()

    def destroy(self):
        return self.canvas.destroy()

