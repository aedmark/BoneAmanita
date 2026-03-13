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
        self.interp = tkinter.Tcl()
        self._load_tcl_spells()

    def _load_tcl_spells(self):
        tcl_script = """
        proc apply_entropy {text chi voltage} {
            set words [split $text " "]
            set out_words {}
            foreach word $words {
                set len [string length $word]
                # Typoglycemia (Scrambling inner letters under extreme chaos)
                if {$chi > 0.85 && $len > 4 && rand() < ($chi / 3.0)} {
                    set first [string index $word 0]
                    set last [string index $word [expr {$len - 1}]]
                    set mid [string range $word 1 [expr {$len - 2}]]
                    set mid_rev [string reverse $mid]
                    lappend out_words "${first}${mid_rev}${last}"
                # Cellular division (splitting words)
                } elseif {$chi > 0.6 && $len > 4 && rand() < ($chi / 2.0)} {
                    set mid [expr {$len / 2}]
                    set part1 [string range $word 0 [expr {$mid - 1}]]
                    set part2 [string range $word $mid end]
                    lappend out_words "${part1}·${part2}"
                # Voltage Arc (random capitalization)
                } elseif {$voltage > 80.0 && rand() < 0.1} {
                    lappend out_words [string toupper $word]
                } else {
                    lappend out_words $word
                }
            }
            return [join $out_words " "]
        }

        proc apply_void {text psi} {
            set words [split $text " "]
            set out_words {}
            foreach word $words {
                # If proximity to the Void is high, memories get redacted
                if {$psi > 0.5 && [string length $word] > 3 && rand() < ($psi / 2.5)} {
                    lappend out_words "████"
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
                # Protect short words like 'fish', 'relic', and 'apply' from being stripped
                if {[string length $word] > 5 && [regexp {(?i).*(ous|ful|ic|ish|ly)[.,!?]*$} $word]} {
                    # Fluff detected, do not append
                } else {
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

    def consume_by_void(self, text: str, psi: float) -> str:
        """ Redacts random words if the system is drifting too close to abstraction. """
        try:
            return self.interp.call('apply_void', text, psi)
        except tkinter.TclError as e:
            from bone_types import Prisma
            print(f"{Prisma.VIOLET}[TCL VOID FRACTURE]: {e}{Prisma.RST}")
            return text