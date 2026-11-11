"""skate. : clavier et souris -> manette Xbox virtuelle.

VERSION 3. Deux changements de fond par rapport aux precedentes :

1. LA SOURIS EST LUE EN RAW INPUT
   On recupere le mouvement brut directement depuis le pilote, sans jamais
   deplacer le curseur. Les versions d'avant le recentraient 125 fois par
   seconde : chacun de ces recentrages etait un faux mouvement que le jeu
   recevait, d'ou le curseur qui clignotait. Plus de recentrage, plus de
   clignotement.
   Le curseur est simplement fige par ClipCursor dans un rectangle d'un pixel,
   ce qui ne produit aucun evenement.

2. LE MAPPAGE EST CELUI DE skate.
   Les grabs sont sur les GACHETTES, pas sur les bumpers. C'est ce qui
   donnait l'impression que les commandes repondaient de travers.
   (releve du projet jasperdevs/skate-kbm, MIT)

F11 active / met en pause. F12 quitte. Les deux marchent depuis le jeu.
"""
import ctypes
import math
import os
import sys
import threading
import time
from ctypes import wintypes

try:
    import vgamepad as vg
except Exception as e:
    print()
    print("  La manette virtuelle n'est pas disponible :", e)
    input("  Entree pour fermer ")
    sys.exit(1)

u32 = ctypes.windll.user32
k32 = ctypes.windll.kernel32

# ------------------------------------------------------------ Raw Input
WM_INPUT = 0x00FF
RIDEV_INPUTSINK = 0x00000100
RID_INPUT = 0x10000003
RIM_TYPEMOUSE = 0
HWND_MESSAGE = -3


class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [("usUsagePage", wintypes.USHORT), ("usUsage", wintypes.USHORT),
                ("dwFlags", wintypes.DWORD), ("hwndTarget", wintypes.HWND)]


class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [("dwType", wintypes.DWORD), ("dwSize", wintypes.DWORD),
                ("hDevice", wintypes.HANDLE), ("wParam", wintypes.WPARAM)]


class RAWMOUSE(ctypes.Structure):
    _fields_ = [("usFlags", wintypes.USHORT), ("usButtonFlags", wintypes.USHORT),
                ("usButtonData", wintypes.USHORT), ("ulRawButtons", wintypes.ULONG),
                ("lLastX", wintypes.LONG), ("lLastY", wintypes.LONG),
                ("ulExtraInformation", wintypes.ULONG)]


class RAWINPUT(ctypes.Structure):
    _fields_ = [("header", RAWINPUTHEADER), ("mouse", RAWMOUSE)]


WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT,
                             wintypes.WPARAM, wintypes.LPARAM)


class WNDCLASS(ctypes.Structure):
    _fields_ = [("style", wintypes.UINT), ("lpfnWndProc", WNDPROC),
                ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int),
                ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HICON),
                ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HBRUSH),
                ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR)]


class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


u32.DefWindowProcW.restype = ctypes.c_ssize_t
u32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
u32.GetRawInputData.argtypes = [wintypes.HANDLE, wintypes.UINT, ctypes.c_void_p,
                                ctypes.POINTER(wintypes.UINT), wintypes.UINT]
u32.ClipCursor.argtypes = [ctypes.POINTER(RECT)]
u32.GetForegroundWindow.restype = wintypes.HWND
# sans ces declarations, HWND_MESSAGE (-3) est tronque sur un Windows 64 bits
# et la fenetre n'est jamais creee
u32.CreateWindowExW.restype = wintypes.HWND
u32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR,
                                wintypes.DWORD, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, wintypes.HWND,
                                wintypes.HMENU, wintypes.HINSTANCE, ctypes.c_void_p]
u32.RegisterClassW.argtypes = [ctypes.c_void_p]
u32.RegisterRawInputDevices.argtypes = [ctypes.c_void_p, wintypes.UINT, wintypes.UINT]
k32.GetModuleHandleW.restype = wintypes.HMODULE
k32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]

brut_dx = 0
brut_dy = 0
raw_ok = [False]


def wndproc(hwnd, msg, wparam, lparam):
    global brut_dx, brut_dy
    if msg == WM_INPUT:
        taille = wintypes.UINT(ctypes.sizeof(RAWINPUT))
        donnees = RAWINPUT()
        lu = u32.GetRawInputData(ctypes.cast(lparam, wintypes.HANDLE), RID_INPUT,
                                 ctypes.byref(donnees), ctypes.byref(taille),
                                 ctypes.sizeof(RAWINPUTHEADER))
        if lu > 0 and donnees.header.dwType == RIM_TYPEMOUSE:
            # usFlags bit 0 = MOUSE_MOVE_ABSOLUTE : on ne garde que le relatif
            if not (donnees.mouse.usFlags & 0x01):
                brut_dx += donnees.mouse.lLastX
                brut_dy += donnees.mouse.lLastY
        return 0
    return u32.DefWindowProcW(hwnd, msg, wparam, lparam)


