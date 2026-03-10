"""bone_tcl.py - The Homoiconic Weaver"""

import tkinter


class TheTclWeaver:
    """
    An embedded Tcl interpreter acting as a homoiconic string mutator.
    It takes the concept 'Everything Is A String' literally.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = TheTclWeaver()
        return cls._instance

    def __init__(self):
        # Instantiate a raw, headless Tcl interpreter (no GUI attached)
        self.interp = tkinter.Tcl()
        self._load_tcl_spells()

    def _load_tcl_spells(self):
        tcl_script = """
        proc apply_entropy {text chi voltage} {
            set words [split $text " "]
            set out_words {}
            foreach word $words {
                if {$chi > 0.7 && [string length $word] > 4 && rand() < ($chi / 2.0)} {
                    set mid [expr {[string length $word] / 2}]
                    set part1 [string range $word 0 $mid-1]
                    set part2 [string range $word $mid end]
                    lappend out_words "${part1}·${part2}"
                } elseif {$voltage > 80.0 && rand() < 0.1} {
                    lappend out_words [string toupper $word]
                } else {
                    lappend out_words $word
                }
            }
            return [join $out_words " "]
        }
        proc semantic_echo {text} {
            set words [split $text " "]
            if {[llength $words] == 0} { return $text }
            set last_word [lindex $words end]
            # Strip punctuation for the echo
            set clean_last [regsub -all {[^a-zA-Z0-9]} $last_word ""]
            if {[string length $clean_last] > 0} {
                return "$text... [string tolower $clean_last]..."
            }
            return "$text..."
        }
        proc strip_fluff {text} {
            set words [split $text " "]
            set out_words {}
            foreach word $words {
                # Strip words ending in typical adjective suffixes (ous, ful, ic, ish, ly)
                if {![regexp {(?i).*(ous|ful|ic|ish|ly)[.,!?]*$} $word]} {
                    lappend out_words $word
                }
            }
            return [join $out_words " "]
        }
        """
        self.interp.eval(tcl_script)

    def deform_reality(self, text: str, chi: float, voltage: float) -> str:
        try:
            return self.interp.call('apply_entropy', text, chi, voltage)
        except tkinter.TclError as e:
            from bone_types import Prisma
            print(f"{Prisma.RED}[TCL ENGINE FRACTURE]: {e}{Prisma.RST}")
            return text

    def haunt_string(self, text: str) -> str:
        try:
            return self.interp.call('semantic_echo', text)
        except tkinter.TclError:
            return text

    def quantum_comb(self, text: str) -> str:
        try:
            return self.interp.call('strip_fluff', text)
        except tkinter.TclError as e:
            from bone_types import Prisma
            print(f"{Prisma.RED}[TCL CRASH]: {e}{Prisma.RST}")
            return text