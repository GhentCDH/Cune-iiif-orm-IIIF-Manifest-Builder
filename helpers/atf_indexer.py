import re
import io

from typing import TypedDict

from pyoracc.atf.common.atffile import AtfFile
from pyoracc.model.line import Line
from pyoracc.model.oraccobject import OraccObject
from pyoracc.model.oraccnamedobject import OraccNamedObject
from pyoracc.model.ruling import Ruling
from pyoracc.model.state import State
from pyoracc.model.translation import Translation

   
class AtfChar(TypedDict):
    text: str
    word_index: int
    char_index: int

class AtfIndexer():

    def __init__(self) -> None:
        self.atf_text: str|None = None
        self.atf: AtfFile|None = None
        self.char_index: dict[tuple, AtfChar] = {}
        pass

    def reset(self):
        self.char_index = {}
        self.atf = None
        self.atf_text = None

    def open(self, path: str, atftype: str = 'oracc'):
        self.reset()
        with io.open(path, encoding='utf-8') as f:
            self.atf_text = f.read()
            self.atf = AtfFile(self.atf_text, atftype, False)
            self._create_indexes()

    def set_text(self, text: str, atftype: str = 'oracc'):
        self.reset()
        self.atf_text = text
        self.atf = AtfFile(self.atf_text, atftype, False)
        self._create_indexes()

    def get_text(self) -> str|None:
        return self.atf_text
    
    def get_char_index(self) -> dict[tuple, AtfChar]:
        return self.char_index

    def get_char_info(self, surface: str, line: str, char_index: int) -> AtfChar|None:
        return self.char_index.get((surface, str(line), int(char_index)))

    def print_structure(self, object: OraccObject, level: int = 0):
        print(("  " * (level + 1)) + str(object.__class__.__name__) + (" " + str(object.objecttype) if hasattr(object, 'objecttype') else ""))

        if hasattr(object, 'children'):
            for child in object.children:
                self.print_structure(child, level + 1)

    def _create_indexes(self):
        if not self.atf:
            raise ValueError("ATF file not loaded")
        
        if not self.atf.text:
            raise ValueError("ATF text not found")
        
        self._parse_object(self.atf.text)

    def _parse_object(self, object: OraccObject):
        if not hasattr(object, 'children'):
            return
        
        # surface object? check for lines
        lines = [item for item in object.children
                if isinstance(item, Line)]
        if len(lines):
            return self._parse_tablet_surface(object)

        # parse subobjects
        objects = [item for item in object.children
                if isinstance(item, (OraccObject, OraccNamedObject))]        
        for object in objects:
            self._parse_object(object)

    def _parse_tablet_surface(self, object: OraccObject):
        # print("surface? " + str(object.__class__.__name__))
        for line in object.children:
            # print(str(line.__class__.__name__))
            if isinstance(line, Line):
                line_word_index = 0
                line_char_index = 0
                for word in line.words:
                    # print(word)
                    line_word_index += 1
                    chars = self._aft_split_word(word)
                    for char in chars:
                        line_char_index += 1
                        char_index_key = (object.objecttype, str(line.label), int(line_char_index))
                        char_info = { "text": char, "word_index": line_word_index, "char_index": line_char_index }
                        self.char_index[char_index_key] = AtfChar(**char_info)
            elif isinstance(line, Ruling):
                pass
            elif isinstance(line, State):
                pass
            elif isinstance(line, Translation):
                pass
            else:
                pass
                # print("Unknown line type: {}".format(type(line)))


    def _aft_split_word(self, atf_word: str) -> list[str]:

        reg_before_separator = r"([^.\[])[.-]+"
        reg_after_separator = r"[.-]+([^.\]])"

        reg_after = r"([>\]}\?;#/]+)"
        reg_before = r"([<\[{]+)"

        tmp = atf_word
        tmp = re.sub(reg_before_separator, "\\1 ", tmp)
        tmp = re.sub(reg_after_separator, " \\1", tmp)
        tmp = re.sub(reg_before, " \\1", tmp)
        tmp = re.sub(reg_after, "\\1 ", tmp)
        signs = [sign for sign in tmp.split(" ") if sign ]

        return signs