proc_ref = WNDPROC(wndproc)


def ecouter_la_souris():
    cls = WNDCLASS()
    cls.lpfnWndProc = proc_ref
    cls.hInstance = k32.GetModuleHandleW(None)
    cls.lpszClassName = "SkateKbmRawInput"
    if not u32.RegisterClassW(ctypes.byref(cls)):
        return
    hwnd = u32.CreateWindowExW(0, "SkateKbmRawInput", "skate kbm", 0,
                               0, 0, 0, 0, wintypes.HWND(HWND_MESSAGE),
                               None, cls.hInstance, None)
    if not hwnd:
        return
    rid = RAWINPUTDEVICE(0x01, 0x02, RIDEV_INPUTSINK, hwnd)  # 01:02 = souris
    if not u32.RegisterRawInputDevices(ctypes.byref(rid), 1, ctypes.sizeof(rid)):
        return
    raw_ok[0] = True
    msg = wintypes.MSG()
    while u32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        u32.TranslateMessage(ctypes.byref(msg))
        u32.DispatchMessageW(ctypes.byref(msg))


threading.Thread(target=ecouter_la_souris, daemon=True).start()
time.sleep(0.5)

# ------------------------------------------------------------ touches
VK_LBUTTON, VK_RBUTTON, VK_MBUTTON = 0x01, 0x02, 0x04
VK_SHIFT_L, VK_CTRL_L, VK_ALT_L = 0xA0, 0xA2, 0xA4
VK_SPACE, VK_RETURN, VK_TAB = 0x20, 0x0D, 0x09
VK_END, VK_F11, VK_F12 = 0x23, 0x7A, 0x7B
VK_ALT_D, VK_CTRL_D = 0xA5, 0xA3
VK_GAUCHE, VK_HAUT, VK_DROITE, VK_BAS = 0x25, 0x26, 0x27, 0x28


def vk(c):
    return ord(c.upper())


def touche(v):
    return bool(u32.GetAsyncKeyState(v) & 0x8000)


# ------------------------------------------------------------ reglages souris
#
# Calcul volontairement SIMPLE : c'est celui qui marchait.
# J'ai essaye d'y ajouter une zone morte inversee, un coup de fouet, un
# maintien du stick... chaque "amelioration" a casse quelque chose
# (manuals a repetition, puis plus d'ollie du tout). On n'y retouche pas.
#
SENS = 0.016        # sensibilite : plus grand = souris plus vive
RETOUR = 0.82       # retour au centre : plus petit = revient plus vite
BOUCLE = 0.008      # 125 fois par seconde

# La sensibilite se regle EN JEU avec les touches 1 et 2, et se retient
# d'une partie sur l'autre. Pas besoin de rouvrir ce fichier.
REGLAGES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reglages.txt")
try:
    with open(REGLAGES, encoding="utf-8") as _f:
        for _l in _f:
            if _l.startswith("SENS="):
                SENS = float(_l.split("=", 1)[1])
except Exception:
    pass


def enregistrer_reglages():
    try:
        with open(REGLAGES, "w", encoding="utf-8") as f:
            f.write("SENS=%.4f\n" % SENS)
    except Exception:
        pass

LARG = u32.GetSystemMetrics(0)
HAUT = u32.GetSystemMetrics(1)

pad = vg.VX360Gamepad()
pad.update()

actif = False
rx = ry = 0.0
dernier_f11 = 0.0
dernier_reglage = 0.0
B = vg.XUSB_BUTTON

# ------------------------------------------------------------ le mappage
#
# Regles suivies :
#  - clavier 60 % : AUCUNE touche de la rangee F, aucune fleche, aucun pave
#    numerique. Tout ce qui est ici existe physiquement sur le clavier.
#  - la main droite est sur la souris : TOUT est atteignable de la main
#    gauche posee sur W A S D, sauf les clics.
#  - aucune touche ne sert deux fois (verifie au demarrage).
#  - les grabs sont sur les gachettes, comme sur une vraie manette skate.
#
#  rangee du haut    Q  .  E  R  T          <- bumper G, X, Y, camera haut
#  rangee du milieu  .  A  S  D  F  G       <- deplacement, bumper D, camera bas
#  rangee du bas     Z  X  C  V             <- camera gauche/droite, B, stick D
#  pouces            Espace, Alt            <- A, clic stick G

