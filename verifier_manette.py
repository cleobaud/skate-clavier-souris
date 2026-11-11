"""Verifie VRAIMENT que la manette virtuelle marche.

Pas de test sur du texte : on cree une manette et on demande a Windows,
par l'API XInput, s'il la voit. Code de sortie 0 = oui, 1 = non.
"""
import ctypes
import sys
import time
from ctypes import wintypes


class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [("wButtons", wintypes.WORD),
                ("bLeftTrigger", ctypes.c_ubyte), ("bRightTrigger", ctypes.c_ubyte),
                ("sThumbLX", ctypes.c_short), ("sThumbLY", ctypes.c_short),
                ("sThumbRX", ctypes.c_short), ("sThumbRY", ctypes.c_short)]


class XINPUT_STATE(ctypes.Structure):
    _fields_ = [("dwPacketNumber", wintypes.DWORD), ("Gamepad", XINPUT_GAMEPAD)]


xi = None
for nom in ("XInput1_4.dll", "xinput1_3.dll", "xinput9_1_0.dll"):
    try:
        xi = ctypes.WinDLL(nom)
        break
    except OSError:
        continue


def manettes():
    out = []
    if xi is None:
        return out
    for i in range(4):
        st = XINPUT_STATE()
        if xi.XInputGetState(i, ctypes.byref(st)) == 0:
            out.append(i)
    return out


avant = manettes()
print("  Manettes XInput avant  :", avant or "aucune")
if avant:
    print()
    print("  /!\\ Une manette virtuelle existe DEJA.")
    print("      C'est un script skate. reste ouvert. Ferme-le (F12),")
    print("      sinon deux manettes se disputent le jeu.")

try:
    import vgamepad as vg
except Exception as e:
    print()
    print("  [NON] vgamepad ne demarre pas :", type(e).__name__, e)
    print("        VIGEM_ERROR_BUS_NOT_FOUND = le pilote ViGEmBus n'est pas actif.")
    print("        -> redemarre le PC.")
    sys.exit(1)

try:
    pad = vg.VX360Gamepad()
    pad.update()
except Exception as e:
    print()
    print("  [NON] impossible de creer la manette :", type(e).__name__, e)
    print("        -> redemarre le PC.")
    sys.exit(1)

time.sleep(2.0)
trouvees = manettes()
print("  Manettes XInput apres  :", trouvees or "aucune")

if not trouvees:
    print()
    print("  [NON] la manette est creee mais Windows ne la voit pas en XInput.")
    print("        -> redemarre le PC.")
    sys.exit(1)

# On teste LA MANETTE QU'ON VIENT DE CREER, pas la premiere de la liste :
# s'il en existait deja une, le test portait sur la mauvaise et echouait
# pour rien.
nouvelles = [i for i in trouvees if i not in avant]
cible = nouvelles[0] if nouvelles else trouvees[0]
print("  Manette testee         : emplacement", cible)

pad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
pad.update()
time.sleep(0.4)
st = XINPUT_STATE()
xi.XInputGetState(cible, ctypes.byref(st))
a_lu = bool(st.Gamepad.wButtons & 0x1000)
pad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
pad.update()

print("  Appui sur A relu par Windows :", "OUI" if a_lu else "non")

del pad
time.sleep(1.5)
print("  Apres debranchement    :", manettes() or "aucune")

if not a_lu:
    print()
    print("  [NON] la manette existe mais ses boutons ne passent pas.")
    sys.exit(1)

print()
print("  [OUI] Manette Xbox virtuelle pleinement fonctionnelle.")
print("        C'est exactement ce que skate. attend.")
sys.exit(0)