MAP = [
    # --- les deux POUSSES. En preset Classic le stick gauche ne sert qu'a
    #     diriger : pousser se fait avec DEUX boutons de face, un par pied.
    #     C'est la chose qui manquait.
    (VK_SPACE, B.XUSB_GAMEPAD_A,              "Espace", "A  - POUSSER (pied 1)"),
    (vk('E'),  B.XUSB_GAMEPAD_X,              "E",      "X  - POUSSER (pied 2)"),

    (vk('C'),  B.XUSB_GAMEPAD_B,              "C",      "B  - FREINER / sortir d'un grind"),
    (vk('R'),  B.XUSB_GAMEPAD_Y,              "R",      "Y  - monter / descendre de la planche"),

    (vk('Q'),  B.XUSB_GAMEPAD_LEFT_SHOULDER,  "Q",      "LB - bumper gauche"),
    (vk('F'),  B.XUSB_GAMEPAD_RIGHT_SHOULDER, "F",      "RB - bumper droit (handplant)"),

    # --- L3 et R3, les clics de stick. L3 est le sprint a pied ; Maj est la
    #     place naturelle pour courir sur un clavier.
    (VK_SHIFT_L, B.XUSB_GAMEPAD_LEFT_THUMB,   "Maj G",  "L3 - clic stick gauche (SPRINT a pied)"),
    (vk('V'),  B.XUSB_GAMEPAD_RIGHT_THUMB,    "V",      "R3 - clic stick droit"),

    # --- camera et croix directionnelle, sous l'index gauche
    (vk('T'),  B.XUSB_GAMEPAD_DPAD_UP,        "T",      "croix HAUT (camera)"),
    (vk('G'),  B.XUSB_GAMEPAD_DPAD_DOWN,      "G",      "croix BAS (camera)"),
    (vk('Z'),  B.XUSB_GAMEPAD_DPAD_LEFT,      "Z",      "croix GAUCHE"),
    (vk('X'),  B.XUSB_GAMEPAD_DPAD_RIGHT,     "X",      "croix DROITE"),

    (VK_RETURN, B.XUSB_GAMEPAD_START,         "Entree", "START - menu pause"),
    (VK_TAB,   B.XUSB_GAMEPAD_BACK,           "Tab",    "BACK - carte"),
    (vk('B'),  B.XUSB_GAMEPAD_GUIDE,          "B",      "bouton Xbox (Guide)"),
]

# ---- controle : aucune touche ne doit servir deux fois ----
_utilisees = {}
_conflits = []
for _v, _b, _nom, _role in MAP:
    if _v in _utilisees:
        _conflits.append("%s sert a la fois pour %s et %s" % (_nom, _utilisees[_v], _role))
    _utilisees[_v] = _role
for _v, _nom in ((vk('W'), 'W'), (vk('A'), 'A'), (vk('S'), 'S'), (vk('D'), 'D')):
    if _v in _utilisees:
        _conflits.append("%s sert au deplacement ET a %s" % (_nom, _utilisees[_v]))
for _v, _nom in ((VK_F11, 'F11'), (VK_F12, 'F12'), (VK_ALT_D, 'Alt droit'),
                 (VK_CTRL_D, 'Ctrl droit'), (VK_END, 'Fin')):
    if _v in _utilisees:
        _conflits.append("%s sert au pilotage du script ET a %s" % (_nom, _utilisees[_v]))


# ------------------------------------------------------------ l'ecran d'accueil
print()
print("  ==========================================================")
print("    skate. - clavier et souris")
print("  ==========================================================")
print()
print("    lecture souris en Raw Input :", "OUI" if raw_ok[0] else "ECHEC")
if not raw_ok[0]:
    print("    -> le curseur risque de clignoter comme avant")
print()
print("    Clavier 60 % QWERTY, preset Classic. Tout est sous la main gauche")
print("    posee sur WASD ; la main droite ne quitte jamais la souris.")
print("    Aucune touche de la rangee F, aucune fleche : rien a chercher au Fn.")
print()
print("    W A S D .... diriger")
print("    Souris ..... TRICKS (Flick-It)")
print("    Clic G ..... GRAB (gachette droite)")
print("    Clic D ..... GRAB (gachette gauche)")
print("    Ctrl G ..... le meme grab gauche, sans lacher la souris")
for _v, _b, _nom, _role in MAP:
    print("    %-10s %s" % (_nom + " ...." if len(_nom) < 7 else _nom + " ..", _role))
print()
print()
print("    1 / 2 ................ souris moins vive / plus vive, EN JEU")
print("                           (sensibilite actuelle : %.3f, retenue)" % SENS)
print("    F11 ou Alt droit ..... activer / mettre en pause")
print("    F12 ou Ctrl droit .... quitter")
print()
if _conflits:
    print("    /!\\ TOUCHES EN DOUBLE :")
    for _c in _conflits:
        print("        " + _c)
else:
    print("    Controle : %d touches mappees, aucune ne sert deux fois." % len(MAP))
print()
print("  Lance le jeu, mets-toi en jeu, puis F11.")
print()
print("  >>> EN PAUSE <<<")


def figer_le_curseur(oui):
    """ClipCursor confine le curseur sans le deplacer : aucun evenement
    de mouvement n'est produit, donc rien ne fait clignoter le jeu."""
    if oui:
        p = POINT()
        u32.GetCursorPos(ctypes.byref(p))
        r = RECT(p.x, p.y, p.x + 1, p.y + 1)
        u32.ClipCursor(ctypes.byref(r))
    else:
        u32.ClipCursor(None)


try:
    while True:
        t = time.time()

        if touche(VK_F12) or touche(VK_END) or touche(VK_CTRL_D):
            break

        # --- reglage de la sensibilite en direct, sans quitter le jeu ---
        if actif and t - dernier_reglage > 0.18:
            if touche(vk('1')) and SENS > 0.004:
                SENS = round(SENS - 0.002, 4)
                dernier_reglage = t
                enregistrer_reglages()
                print("  sensibilite souris : %.3f  (moins vive)" % SENS)
            elif touche(vk('2')) and SENS < 0.060:
                SENS = round(SENS + 0.002, 4)
                dernier_reglage = t
                enregistrer_reglages()
                print("  sensibilite souris : %.3f  (plus vive)" % SENS)

        if (touche(VK_F11) or touche(VK_ALT_D)) and t - dernier_f11 > 0.5:
            dernier_f11 = t
            actif = not actif
            rx = ry = 0.0
            brut_dx = brut_dy = 0
            if actif:
                figer_le_curseur(True)
                print("  >>> ACTIF - retourne dans le jeu <<<")
            else:
                figer_le_curseur(False)
                pad.reset()
                pad.update()
                print("  >>> EN PAUSE - la souris te revient <<<")

        if not actif:
            time.sleep(0.05)
            continue

        # --- stick gauche ---
        gx = gy = 0.0
        if touche(vk('A')):
            gx -= 1.0
        if touche(vk('D')):
            gx += 1.0
        if touche(vk('W')):
            gy += 1.0
        if touche(vk('S')):
            gy -= 1.0
        n = math.hypot(gx, gy)
        if n > 1.0:
            gx, gy = gx / n, gy / n

        # --- stick droit : mouvement brut de la souris ---
        dx, dy = brut_dx, brut_dy
        brut_dx = brut_dy = 0

        rx += dx * SENS
        ry -= dy * SENS
        rx *= RETOUR
        ry *= RETOUR
        rx = max(-1.0, min(1.0, rx))
        ry = max(-1.0, min(1.0, ry))
        if abs(rx) < 0.01:
            rx = 0.0
        if abs(ry) < 0.01:
            ry = 0.0

        pad.left_joystick_float(x_value_float=gx, y_value_float=gy)
        pad.right_joystick_float(x_value_float=rx, y_value_float=ry)
        # LES GRABS sont sur les gachettes (source : EA, preset Classic).
        # clic gauche -> gachette droite, clic droit -> gachette gauche.
        # Ctrl gauche fait la gachette gauche aussi, pour grabber sans la souris.
        pad.right_trigger_float(value_float=1.0 if touche(VK_LBUTTON) else 0.0)
        pad.left_trigger_float(
            value_float=1.0 if (touche(VK_RBUTTON) or touche(VK_CTRL_L)) else 0.0)

        for v, bouton, _n, _r in MAP:
            if touche(v):
                pad.press_button(button=bouton)
            else:
                pad.release_button(button=bouton)

        pad.update()
        time.sleep(BOUCLE)

except KeyboardInterrupt:
    pass

figer_le_curseur(False)
pad.reset()
pad.update()
del pad
print()
print("  Arrete, souris rendue.")
time.sleep(2)
